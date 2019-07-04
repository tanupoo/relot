#!/usr/bin/env python

import asyncio
import websockets
from aiohttp import web
import argparse
import logging

import if_csv
import json
import os

#logger = logging.getLogger('websockets.server')
#logger.setLevel(logging.ERROR)
#logger.addHandler(logging.StreamHandler())
logging.basicConfig()

async def send_data(websocket, feeder):
    msg = feeder.next()
    if opt.debug:
        print("DEUBG: ", msg)
    if not len(msg):
        print("ERROR: no data found in the feeder.")
        return
    await websocket.send(msg)

DATA = [
        "sample/x01.csv",
        "sample/x02.csv",
        "sample/x03.csv",
        "sample/x04.csv",
        "sample/x05.csv",
        "sample/x06.csv",
        "sample/x07.csv",
        ]

async def handler(websocket, path):
    print("path =", path)
    feeder = if_csv.feeder(DATA, debug=opt.debug)
    feeding = False
    interval = 2
    while True:
        if len(websocket.messages) > 0:
            message = await websocket.recv()
        else:
            message = None
        if message:
            data = json.loads(message)
            print("DEBUG: data", data)
            cmd = data["cmd"]
            if cmd == "close":
                print("INFO: %s: closed by client.", websocket)
                websocket.close()
                return
            elif cmd == "start":
                interval = float(data["interval"])
                feeding = True
            elif cmd == "stop":
                feeding = False
            else:
                print("ERROR: invalid command {}".format(cmd))
                return
        #
        if feeding is True:
            await send_data(websocket, feeder)
        await asyncio.sleep(interval)

async def get_doc(request):
    path = ".{}".format(request.path)
    logger.debug("DEBUG: serving {}".format(path))
    if os.path.exists(path):
        return web.FileResponse(path)
    else:
        raise web.HTTPNotFound()

def set_logger(prog_name="", log_file=None, logging_stdout=False,
               debug_mode=False):
    def get_logging_handler(channel, debug_mode):
        channel.setFormatter(logging.Formatter(fmt=LOG_FMT,
                                               datefmt=LOG_DATE_FMT))
        if debug_mode:
            channel.setLevel(logging.DEBUG)
        else:
            channel.setLevel(logging.INFO)
        return channel
    #
    # set logger.
    #   log_file: a file name for logging.
    logging.basicConfig()
    logger = logging.getLogger(prog_name)
    if logging_stdout is True:
        logger.addHandler(get_logging_handler(logging.StreamHandler(),
                                              debug_mode))
    if log_file is not None:
        logger.addHandler(get_logging_handler(logging.FileHandler(log_file),
                                              debug_mode))
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger

"""
main code
"""
ap = argparse.ArgumentParser(
        description="relots server.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument("-p", action="store", dest="server_port", default="65482",
                help="specify a port number to be listened.")
ap.add_argument("-w", action="store", dest="ws_port", default="65483",
                help="specify a port number to be listened.")
ap.add_argument("-s", action="store", dest="server_addr", default="0.0.0.0",
                help="specify an IP address to be listened.")
ap.add_argument("-l", action="store", dest="log_file",
                help="specify a file name for logging.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

logger = set_logger(prog_name="Data-Server", log_file=opt.log_file,
                    debug_mode=opt.debug)
# enable the websocket server.
start_server = websockets.serve(handler, opt.server_addr, opt.ws_port)
asyncio.get_event_loop().run_until_complete(start_server)
# enable the http server.
app = web.Application()
app.router.add_route("GET", "/html/{tail:.*}", get_doc)
print("Starting the server, listening on {}://{}:{}/".
      format("http", opt.server_addr, opt.server_port))
web.run_app(app, host=opt.server_addr, port=opt.server_port, print=None)
#asyncio.get_event_loop().run_forever()

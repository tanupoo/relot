#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import argparse
from tcp_server import tcp_server
import SocketServer
from if_db import *
import threading
import select
import json
import datetime

class handler(SocketServer.BaseRequestHandler):

    def _send_data(self):
        msg = self.feeder.get_latest()
        if self.server.debug_level:
            print("DEUBG: ", msg)
        if len(msg):
            self.request.send(msg)
            if self.server.debug_level:
                print("DEBUG: sent: msg=%s" % msg)
        else:
            print("ERROR: no data found in the feeder.")

    '''
    main
    '''
    def handle(self):
        peer = "%s:%s" % (threading.currentThread().getName(),
                          repr(self.client_address))
        timeout = 1
        f_stop = True
        self.feeder = feeder(debug_level=self.server.debug_level)
        while True:
            (rfd, wfd, efd) = select.select([self.request], [], [], timeout)
            if len(rfd) == 0 and f_stop is False:
                '''
                timeouted. will send data to the peer.
                '''
                self._send_data()
            else:
                '''
                received something. will execute the command passed.
                '''
                msg = self.request.recv(512)
                if not msg:
                    print("INFO: %s: session terminated by client" % peer)
                    break
                if self.server.debug_level:
                    print("DEBUG: %s: msg:[%s]" % (peer, repr(msg)))
                j_msg = json.loads(msg)
                cmd = j_msg['cmd'];
                if cmd == "close":
                    print("INFO: %s: closed by client's command" % peer)
                    break
                elif cmd == "start":
                    f_stop = False
                    i = j_msg.get('interval')
                    if not i:
                        print("INFO: %s: interval is not specified" % peer)
                        break
                    try:
                        i = float(i)
                    except Exception as e:
                        print("ERROR: %s: invalid message" % peer)
                        break
                    timeout = i
                    # start to send data immediately.
                    self._send_data()
                elif cmd == "stop":
                    f_stop = True
                else:
                    print("ERROR: %s: invalid command" % repr(cmd))
                    break

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-p", action="store", dest="server_port", default="49001",
        help="specify a port number to be listened. default is 49001")
    p.add_argument('-s', action='store', dest='server_addr', default='',
        help='specify an IP address to be listened.')
    p.add_argument('-d', action='append_const', dest='_f_debug',
                   default=[], const=1, help="increase debug mode.")
    p.add_argument('--debug', action='store', dest='_debug_level', default=0,
        help="specify a debug level.")

    args = p.parse_args()
    args.debug_level = len(args._f_debug) + int(args._debug_level)

    return args

'''
test code
'''
if __name__ == "__main__":
    opt = parse_args()
    print("addr = %s" % addr)
    print("port = %s" % port)
    print("debug: %d" % self.debug_level)
    this = tcp_server(handler, addr, port, self.debug_level)
    this.go()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import socket
import threading
from SocketServer import TCPServer, ThreadingMixIn

class ThreadedTCPServer(ThreadingMixIn, TCPServer):

    def __init__(self, server_address, handler, debug_level=0):
        self.debug_level = debug_level
        TCPServer.__init__(self, server_address, handler)

class tcp_server():

    def __init__(self, handler, addr, port, debug_level=0):
        self.handler = handler
        self.addr = addr
        self.port = port
        self.debug_level = debug_level
        self.server = ThreadedTCPServer((addr, int(port)), handler, debug_level)

    def go(self):
        try:
            self.server.serve_forever()
            print("listening on %s[%d]" % self.server.server_address)
        except KeyboardInterrupt as e:
            print("Caught KeyboardInterrupt")
            self.server.shutdown()
            exit(0)
        except Exception as e:
            print("ERROR: ", e)
            self.server.shutdown()
            exit(0)

if __name__ == "__main__":
    debug_level = 0
    if len(sys.argv) == 1:
        print("Usage: %s [-d] (port) [addr]" % (sys.argv[0]))
        exit(1)
    if sys.argv[1] == "-d":
        debug_level = 1
        sys.argv.pop(1)
    if len(sys.argv) == 2:
        port = sys.argv[1]
        addr = "0.0.0.0"
    elif len(sys.argv) == 3:
        port = sys.argv[1]
        addr = sys.argv[2]
    print("addr = %s" % addr)
    print("port = %s" % port)
    print("debug: %d" % debug_level)
    this = tcp_server(handler, addr, port, debug_level)
    this.go()


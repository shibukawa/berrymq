# -*- coding: utf-8 -*-

import json
import select 
import threading
import SocketServer
from server_common import (SimpleJSONRPCDispatcher,
                           SimpleJSONRPCRequestHandler)


class SimpleJSONRPCServer(SocketServer.TCPServer,
                          SimpleJSONRPCDispatcher):
    """Simple JSON-RPC server.

    Simple JSON-RPC server that allows functions and a single instance
    to be installed to handle requests. The default implementation
    attempts to dispatch JSON-RPC calls to the functions or instance
    installed in the server. Override the _dispatch method inhereted
    from SimpleJSONRPCDispatcher to change this behavior.
    """

    allow_reuse_address = True

    def __init__(self, addr, requestHandler=SimpleJSONRPCRequestHandler,
                 logRequests=True):
        self.logRequests = logRequests

        SimpleJSONRPCDispatcher.__init__(self, allow_none=True, encoding=None)
        SocketServer.TCPServer.__init__(self, addr, requestHandler)

        self.__thread = None  

    def serve_forever(self, in_thread=False, poll_interval=0.5):
        def serve_thread(server, poll_interval):
            server.serve_forever(poll_interval=poll_interval)
        if in_thread:
            args = [self, poll_interval]
            self.__thread = threading.Thread(target=serve_thread, args=args)
            self.__thread.setDaemon(True)
            self.__thread.start()
        else:
            SocketServer.TCPServer.serve_forever(self, poll_interval)

    def shutdown(self, immediately = True):
        if not immediately:
            self._BaseServer__serving = False
            return
        SocketServer.TCPServer.shutdown(self)
        if self.__thread:
            self.__thread.join()
            self.__thread = None

# -*- coding: utf-8 -*-

import json
import select 
import threading
import SocketServer
from server_common import (SimpleJSONRPCDispatcher,
                           SimpleJSONRPCRequestHandler)
try:
    import fcntl
except ImportError:
    fcntl = None


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

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)

        self.__serving = False  
        self.__thread = None  
        self.__is_shut_down = threading.Event()

    def serve_forever(self, in_thread=False):
        def serve_thread(server):
            server.serve_forever()
        if in_thread:
            self.__thread = threading.Thread(target=serve_thread, args=[self])
            self.__thread.start()
        else:
            self.__serving = True
            self.__is_shut_down.clear()
            while self.__serving:
                self.handle_request()
            self.__is_shut_down.set()



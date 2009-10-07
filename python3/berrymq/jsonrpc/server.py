# -*- coding: utf-8 -*-

# Almost all code comes from http://code.activestate.com/recipes/552751/

import sys
import json
import select 
import threading
import traceback
import socketserver
import xmlrpc.server
try:
    import fcntl
except ImportError:
    fcntl = None


class SimpleJSONRPCDispatcher(xmlrpc.server.SimpleXMLRPCDispatcher):
    def _marshaled_dispatch(self, request_raw, dispatch_method = None):
        id = None
        try:
            request = json.loads(request_raw.decode("utf-8"))
            method = request['method']
            params = request['params']
            id     = request['id']

            if dispatch_method is not None:
                result = dispatch_method(method, params)
            else:
                result = self._dispatch(method, params)
            response = dict(id=id, result=result, error=None)
        except:
            extpe, exv, extrc = sys.exc_info()
            err = dict(type=str(extpe),
                       message=str(exv),
                       traceback=''.join(traceback.format_tb(extrc)))
            response = dict(id=id, result=None, error=err)
        try:
            response_raw = json.dumps(response, ensure_ascii=False)
            if sys.version_info[1] != 0:
                response_raw = response_raw.encode("utf-8")
            return response_raw
        except:
            extpe, exv, extrc = sys.exc_info()
            err = dict(type=str(extpe),
                       message=str(exv),
                       traceback=''.join(traceback.format_tb(extrc)))
            response = dict(id=id, result=None, error=err)
            
            response_raw = json.dumps(response, ensure_ascii=False)
            if sys.version_info[1] != 0:
                response_raw = response_raw.encode("utf-8")
            return response_raw


class SimpleJSONRPCRequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
    # Class attribute listing the accessible path components;
    # paths not on this list will result in a 404 error.
    rpc_paths = ('/', '/JSON')


class SimpleJSONRPCServer(socketserver.TCPServer,
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
        socketserver.TCPServer.__init__(self, addr, requestHandler)
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
            socketserver.TCPServer.serve_forever(self, poll_interval)

    def shutdown(self, immediately = True):
        if not immediately:
            self._BaseServer__serving = False
            return
        socketserver.TCPServer.shutdown(self)
        if self.__thread:
            self.__thread.join()
            self.__thread = None

# -*- coding: utf-8 -*-

# Almost all code comes from http://code.activestate.com/recipes/552751/

import sys
import json
import select 
import threading
import traceback
import xmlrpc.client
try:
    import fcntl
except ImportError:
    fcntl = None


class ResponseError(xmlrpc.client.ResponseError):
    pass


class Fault(xmlrpc.client.ResponseError):
    pass


def _get_response(file, sock):
    data = b""
    while 1:
        if sock:
            response = sock.recv(1024)
        else:
            response = file.read(1024)
        if not response:
            break
        data += response

    file.close()

    return data.decode("utf_8")


if sys.version_info[1] == 0:
    class Transport(xmlrpc.client.Transport):
        def _parse_response(self, file, sock):
            return _get_response(file, None)


    class SafeTransport(xmlrpc.client.SafeTransport):
        def _parse_response(self, file, sock):
            return _get_response(file, None)
else:
    class Transport(xmlrpc.client.Transport):
        def parse_response(self, file):
            return _get_response(file, None)


    class SafeTransport(xmlrpc.client.SafeTransport):
        def parse_response(self, file):
            return _get_response(file, None)


class ServerProxy:
    def __init__(self, uri, id=None, transport=None, use_datetime=0):
        # establish a "logical" server connection

        # get the url
        import urllib.parse
        type, uri = urllib.parse.splittype(uri)
        if type not in ("http", "https"):
            raise IOError("unsupported JSON-RPC protocol")
        self.__host, self.__handler = urllib.parse.splithost(uri)
        if not self.__handler:
            self.__handler = "/JSON"

        if transport is None:
            if type == "https":
                transport = SafeTransport(use_datetime=use_datetime)
            else:
                transport = Transport(use_datetime=use_datetime)

        self.__transport = transport
        self.__id        = id

    def __request(self, methodname, params):
        # call a method on the remote server

        request_raw = json.dumps(dict(id=self.__id, method=methodname,
                                      params=params), 
                                      ensure_ascii=False).encode("utf-8")
        response_raw = self.__transport.request(
            self.__host,
            self.__handler,
            request_raw,
            verbose=False)
        response = json.loads(response_raw)

        if response["id"] != self.__id:
            raise ResponseError("Invalid request id (is: %s, expected: %s)" \
                                % (response["id"], self.__id))
        if response["error"] is not None:
            raise Fault("JSON Error", response["error"])
        return response["result"]

    def __repr__(self):
        return "<ServerProxy for %s%s>" % (self.__host, self.__handler)

    __str__ = __repr__

    def __getattr__(self, name):
        return xmlrpc.client._Method(self.__request, name)

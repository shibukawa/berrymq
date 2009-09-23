# -*- coding: utf-8 -*-

# Almost all code comes from http://code.activestate.com/recipes/552751/

import sys
import select 
import threading
import traceback
import xmlrpclib
try:
    import fcntl
except ImportError:
    fcntl = None
try:
    import json
except ImportError:
    import simplejson as json


class ResponseError(xmlrpclib.ResponseError):
    pass


class Fault(xmlrpclib.ResponseError):
    pass


def _get_response(file, sock):
    data = ""
    while 1:
        if sock:
            response = sock.recv(1024)
        else:
            response = file.read(1024)
        if not response:
            break
        data += response
    file.close()
    return data


class Transport(xmlrpclib.Transport):
    def _parse_response(self, file, sock):
        return _get_response(file, sock)


class SafeTransport(xmlrpclib.SafeTransport):
    def _parse_response(self, file, sock):
        return _get_response(file, sock)


class ServerProxy:
    def __init__(self, uri, id=None, transport=None, use_datetime=0):
        # establish a "logical" server connection

        # get the url
        import urllib
        type, uri = urllib.splittype(uri)
        if type not in ("http", "https"):
            raise IOError, "unsupported JSON-RPC protocol"
        self.__host, self.__handler = urllib.splithost(uri)
        if not self.__handler:
            self.__handler = "/JSON"

        if transport is None:
            if sys.version_info[:2] == (2, 4):
                if type == "https":
                    transport = SafeTransport()
                else:
                    transport = Transport()
            else:
                if type == "https":
                    transport = SafeTransport(use_datetime=use_datetime)
                else:
                    transport = Transport(use_datetime=use_datetime)

        self.__transport = transport
        self.__id        = id

    def __request(self, methodname, params):
        # call a method on the remote server

        request = json.dumps(dict(id=self.__id, method=methodname,
                                  params=params))
        data = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=False
            )

        response = json.loads(data)

        if response["id"] != self.__id:
            raise ResponseError("Invalid request id (is: %s, expected: %s)" \
                                % (response["id"], self.__id))
        if response["error"] is not None:
            raise Fault("JSON Error@%s" % self.__host, response["error"])
        return response["result"]

    def __repr__(self):
        return "<ServerProxy for %s%s>" % (self.__host, self.__handler)

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        return xmlrpclib._Method(self.__request, name)

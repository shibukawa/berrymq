# -*- coding: utf-8 -*-

import os
import sys
import unittest

rootdir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, rootdir)
import berrymq
import berrymq.jsonrpc.server
import berrymq.jsonrpc.client

"""
Test Sequence
=============

Use 2 nodes,  Primary(P) and Secondary(S).

1. Launch P@localhost:12345
2. Launch S@localhost:12346
3. P <- S
   send "start_test"
4. P -> S
   call connect() and wait 1[s]
5. P -> S
   twitter("sample1:test1")
   twitter("sample2:*")
   twitter("*:test3")
   twitter("sample4:test4", arg)
   twitter("sample5:test5", kwargs)
6. P -> S
   return
7. P <- S
   twitter("sample1:test1")
   twitter("sample2:*")
   twitter("*:test3")
   twitter("sample4:test4", arg)
   twitter("sample5:test5", kwargs)
8. P <- S
   send "verify"
9. P show result
10. S show result
"""

jsonserver = None

def start_test():
    print "start_test"
    print "    send from server"
    return True

def verify():
    print "verify"
    return True

def quit():
    print "quit"
    jsonserver.shutdown(immediately=False)

SERVER_URL = ("localhost", 12345)

def primary_node():
    global jsonserver
    jsonserver = berrymq.jsonrpc.server.SimpleJSONRPCServer(SERVER_URL)
    jsonserver.register_function(start_test)
    jsonserver.register_function(verify)
    jsonserver.register_function(quit)
    print "start primary server. waiting secondary node."
    jsonserver.serve_forever()


def secondary_node():
    jsonclient = berrymq.jsonrpc.client.ServerProxy("http://%s:%d" % SERVER_URL)
    jsonclient.start_test()
    print "send from client"
    jsonclient.verify()
    jsonclient.quit()


def usage():
    print """test inter process communication

    Run this scprit twice at same machine. First one is primary and second 
    is seconary.

usage:
    python test_interprocess.py -primary   : run this first
    python test_interprocess.py -secondary : run after primary process
"""

if __name__ == "__main__":
    if "-primary" in sys.argv:
        primary_node()
    elif "-secondary" in sys.argv:
        secondary_node()
    else:
        usage()


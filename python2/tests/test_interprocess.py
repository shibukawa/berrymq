# -*- coding: utf-8 -*-

import os
import sys
import unittest

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, rootdir)
import berrymq
import berrymq.connect
import berrymq.jsonrpc.server
import berrymq.jsonrpc.client

"""
Test Sequence
=============

Use 2 nodes,  Primary(P) and Secondary(S).

1. Launch P
   Control JSONRPC Server:localhost:12345
2. Launch S
   Open JSON-RPC Server 
3. P <- S
   send "start_slyle02_test"
4. P -> S
   call connect_oneway()
5. P -> S
   call send_message("style02:test02", [1,2,3], {"a":1, "b":2})
6. P -> S
   return
7. P <- S
   twitter("style01:test01")
8. P <- S
   verify @ S
   send "exit_style01_test"
   verify @ P
9. P <- S
   send "start_stlye02_test"
10. P -> S
   close_connection() and wait 1[s]
11. P -> S
   connect_oneway()
12. 
"""

token = None

def start_style01_test():
    print "start_style01_test"
    return True

def exit_style01_test():
    print "exit_style01_test"
    return True

def start_style02_test():
    print "start_style02_test"
    global token
    client = berrymq.jsonrpc.client.ServerProxy(_url(SECONDARY_NODE_URL))
    token = client.connect_oneway(1000)
    print "  token = %s" % token
    client.send_message(token, "style02:test02", [1,2,3], {"a":1, "b":2})
    return True

def exit_style02_test():
    print "exit_style02_test"
    client = berrymq.jsonrpc.client.ServerProxy(_url(SECONDARY_NODE_URL))
    print "  " + client.close_connection(token)
    return True

def start_style03_test():
    print "start_style03_test"
    return True

def exit_style03_test():
    print "exit_style03_test"
    return True

def quit():
    print "quit"
    jsonserver.shutdown(immediately=False)


CONTROL_SERVER_URL = ("localhost", 12345)
PRIMARY_NODE_URL = ("localhost", 12346)
SECONDARY_NODE_URL = ("localhost", 12347)

def _url(URL):
    return "http://%s:%s" % URL


def primary_node():
    global jsonserver
    jsonserver = berrymq.jsonrpc.server.SimpleJSONRPCServer(CONTROL_SERVER_URL)
    jsonserver.register_function(start_style02_test)
    jsonserver.register_function(exit_style02_test)
    jsonserver.register_function(quit)
    print "start primary server. waiting secondary node."
    jsonserver.serve_forever()


def secondary_node():
    expected_at_secondary = [
        ["style02:test02", [1,2,3], {"a":1, "b":2}],
    ]
    test_results = []
    @berrymq.following("*:*")
    def test_receiver(message):
        expected = expected_at_secondary[0]
        if expected[0] == message.id and \
           expected[1] == message.args and \
           expected[2] == message.kwargs:
            result = "ok"
        else:
            result = "ng"
        test_results.append(str(expected), str(message), result)
    
    exported_functions = berrymq.connect.ExportedFunctions()
    secondary_node_server = berrymq.jsonrpc.server.SimpleJSONRPCServer(
        SECONDARY_NODE_URL)
    secondary_node_server.register_instance(exported_functions)
    secondary_node_server.serve_forever(in_thread=True)
    controller = berrymq.jsonrpc.client.ServerProxy(_url(CONTROL_SERVER_URL))
    controller.start_style02_test()
    controller.exit_style02_test()
    controller.quit()
    secondary_node_server.shutdown()

    for expected, actual, result in test_results:
        if result == "ok":
            print "ok: expected = %s" % expected
        else:
            print "ng: expected = %s, actual = %s" % (expected, actual)

def usage():
    print """test JSON-RPC level inter process communication

    Run this scprit twice at same machine. First one is primary and second 
    is seconary.

usage:
    python test_interprocess_low.py -primary   : run this first
    python test_interprocess_low.py -secondary : run after primary process
"""

if __name__ == "__main__":
    if "-primary" in sys.argv:
        primary_node()
    elif "-secondary" in sys.argv:
        secondary_node()
    else:
        usage()


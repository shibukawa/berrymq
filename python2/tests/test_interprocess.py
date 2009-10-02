# -*- coding: utf-8 -*-
"""test program for interprocess communication(JSON-RPC layer)
"""

import os
import sys
import time
import unittest

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, rootdir)
import berrymq
import berrymq.jsonrpc.server
import berrymq.jsonrpc.client
import berrymq.adapter.growl


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

# Const

CONTROL_SERVER_URL = ("localhost", 12345) # primary node
PRIMARY_NODE_URL = ("localhost", 12346)
SECONDARY_NODE_URL = ("localhost", 12347)

# Utilities

def _url(URL):
    return "http://%s:%s" % URL

def check(expected, actual):
    if actual == expected:
        print "  ok: %s" % expected
    else:
        print "  ng: expected=%s, acutal=%s" % (expected, actual)

def quit():
    print "quit"
    jsonserver.shutdown(immediately=False)


# Test Entry Points
# 
# These functions is run at primary node and called from secondary one via RPC.


class Style01Test(object):
    def __init__(self):
        self.received_messages = []

    def message_receiver(self, message):
        self.received_messages.append(message.id)

    def start(self):
        berrymq.regist_method("*", self.message_receiver)
        berrymq.init_connection(PRIMARY_NODE_URL)
        berrymq.interconnect(SECONDARY_NODE_URL)
        berrymq.twitter("style01c:test01")
        time.sleep(1)
        return True

    def exit(self):
        expected = ['style01c:test01', u'style01s:test02']
        check(expected, self.received_messages)
        berrymq.close_connection()
        return True


class Style02Test(object):
    def start(self):
        berrymq.connect_oneway(SECONDARY_NODE_URL)
        berrymq.send_message("style02c:test02", 1, 2, 3, a=1, b=2)
        return True

    def exit(self):
        berrymq.close_connection()
        return True


class Style03Test(object):
    def start(self):
        berrymq.connect_via_queue(SECONDARY_NODE_URL, "style03s:*")
        berrymq.send_message("style03c:test01", 3, 2, 1, a=1, b=2)
        return True

    def check(self):
        check("style03s:test02", berrymq.get().id)
        return True

    def exit(self):
        check("style03s:test03", berrymq.get_nowait().id)
        berrymq.close_connection()
        return True


class TestSuite(object):
    def __init__(self):
        self.style01 = Style01Test()
        self.style02 = Style02Test()
        self.style03 = Style03Test()


# Main Routines

def primary_node():
    global jsonserver
    jsonserver = berrymq.jsonrpc.server.SimpleJSONRPCServer(CONTROL_SERVER_URL)
    jsonserver.register_instance(TestSuite(), allow_dotted_names=True)
    jsonserver.register_function(quit)
    print "start primary server. waiting secondary node."

    @berrymq.following_function("style03s:*")
    def receive_messages(message):
        _primary_node_test_result.append(message)
    
    berrymq.twitter("start primary server:info")
    jsonserver.serve_forever()


def secondary_node():
    expected_at_secondary = [
        ["style02c:test02", [1,2,3], {"a":1, "b":2}],
        ["style03c:test01", [3,2,1], {"a":1, "b":2}],
        ["style03s:test02", (), {}],
        ["style03s:test03", (), {}],
        ["style01c:test01", [], {}],
        ["style01s:test02", (), {}],
    ]
    test_results = []
    @berrymq.following_function("*:*")
    def test_receiver(message):
        expected = expected_at_secondary[0]
        if expected[0] == message.id and \
           expected[1] == message.args and \
           expected[2] == message.kwargs:
            result = "ok"
        else:
            result = "ng"
        del expected_at_secondary[0]
        test_results.append([str(expected), 
                             str([message.id, message.args, message.kwargs]), 
                             result])
    
    berrymq.init_connection(SECONDARY_NODE_URL)

    controller = berrymq.jsonrpc.client.ServerProxy(_url(CONTROL_SERVER_URL))
    controller.style02.start()
    controller.style02.exit()

    controller.style03.start()
    berrymq.twitter("style03s:test02")
    controller.style03.check()
    berrymq.twitter("style03s:test03")
    controller.style03.exit()

    controller.style01.start()
    berrymq.twitter("style01s:test02")
    time.sleep(1)

    controller.style01.exit()
    controller.quit()

    berrymq.close_connection()

    for expected, actual, result in test_results:
        if result == "ok":
            print "ok: expected = %s" % expected
        else:
            print "ng: expected = %s, actual = %s" % (expected, actual)
    if len(test_results) == 0:
        print "ng: no message received"

def usage():
    print """test JSON-RPC level inter process communication

    Run this scprit twice at same machine. First one is primary and second 
    is seconary.

usage:
    python test_interprocess_low.py -primary   [option]
         : run this first
    python test_interprocess_low.py -secondary [option]
         : run after primary process

option:
    -growl : transfer messages to growl(for debug)
"""

if __name__ == "__main__":
    if "-growl" in sys.argv:
        listner = berrymq.adapter.growl.GrowlAdapter("*:*")
    if "-primary" in sys.argv:
        primary_node()
    elif "-secondary" in sys.argv:
        secondary_node()
    else:
        usage()

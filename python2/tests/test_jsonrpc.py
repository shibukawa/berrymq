# -*- coding: utf-8 -*-

import time
import unittest
import berrymq.jsonrpc.server
import berrymq.jsonrpc.client


class TestJSONRPC(unittest.TestCase):
    def setUp(self):
        time.sleep(3)
        url = ("localhost", 8000)
        self.server = berrymq.jsonrpc.server.SimpleJSONRPCServer(url)

    def tearDown(self):
        self.server.shutdown()    

    def test_send_message(self):
        called = []
        def test_func():
            called.append("test_func called")
            return True
        self.server.register_function(test_func)
        self.server.serve_forever(in_thread=True)
        client = berrymq.jsonrpc.client.ServerProxy("http://localhost:8000")
        client.test_func()
        self.assertEquals(["test_func called"], called)

    def test_reply(self):
        def test_func():
            return 123
        self.server.register_function(test_func)
        self.server.serve_forever(in_thread=True)
        client = berrymq.jsonrpc.client.ServerProxy("http://localhost:8000")
        self.assertEquals(123, client.test_func())

    def test_invalid_parameters(self):
        self.server.register_function(lambda x,y:x+y, 'add')
        self.server.serve_forever(in_thread=True)
        client = berrymq.jsonrpc.client.ServerProxy("http://localhost:8000")
        self.assertRaises(berrymq.jsonrpc.client.Fault, client.add, 5, "toto")

    def test_invalid_parameters_anity(self):
        self.server.register_function(lambda x,y:x+y, 'add')
        self.server.serve_forever(in_thread=True)
        client = berrymq.jsonrpc.client.ServerProxy("http://localhost:8000")
        self.assertRaises(berrymq.jsonrpc.client.Fault, client.add, 5, 6, 7)

    def test_invalid_method_name(self):
        self.server.register_function(lambda x,y:x+y, 'add')
        self.server.serve_forever(in_thread=True)
        client = berrymq.jsonrpc.client.ServerProxy("http://localhost:8000")
        self.assertRaises(berrymq.jsonrpc.client.Fault, client.addx, 2, 4)


def test_setup():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestJSONRPC))
    return test_suite

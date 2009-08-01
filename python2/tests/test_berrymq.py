# -*- coding: utf-8 -*-

import unittest
berrymq = None

class IdentifierTest(unittest.TestCase):
    def test_match(self):
        exposer = berrymq.Identifier("id_sample1:entry")
        follower = berrymq.Identifier("id_sample1:entry")
        self.assert_(follower.is_match(exposer))

    def test_match_only_name(self):
        exposer = berrymq.Identifier("id_sample2")
        follower = berrymq.Identifier("id_sample2:entry")
        self.assert_(follower.is_match(exposer))
    
    def test_wildcard_action(self):
        exposer = berrymq.Identifier("id_sample3:test")
        follower = berrymq.Identifier("id_sample3:*")
        self.assert_(follower.is_match(exposer))

    def test_wildcard_name_1(self):
        exposer = berrymq.Identifier("id_sample4:entry")
        follower = berrymq.Identifier("*:entry")
        self.assert_(follower.is_match(exposer))

    def test_wildcard_name_2(self):
        exposer = berrymq.Identifier("*:entry")
        follower = berrymq.Identifier("id_sample4:entry")
        self.assert_(follower.is_match(exposer))

    def test_wildcard_all_1(self):
        exposer = berrymq.Identifier("id_sample5:entry")
        follower = berrymq.Identifier("*:*") 
        self.assert_(follower.is_match(exposer))


    def test_wildcard_all_2(self):
        exposer = berrymq.Identifier("id_sample6:entry")
        follower = berrymq.Identifier("*") 
        self.assert_(follower.is_match(exposer))

    def test_local_namespace(self):
        exposer = berrymq.Identifier("_id_sample7:entry")
        self.assert_(exposer.is_local)

    def test_namespace(self):
        exposer = berrymq.Identifier("id_sample8@layer:entry")
        follower = berrymq.Identifier("*@layer:entry")
        self.assertEqual("layer", exposer.namespace)
        self.assertEqual("layer", follower.namespace)


class TestMessageSendAndReceive(unittest.TestCase):
    def test_received_by_function1(self):
        call_history = []
        @berrymq.auto_twitter("sample1", entry=True)
        def sample_expose1():
            call_history.append("expose")

        @berrymq.following_function("sample1:entry")
        def test_entry(message):
            self.assertEqual("sample1:entry", message.id) 
            call_history.append("entry")

        sample_expose1()
        self.assertEqual(["entry", "expose"], call_history)

    def test_received_by_function2(self):
        call_history = []
        @berrymq.auto_twitter("sample2", exit=True)
        def sample_expose():
            call_history.append("expose")

        @berrymq.following_function("sample2:exit")
        def test_entry(message):
            call_history.append("exit")

        sample_expose()
        self.assertEqual(["expose", "exit"], call_history)

    def test_auto_twitter(self):
        call_history = []
        @berrymq.auto_twitter("sample3")
        def sample_expose():
            call_history.append("expose")

        @berrymq.following_function("sample3:entry")
        def test_entry(message):
            call_history.append("entry")

        @berrymq.following_function("sample3:exit")
        def test_exit(message):
            call_history.append("exit")

        sample_expose()
        self.assertEqual(["entry", "expose", "exit"], call_history)

    def test_original_exposepoint(self):
        call_history = []

        def sample_expose3():
            call_history.append("expose")
            berrymq.twitter("sample4:original")

        @berrymq.following_function("sample4:original")
        def test_original(message):
            call_history.append("original")

        sample_expose3()
        self.assertEqual(["expose", "original"], call_history)

    def test_wildcard_following(self):
        call_history = []

        def sample_twitter3():
            call_history.append("action")
            berrymq.twitter("sample10:action")

        @berrymq.following_function("*:action")
        def test_original_action(message):
            call_history.append("accept")

        sample_twitter3()
        self.assertEqual(["action", "accept"], call_history)

    def test_staticmethod(self):
        call_history = []
        @berrymq.auto_twitter("sample5:entry")
        def sample_expose():
            call_history.append("expose")

        class TestClass(object):
            @staticmethod
            @berrymq.following_function("sample5:entry")
            def test_entry(message):
                call_history.append("entry")

        sample_expose()
        self.assertEqual(["entry", "expose"], call_history)

    def test_classmethod(self):
        call_history = []
        @berrymq.auto_twitter("sample6:entry")
        def sample_expose():
            call_history.append("expose")

        class TestClass(object):
            __metaclass__ = berrymq.Follower
            @classmethod
            @berrymq.following("sample6:entry")
            def test_entry(cls, message):
                call_history.append("entry")

        sample_expose()
        self.assertEqual(["entry", "expose"], call_history)

    def test_instancemethod(self):
        call_history = []
        @berrymq.auto_twitter("sample7:entry")
        def sample_expose():
            call_history.append("expose")

        class TestClass(object):
            __metaclass__ = berrymq.Follower
            @berrymq.following("sample7:entry")
            def test_entry(self, message):
                call_history.append("entry")

        instance = TestClass()
        sample_expose()
        self.assertEqual(["entry", "expose"], call_history)

    def test_guard_condition(self):
        call_history = []
        @berrymq.auto_twitter("sample8")
        def sample_expose(arg):
            call_history.append("expose")

        @berrymq.following_function("sample8:entry", 
            guard_condition=lambda message: message.args[0] == "match")
        def test_entry(message):
            call_history.append("entry")

        @berrymq.following_function("sample8:exit", 
            guard_condition=lambda message: message.args[0] == "match")
        def test_entry(message):
            call_history.append("exit")

        sample_expose("not match")
        self.assertEqual(["expose"], call_history)

    def test_wildcard(self):
        call_history = []
        @berrymq.following_function("sample10:test")
        def sample(message):
            call_history.append("called")
        berrymq.twitter("*:test")
        self.assertEqual(["called"], call_history)

    def _test_composite_condition(self):
        call_history = []
        @berrymq.auto_twitter("sample9_1", entry=True)
        def sample_expose1(arg):
            call_history.append("expose1", entry=True)

        @berrymq.auto_twitter("sample9_2")
        def sample_expose2(arg):
            call_history.append("expose2")

        @berrymq.following_function(berrymq.cond("sample9_1:entry") & \
                                    berrymq.cond("sample9_2:entry"))

        def test_and_condition(message):
            call_history.append("and_condition")

        sample_expose1()
        sample_expose2()
        self.assertEqual(["expose1", "and_condition", "expose2"], call_history)


def test_setup(berrymq_module):
    global berrymq
    berrymq = berrymq_module
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(IdentifierTest))
    test_suite.addTest(unittest.makeSuite(TestMessageSendAndReceive))
    return test_suite

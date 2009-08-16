# -*- coding: utf-8 -*-

import unittest

berrymq = None
import time

class ThreadPoolTest(unittest.TestCase):
    def test_create1(self):
        self.assertRaises(ValueError, 
            berrymq.ThreadPool.make_thread_pool, -1)

    def test_create2(self):
        berrymq.ThreadPool.make_thread_pool(5)
        self.assertEqual(5, len(berrymq.ThreadPool._pool))
        self.assert_(not berrymq.ThreadPool.empty())
        berrymq.ThreadPool.stop_thread_pool()
        self.assertEqual(0, len(berrymq.ThreadPool._pool))
        self.assert_(berrymq.ThreadPool.empty())

    def test_recreate1(self):
        berrymq.ThreadPool.make_thread_pool(3)
        self.assertEqual(3, len(berrymq.ThreadPool._pool))
        berrymq.ThreadPool.make_thread_pool(5)
        self.assertEqual(5, len(berrymq.ThreadPool._pool))
        berrymq.ThreadPool.stop_thread_pool()
        self.assertEqual(0, len(berrymq.ThreadPool._pool))

    def test_recreate2(self):
        berrymq.ThreadPool.make_thread_pool(5)
        self.assertEqual(5, len(berrymq.ThreadPool._pool))
        berrymq.ThreadPool.make_thread_pool(5)
        self.assertEqual(5, len(berrymq.ThreadPool._pool))
        berrymq.ThreadPool.stop_thread_pool()
        self.assertEqual(0, len(berrymq.ThreadPool._pool))

    def test_recreate3(self):
        berrymq.ThreadPool.make_thread_pool(5)
        self.assertEqual(5, len(berrymq.ThreadPool._pool))
        berrymq.ThreadPool.make_thread_pool(3)
        time.sleep(1)
        berrymq.ThreadPool.clear_thread_pool()
        self.assertEqual(3, len(berrymq.ThreadPool._pool))
        berrymq.ThreadPool.stop_thread_pool()
        self.assertEqual(0, len(berrymq.ThreadPool._pool))


class PrallelWorkTest(unittest.TestCase):
    def test_parallel_working(self):
        """parallel test(not parallel version)
        """
        call_history = []
        @berrymq.auto_twitter("sample1:entry")
        def exp():
            call_history.append("exp_1")
            time.sleep(3)
            call_history.append("exp_2")

        @berrymq.following_function("sample1:entry")
        def com1(message):
            time.sleep(1)
            call_history.append("com1_1")
            time.sleep(3)
            call_history.append("com1_2")

        @berrymq.following_function("sample1:entry")
        def com2(message):
            time.sleep(2)
            call_history.append("com2_1")
            time.sleep(3)
            call_history.append("com2_2")
        exp()
        self.assertEqual(["com1_1", "com1_2", "com2_1",
                          "com2_2", "exp_1", "exp_2"],
                          call_history)

    def test_parallel_working2(self):
        """parallel test
        
              0. 1. 2. 3. 4. 5.
        exp : *        *
        com1:    *        *
        com2:       *        *
        """
        berrymq.set_multiplicity(3)
        call_history = []
        @berrymq.auto_twitter("sample2:entry")
        def exp():
            call_history.append("exp_1")
            time.sleep(3)
            call_history.append("exp_2")

        @berrymq.following_function("sample2:entry")
        def com1(message):
            time.sleep(1)
            call_history.append("com1_1")
            time.sleep(3)
            call_history.append("com1_2")
            
        @berrymq.following_function("sample2:entry")
        def com2(message):
            time.sleep(2)
            call_history.append("com2_1")
            time.sleep(3)
            call_history.append("com2_2")

        exp()
        time.sleep(4)
        berrymq.set_multiplicity(0)
        self.assertEqual(["exp_1", "com1_1", "com2_1",
                          "exp_2", "com1_2", "com2_2"],
                         call_history)


def test_setup(berrymq_module):
    global berrymq
    berrymq = berrymq_module
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ThreadPoolTest))
    test_suite.addTest(unittest.makeSuite(PrallelWorkTest))
    return test_suite

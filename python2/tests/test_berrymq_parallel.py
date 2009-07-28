# -*- coding: utf-8 -*-

mqas = None
import time

def test_thread_pool_create1():
    try:
        berrymq.ThreadPool.make_thread_pool(-1)
    except ValueError:
        pass
    else:
        raise RuntimeError("ValueError should be raised")
    print("mqas: test_thread_pool_create1() OK!")


def test_thread_pool_create2():
    berrymq.ThreadPool.make_thread_pool(5)
    assert len(berrymq.ThreadPool._pool) == 5
    assert berrymq.ThreadPool.empty() == False
    berrymq.ThreadPool.stop_thread_pool()
    assert len(berrymq.ThreadPool._pool) == 0
    assert berrymq.ThreadPool.empty() == True
    print("berrymq: test_thread_pool_create2() OK!")


def test_thread_pool_recreate1():
    berrymq.ThreadPool.make_thread_pool(3)
    assert len(berrymq.ThreadPool._pool) == 3
    berrymq.ThreadPool.make_thread_pool(5)
    assert len(berrymq.ThreadPool._pool) == 5
    berrymq.ThreadPool.stop_thread_pool()
    assert len(berrymq.ThreadPool._pool) == 0
    print("berrymq: test_thread_pool_recreate1() OK!")


def test_thread_pool_recreate2():
    berrymq.ThreadPool.make_thread_pool(5)
    assert len(berrymq.ThreadPool._pool) == 5
    berrymq.ThreadPool.make_thread_pool(5)
    assert len(berrymq.ThreadPool._pool) == 5
    berrymq.ThreadPool.stop_thread_pool()
    assert len(berrymq.ThreadPool._pool) == 0
    print("berrymq: test_thread_pool_recreate2() OK!")


def test_thread_pool_recreate3():
    berrymq.ThreadPool.make_thread_pool(5)
    assert len(berrymq.ThreadPool._pool) == 5
    berrymq.ThreadPool.make_thread_pool(3)
    time.sleep(1)
    berrymq.ThreadPool.clear_thread_pool()
    assert len(berrymq.ThreadPool._pool) == 3
    berrymq.ThreadPool.stop_thread_pool()
    assert len(berrymq.ThreadPool._pool) == 0
    print("berrymq: test_thread_pool_recreate3() OK!")


def test_followers_works_parallely1():
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
    assert call_history == ["com1_1", "com1_2", "com2_1",
                            "com2_2", "exp_1", "exp_2"]
    print("berrymq: test_followers_works_parallely1() OK!")


def test_followers_works_parallely2():
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
    #print(call_history)
    assert call_history == ["exp_1", "com1_1", "com2_1",
                            "exp_2", "com1_2", "com2_2"]
    print("berrymq: test_followers_works_parallely2() OK!")


def test(berrymq_module):
    global berrymq
    berrymq = berrymq_module
    test_thread_pool_create1()
    test_thread_pool_create2()
    test_thread_pool_recreate1()
    test_thread_pool_recreate2()
    test_thread_pool_recreate3()
    test_followers_works_parallely1()
    test_followers_works_parallely2()

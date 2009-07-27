# -*- coding: utf-8 -*-

berrymq = None

def identifier_test():
    exposer1 = berrymq.Identifier("id_sample1:entry")
    follower1 = berrymq.Identifier("id_sample1:entry")
    assert follower1.is_match(exposer1)

    exposer2 = berrymq.Identifier("id_sample2")
    follower2 = berrymq.Identifier("id_sample2:entry")
    assert follower2.is_match(exposer2)

    exposer3 = berrymq.Identifier("id_sample3:test")
    follower3 = berrymq.Identifier("id_sample3:*")
    assert follower3.is_match(exposer3)

    exposer4 = berrymq.Identifier("id_sample4:entry")
    follower4 = berrymq.Identifier("*:entry")
    assert follower4.is_match(exposer4)

    assert exposer1.available_for_exposition()
    assert not exposer2.available_for_exposition()
    assert exposer3.available_for_exposition()
    assert not follower3.available_for_exposition()
    assert not follower4.available_for_exposition()

    print("berrymq: identifier_test() OK!")


def entry_test():
    call_history = []
    @berrymq.auto_twitter("sample1", entry=True)
    def sample_expose1():
        call_history.append("expose")

    @berrymq.following_function("sample1:entry")
    def test_entry(message):
        assert message.id == "sample1:entry"
        call_history.append("entry")

    sample_expose1()
    assert call_history == ["entry", "expose"]
    print("berrymq: entry_test() OK!")


def exit_test():
    call_history = []
    @berrymq.auto_twitter("sample2", exit=True)
    def sample_expose():
        call_history.append("expose")

    @berrymq.following_function("sample2:exit")
    def test_entry(message):
        call_history.append("exit")

    sample_expose()
    assert call_history == ["expose", "exit"]
    print("berrymq: exit_test() OK!")


def func_test():
    call_history = []
    @berrymq.auto_twitter("sample3")
    def sample_expose():
        #if len(call_history) != 0:
        #    raise ValueError()
        call_history.append("expose")

    @berrymq.following_function("sample3:entry")
    def test_entry(message):
        call_history.append("entry")

    @berrymq.following_function("sample3:exit")
    def test_exit(message):
        call_history.append("exit")

    sample_expose()
    assert call_history == ["entry", "expose", "exit"]
    print("berrymq: func_test() OK!")


def original_exposepoint_test():
    call_history = []

    def sample_expose3():
        call_history.append("expose")
        berrymq.twitter("sample4:original")

    @berrymq.following_function("sample4:original")
    def test_original(message):
        call_history.append("original")

    sample_expose3()
    assert call_history == ["expose", "original"]
    print("berrymq: original_exposepoint_test() OK!")


def wildcard_following_test():
    call_history = []

    def sample_twitter3():
        call_history.append("action")
        berrymq.twitter("sample10:action")

    @berrymq.following_function("*:action")
    def test_original(message):
        call_history.append("accept")

    sample_twitter3()
    assert call_history == ["action", "accept"]
    print("berrymq: wildcard_following_test() OK!")


def staticmethod_test():
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
    assert call_history == ["entry", "expose"]
    print("berrymq: staticmethod_test() OK!")


def classmethod_test():
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
    assert call_history == ["entry", "expose"]
    print("berrymq: classmethod_test() OK!")


def instancemethod_test():
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
    assert call_history == ["entry", "expose"]
    print("berrymq: instancemethod_test() OK!")


def guard_condition_test():
    call_history = []
    @berrymq.auto_twitter("sample8")
    def sample_expose(arg):
        call_history.append("expose")

    @berrymq.following_function("sample8:entry", guard_condition=lambda message: message.args[0] == "match")
    def test_entry(message):
        call_history.append("entry")

    @berrymq.following_function("sample8:exit", guard_condition=lambda message: message.args[0] == "match")
    def test_entry(message):
        call_history.append("exit")

    sample_expose("not match")
    assert call_history == ["expose"]
    print("berrymq: guard_condition_test() OK!")


def composite_condition_test():
    call_history = []
    @berrymq.auto_twitter("sample9_1", entry=True)
    def sample_expose1(arg):
        call_history.append("expose1", entry=True)

    @berrymq.auto_twitter("sample9_2")
    def sample_expose2(arg):
        call_history.append("expose2")

    @berrymq.following_function(berrymq.cond("sample9_1:entry") & berrymq.cond("sample9_2:entry"))
    def test_and_condition(message):
        call_history.append("and_condition")

    sample_expose1()
    sample_expose2()

    assert call_history == ["expose1", "and_condition", "expose2"]
    print("berrymq: composite_condition_test() OK!")


def test(berrymq_module):
    global berrymq
    berrymq = berrymq_module
    identifier_test()
    entry_test()
    exit_test()
    func_test()
    original_exposepoint_test()
    wildcard_following_test()
    staticmethod_test()
    classmethod_test()
    instancemethod_test()
    guard_condition_test()

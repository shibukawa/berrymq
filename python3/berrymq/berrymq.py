# -*- coding: utf-8 -*-

"""Commitment oriented architecture framework implementations.

This is my experimental idea.

In Hollywood's raw, object B doesn't know when it called(System A).

A -> B

In This framework, it has different philosophy(System B).

A ... I'm hungry
  B ... Yes! Have a humbarger. Here you are!

System A is allopoietic and system B is autopoietic(but it has no special
features to generate copies). All objects in system B behave distributed
autonomously. Its object knows boundary between itself and outer world.
It knows what it can do and when it should work. In Hollywood's raw,
It knows what it can do but it doesn't know when it should work.

This implementation's API uses metaphor of twitter(but it does not follows
people but message/event):

  class A:
    def do_something(self):
      twitter("I'm hungry")

  class B(__metaclass__=Follower):
    @following("I'm hungry")
    def give_hunberger(self, message):
      print("Yes! Have a humbarger. Here you are!")

Recent frameworks inject dependencies in setting up time. But all objects
in this framework don't have dependencies at any time. In fact, you should use
this mechanism between same level objects. I call it "society".
Many systems (including real world) are hierarchical society.
Any books says that 200 is the biggest members it can live in one group
without any special rules and hierarchy.
Between societies, you can use normal relationship(including Hallywoods raw).

Have fun!

This architecture inspired by Toradora!. It's Japanese nobel/cartoon.
Characters in this pieces behave to give profit for others.
They live strongly.
This story is more impressed than Takeshi Kitano's films for me.

"""

import re
import sys
import queue
import types
import weakref
import threading
import xmlrpc.client
import itertools
import functools

from . import berrymq_network as network


def _dummy(message):
    """Dummy guard condition function.

    It always matches.

    @param message: passed values from expositions.
    @type  message: Message object.
    @return: whether follower should be called or not.
    @rtype : boolean.
    """
    return True


class Identifier:
    """Event naming identifier.

    identifier is built by string.
    It supports wildcard.

    "sample:*" => match any action in "sample"
    "*:entry" => match any "entry" messsge

    @future: including URI(for external followable node)
    """
    __slots__ = ("name", "action", "namespace", "functions")
    _split_name_action = re.compile(r"(.*):(.*)")
    _split_namespace = re.compile(r"(.*)@(.*)")

    def __init__(self, key_or_identifier, action=None, guard_condition=_dummy):
        self.functions = [None, None]
        if action is not None:
            self.name = key_or_identifier.name
            self.action = set([action])
            self.functions[0] = self._match_all
            return
        name, namespace, action = self._split_key(key_or_identifier)
        self.namespace = namespace
        if name == "*" and action == "*":
            self.name = None
            self.action = None
            self.functions[0] = self._match_always
        elif name == "*" and action != "*":
            self.name = None
            self.action = set([action])
            self.functions[0] = self._match_action_only
        elif name != "*" and action == "*":
            self.name = name
            self.action = None
            self.functions[0] = self._match_name_only
        elif name != "*" and action != "*":
            self.name = name
            self.action = set([action])
            self.functions[0] = self._match_all
        self.functions[1] = guard_condition

    def _split_key(self, key):
        match = self._split_name_action.match(key)
        if match:
            name, action = match.groups()
        else:
            name = key
            action = "*"
        match = self._split_namespace.match(name)
        if match:
            name, namespace = match.groups()
        else:
            namespace = None
        return name, namespace, action

    def __str__(self):
        return "<berrymq.Identifier object at %d: id=%s>" % (
            id(self), self.id_str())

    def id_str(self):
        name = "*" if self.name is None else self.name
        action = "*" if self.action is None else ",".join(sorted(self.action))
        return "%s:%s" % (name, action)

    @classmethod
    def _match_all(cls, lhs, rhs):
        return cls._match_name_only(lhs, rhs) \
            and cls._match_action_only(lhs, rhs)

    @staticmethod
    def _match_name_only(lhs, rhs):
        if None in [lhs.name, rhs.name]:
            return
        return lhs.name == rhs.name

    @staticmethod
    def _match_action_only(lhs, rhs):
        if lhs.action is None:
            return bool(rhs.action)
        if rhs.action is None:
            return bool(lhs.action)
        return bool(lhs.action & rhs.action)

    @staticmethod
    def _match_always(lhs, rhs):
        return True

    def is_match(self, expose_identifier, message=None):
        if self.functions[0](self, expose_identifier):
            return self.functions[1](message)
        return False

    def is_local(self):
        return self.name.startswith("_")


class cond(object):
    def __init__(self, identifier, guard_condition=_dummy):
        self.targets = [Identifier(identifier, guard_condition=guard_condition)]

    def __and__(self, rhs):
        newtarget = target(None, None)
        newtarget.targets = self.targets + rhs.targets
        return newtarget


def _get_attributes(instance, typeobj):
    """Helper generator to implement TDFW.

    It returns match objects.
    """
    for key in dir(instance):
        if key.startswith("__"):
            continue
        value = getattr(instance, key)
        if type(value) == typeobj:
            yield value


class _weakmethod_ref:
    """This method is arange version of Python Cookbook 2nd 6.10"""
    __slots__ = ("_obj", "_func")
    def __init__(self, fn):
        try:
            o, f = fn.__self__, fn.__func__
        except AttributeError:
            self._obj = None
            self._func = fn
        else:
            self._obj = weakref.ref(o)
            self._func = f

    def __call__(self):
        if self._obj is None:
            return self._func
        elif self._obj() is None:
            return None
        return types.MethodType(self._func, self._obj())


class _weakfunction_ref(object):
    """This method is arange version of Python Cookbook 2nd 6.10"""
    __slots__ = ("_func")
    def __init__(self, fn):
        self._func = weakref.ref(fn)

    def __call__(self):
        if self._func() is None:
            return None
        return self._func()


class InvalidExpositionName(Exception): pass


class MessageQueueAsStructure:
    _followers = {}
    _expositions = set()

    def __init__(self):
        pass

    def get_valid_followers(self):
        for name, followers in self._followers.items():
            for id_obj, function_wrapper in followers:
                function = function_wrapper()
                if function is not None:
                    yield id_obj, function

    def get_valid_expositions(self):
        for id_obj, function_wrapper in self._expositions:
            function = function_wrapper()
            if function is not None:
                yield id_obj, function

    def regist_exposition(self, id_obj, function):
        self._expositions.add((id_obj, function))

    def regist_follower(self, id_obj, function):
        followers = self._followers.setdefault(id_obj.name, [])
        followers.append((id_obj, function))

    def twitter(self, id_obj, args, kwargs, counter=100):
        self.twitter_local(id_obj, args, kwargs, counter)
        #if p2p._receiver:
        #    p2p._receiver._twitter_to_other_process(id_obj, args, kwargs)


    def twitter_local(self, id_obj, args, kwargs, counter=100):
        message = Message(id_obj, args, kwargs, counter)
        wildcard_actions = self._followers.get(None, [])
        certaion_actions = self._followers.get(id_obj.name, [])
        for follower in itertools.chain(certaion_actions, wildcard_actions):
            following_id, function = follower
            if not following_id.is_match(id_obj, message):
                continue
            if function() is None:
                continue # delete after
            if ThreadPool.empty():
                function()(message)
            else:
                ThreadPool.request_work(function(), message)


class ThreadPool(object):
    _qin = queue.Queue()
    _qerr = queue.Queue()
    _pool = []

    @classmethod
    def _report_error(cls):
        cls._qerr.put(sys.exc_info()[:2])

    @staticmethod
    def _get_all_from_queue(Q):
        try:
            while True:
                yield Q.get_nowait()
        except queue.Empty:
            raise StopIterator

    @classmethod
    def do_work_from_queue(cls):
        while True:
            command, target_method, message = cls._qin.get()
            if command == "stop":
                break
            try:
                if command == "process":
                    target_method(message)
                else:
                    raise ValueError("Unknown command %r" % command)
            except:
                cls._report_error()

    @classmethod
    def make_thread_pool(cls, number):
        if number < 0:
            raise ValueError("'number' should be bigger than 0.")
        number -= len(cls._pool)
        if number > 0:
            for i in range(number):
                new_thread = threading.Thread(target=cls.do_work_from_queue)
                new_thread.setDaemon(True)
                cls._pool.append(new_thread)
                new_thread.start()
        elif number < 0:
            number = abs(number)
            for i in range(number):
                cls.request_work(None, None, "stop")

    @classmethod
    def empty(cls):
        return len(cls._pool) == 0

    @classmethod
    def clear_thread_pool(cls):
        alive_list = []
        for thread in cls._pool:
            if thread.isAlive():
                alive_list.append(thread)
        cls._pool = alive_list


    @classmethod
    def request_work(cls, target_function, message, command="process"):
        cls._qin.put((command, target_function, message))

    @classmethod
    def get_all_errors(cls):
        return cls._get_all_from_queue(cls._qerr)

    @classmethod
    def stop_thread_pool(cls):
        for i in range(len(cls._pool)):
            cls.request_work(None, None, "stop")
        for existing_thread in cls._pool:
            existing_thread.join()
        del cls._pool[:]


class OpenMethodAttribute(object):
    """This class is attached to exposition/following functions/methods.

    After initialization, this shows any information to draw connections.

    @sa exposition
    @sa following
    @sa following_method
    """
    __slots__ = ("expositions", "followers", "is_init")
    attribute_name = "__exposition_information"
    def __init__(self):
        self.expositions = []
        self.followers = []
        self.is_init = False

    @classmethod
    def add_follower(cls, id_obj, function):
        attribute = cls._set_open_method_attribute(function)
        attribute.followers.append(id_obj)

    @classmethod
    def add_exposition(cls, id_obj, function):
        attribute = cls._set_open_method_attribute(function)
        attribute.expositions.append(id_obj)

    @classmethod
    def _set_open_method_attribute(cls, function):
        attribute = getattr(function, cls.attribute_name, None)
        if attribute is None:
            attribute = cls()
            setattr(function, cls.attribute_name, attribute)
        return attribute


def following_function(identifier, guard_condition=_dummy):
    id_obj = Identifier(identifier, guard_condition=guard_condition)
    def _(f):
        _berrymq.regist_follower(id_obj, _weakfunction_ref(f))
        return f
    return _


def following(identifier, guard_condition=_dummy):
    id_obj = Identifier(identifier, guard_condition=guard_condition)
    def _(f):
        OpenMethodAttribute.add_follower(id_obj, f)
        return f
    return _


def auto_twitter(identifier, entry=False, exit=False):
    id_obj = Identifier(identifier)
    def _(func):
        if entry == exit:
            entry_id = Identifier(id_obj, "entry")
            exit_id = Identifier(id_obj, "exit")
            @functools.wraps(func)
            def __(*args, **kwargs):
                _berrymq.twitter(entry_id, args, kwargs)
                func(*args, **kwargs)
                _berrymq.twitter(exit_id, args, kwargs)
            return __
        elif exit or id_obj.action is not None and "exit" in id_obj.action:
            id_obj.action = set(["exit"])
            @functools.wraps(func)
            def __(*args, **kwargs):
                func(*args, **kwargs)
                _berrymq.twitter(id_obj, args, kwargs)
            return __
        elif entry or id_obj.action is not None and "entry" in id_obj.action:
            id_obj.action = set(["entry"])
            @functools.wraps(func)
            def __(*args, **kwargs):
                _berrymq.twitter(id_obj, args, kwargs)
                func(*args, **kwargs)
            return __
        return func
    return _


class Follower(type):
    """Metaclass for definition of follower instance methods.

    use like this:

      class Logger(metaclass=Follower):
          @following_method("function", "call")
          def log_function_call(self, message):
              ...

          @classmethod
          @following_classmethod("error", "raised")
          def show_error(cls, message):
              ...

          @staticmethod
          @following("thread", "created")
          def log_thread(message):
              ...
    """
    def __new__(cls, name, bases, dict):
        """Create exposition point for classmethod."""
        newtype = type.__new__(cls, name, bases, dict)
        for method in _get_attributes(newtype, types.MethodType):
            attribute = getattr(method, OpenMethodAttribute.attribute_name, None)
            if attribute is None:
                continue
            for id_obj in attribute.followers:
                _berrymq.regist_follower(id_obj, _weakmethod_ref(method))
            for id_obj in attribute.expositions:
                _berrymq.regist_exposition(id_obj, _weakmethod_ref(method))

            attribute.is_init = True
        return newtype

    def __call__(cls, *args):
        """Create exposition point for instancemethod."""
        instance = type.__call__(cls, *args)
        for method in _get_attributes(instance, types.MethodType):
            attribute = getattr(method, OpenMethodAttribute.attribute_name, None)
            if attribute is None:
                continue
            if attribute.is_init:
                continue
            for id_obj in attribute.followers:
                _berrymq.regist_follower(id_obj, _weakmethod_ref(method))
            for id_obj in attribute.expositions:
                _berrymq.regist_exposition(id_obj, _weakmethod_ref(method))
        return instance


class Message(object):
    def __init__(self, id_obj, args, kwargs, counter):
        self._id_obj = id_obj
        self._args = args
        self._kwargs = kwargs
        self._counter = counter
        self.__dict__.update(kwargs)

    @property
    def name(self):
        return self._id_obj._name

    @property
    def action(self):
        return self._id_obj._action

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def id(self):
        return self._id_obj.id_str()

    def twitter(self, id_obj, **kwargs):
        _berrymq.twitter(id_obj, kwargs, self._counter-1)

    def apply(self, func):
        """Utility method to enease method call deligation.

        You can use like this:
          @exposition("result", "show")
          def show_result(score):
              print("my score:", score)
              twitter("result", "show", username="shibu", score=score) # get 2 kwparams

          def log(username, score): # same params with exposition point.
              ...

          @following("result", "show")
          def log_score_exposition(message):
              message.apply(log) # use this!

        """
        return func(**self.kwargs)


_berrymq = MessageQueueAsStructure()


def set_multiplicity(number):
    if number != 0:
        ThreadPool.make_thread_pool(number)
    else:
        ThreadPool.clear_thread_pool()


def show_expositions():
    methods = []
    for id_obj, function_wrapper in _berrymq.get_valid_expositions():
        for action in id_obj.action:
            methods.append("%s:%s" % (id_obj.name, action))
    return sorted(set(methods))


def show_followers():
    methods = []
    for id_obj, function_wrapper in _berrymq.get_valid_followers():
        for action in id_obj.action:
            methods.append("%s:%s" % (id_obj.name, action))
    return sorted(set(methods))


def show_network():
    network = {}
    nodes = []
    edges = []
    classobjs = set()

    nodetype = {"class":{"shape":"box3d", "bgcolor":"#C1E4FF",
                         "pencolor":"#358ACC"},
                "joint":{"shape":"none"}}

    for name, action, method in _berrymq.get_valid_expositions():
        key = (name, action)
        net = network.setdefault(key, {"follower":[], "exposition":[]})
        if isinstance(method, types.MethodType):
            classobjs.add(method.__self__.__class__)
            net["exposition"].append(id(method.__self__.__class__))
        else:
            net["exposition"].append(None)

    for name, action, method in _berrymq.get_valid_followers():
        key = (name, action)
        net = network.setdefault(key, {"follower":[], "exposition":[]})
        if isinstance(method, types.MethodType):
            classobjs.add(method.__self__.__class__)
            net["follower"].append(id(method.__self__.__class__))
        else:
            net["follower"].append(None)

    for classobj in classobjs:
        nodes.append(["class", id(classobj), classobj.__name__])

    for key in network:
        followers = network[key]["follower"]
        expositions = network[key]["exposition"]
        if len(followers) == 1 and len(expositions) == 1:
            edges.append([expositions[0], followers[0],
                          {"label": "%s:%s"%key}])
        else:
            nodes.append(["joint", id(classobj), "%s:%s"%key])
            for exposition in expositions:
                edges.append([exposition, id(classobj),{"label":""}])
            for follower in followers:
                edges.append([id(classobj), follower,{"label":""}])
    result = ["digraph {"]

    for typename, objid, label in nodes:
        params = ['label="%s"' % label]
        params += ['%s="%s"' % item for item in nodetype[typename].items()]
        result.append("  %s [%s];" % (objid, ", ".join(params)))
    for start, end, params in edges:
        param_str = ['%s="%s"' % item for item in params.items()]
        result.append("  %s -> %s [%s];" % (start, end, ", ".join(param_str)))
    result.append("}")
    return "\n".join(result)


def twitter(identifier, *args, **kwargs):
    _berrymq.twitter(Identifier(identifier), args, kwargs)


class MessageQueueReceiver(object):
    def __init__(self, url):
        self.servers = {}
        self.my_url = url

    def _add_connection(self, url):
        proxy = xmlrpc.client.ServerProxy(url)
        self.servers[url] = proxy
        proxy.connect(self.my_url)

    def connect(self, url):
        self.servers[url] = xmlrpc.client.ServerProxy(url)
        return True

    def quit(self):
        global _stop_server
        _stop_server = True
        return True

    def send_twitter(self, id, args, kwargs):
        print("twitter from other: %s args=%s, kwargs=%s" % (id, args, kwargs))
        _berrymq.twitter_local(Identifier(id), args, kwargs)
        return True

    def _twitter_to_other_process(self, id_obj, args, kwargs):
        for server in self.servers.values():
            server.send_twitter(id_obj.id_str(), args, kwargs)
        return True

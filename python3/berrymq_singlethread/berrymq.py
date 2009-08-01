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
import itertools
import functools


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
            self.namespace = key_or_identifier.namespace
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

    def _match_all(self, rhs):
        return self._match_name_only(rhs) and self._match_action_only(rhs)

    def _match_name_only(self, rhs):
        if rhs.name is None:
            return True
        return self.name == rhs.name

    def _match_action_only(self, rhs):
        if rhs.action is None:
            return True
        return bool(self.action & rhs.action)

    def _match_always(self, rhs):
        return True

    def is_match(self, expose_identifier, message=None):
        if self.functions[0](expose_identifier):
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


class _weakfunction_ref:
    """This method is arange version of Python Cookbook 2nd 6.10"""
    __slots__ = ("_func")
    def __init__(self, fn):
        self._func = weakref.ref(fn)

    def __call__(self):
        if self._func() is None:
            return None
        return self._func()


class Transporter:
    _followers = {}

    def get_valid_followers(self):
        for name, followers in self._followers.items():
            for id_obj, function_wrapper in followers:
                function = function_wrapper()
                if function is not None:
                    yield id_obj, function

    def regist_follower(self, id_obj, function):
        followers = self._followers.setdefault(id_obj.name, [])
        followers.append((id_obj, function))

    def twitter(self, id_obj, args, kwargs, counter=100):
        message = Message(id_obj, args, kwargs, counter)
        if id_obj.name is None:
            actions = self._followers.values()
        else:
            wildcard_actions = self._followers.get(None, [])
            certain_actions = self._followers.get(id_obj.name, [])
            actions = [wildcard_actions, certain_actions]
        for following_id, function in itertools.chain(*actions):
            if not following_id.is_match(id_obj, message):
                continue
            if function() is None:
                continue # delete after
            else:
                function()(message)


class RootTransporter:
    _default_namespace = None
    _namespaces = {}

    @classmethod
    def twitter(cls, id_obj, args, kwargs):
        namespace = id_obj.namespace
        if namespace is None:
            namespace = cls._default_namespace
        cls.get(namespace).twitter(id_obj, args, kwargs)

    @classmethod
    def regist_follower(cls, id_obj, method):
        namespace = id_obj.namespace
        if namespace is None:
            namespace = cls._default_namespace
        cls.get(namespace).regist_follower(id_obj, method)

    @classmethod
    def show_followers(cls):
        pass

    @classmethod
    def get(cls, namespace):
        message_queue = cls._namespaces.get(namespace)
        if message_queue is None:
            message_queue = Transporter()
            cls._namespaces[namespace] = message_queue
        return message_queue

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


class MethodDecorator:
    """This class is attached to exposition/following functions/methods.

    After initialization, this shows any information to draw connections.

    @sa exposition
    @sa following
    @sa following_method
    """
    __slots__ = ("expositions", "followers", "is_init")
    attribute_name = "__exposition_information"
    def __init__(self):
        self.followers = []
        self.is_init = False

    @classmethod
    def add_follower(cls, id_obj, function):
        attribute = cls._set_open_method_attribute(function)
        attribute.followers.append(id_obj)

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
        RootTransporter.regist_follower(id_obj, _weakfunction_ref(f))
        return f
    return _


def following(identifier, guard_condition=_dummy):
    id_obj = Identifier(identifier, guard_condition=guard_condition)
    def _(f):
        MethodDecorator.add_follower(id_obj, f)
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
                RootTransporter.twitter(entry_id, args, kwargs)
                func(*args, **kwargs)
                RootTransporter.twitter(exit_id, args, kwargs)
            return __
        elif exit or id_obj.action is not None and "exit" in id_obj.action:
            id_obj.action = set(["exit"])
            @functools.wraps(func)
            def __(*args, **kwargs):
                func(*args, **kwargs)
                RootTransporter.twitter(id_obj, args, kwargs)
            return __
        elif entry or id_obj.action is not None and "entry" in id_obj.action:
            id_obj.action = set(["entry"])
            @functools.wraps(func)
            def __(*args, **kwargs):
                RootTransporter.twitter(id_obj, args, kwargs)
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
            attribute = getattr(method, MethodDecorator.attribute_name, None)
            if attribute is None:
                continue
            for id_obj in attribute.followers:
                RootTransporter.regist_follower(id_obj, _weakmethod_ref(method))
            attribute.is_init = True
        return newtype

    def __call__(cls, *args):
        """Create exposition point for instancemethod."""
        instance = type.__call__(cls, *args)
        for method in _get_attributes(instance, types.MethodType):
            attribute = getattr(method, MethodDecorator.attribute_name, None)
            if attribute is None:
                continue
            if attribute.is_init:
                continue
            for id_obj in attribute.followers:
                RootTransporter.regist_follower(id_obj, _weakmethod_ref(method))
        return instance


class Message:
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
        RootTransporter.twitter(id_obj, kwargs, self._counter-1)

    def apply(self, func):
        """Utility method to enease method call deligation.

        You can use like this:
          @exposition("result", "show")
          def show_result(score):
              print("my score:", score)
              # get 2 kwparams
              twitter("result", "show", username="shibu", score=score) 

          def log(username, score): # same params with exposition point.
              ...

          @following("result", "show")
          def log_score_exposition(message):
              message.apply(log) # use this!

        """
        return func(**self.kwargs)


def show_followers():
    methods = []
    for id_obj, function_wrapper in RootTransporter.get_valid_followers():
        for action in id_obj.action:
            methods.append("%s:%s" % (id_obj.name, action))
    return sorted(set(methods))


def twitter(identifier, *args, **kwargs):
    RootTransporter.twitter(Identifier(identifier), args, kwargs)

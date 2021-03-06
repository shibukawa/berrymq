.. highlightlang:: rest

============
Introduction
============

**berryMQ** is a on-memory tiny message queuing library. Project goal is "programmer friendly MQ". This doesn't aim reliability, persistency. It will support cross-language messaging(Python, Ruby and so on).

.. _identifier:

Identifier
==========

   This is a key rule of berryMQ. Identifier is used as:

   * Message ID
   * receive filter

   Identifier consists of two parts. First one is called ``name``, second is
   ``action``. You can specify it following form::

      "name:action"

   Identifier can accept wildcard(*). If there is an identifier ``"test:*"``,
   it matchs both ``"test:run"`` and ``"test:stop"``. Show all variations:

   ============ ======== =========
   Sample       Name     Action
   ============ ======== =========
   ``test:run`` ``test`` ``run``
   ``test:*``   ``test`` ``*``
   ``*:run``    ``*``    ``run``
   ``*:*``      ``*``    ``*``
   ``test``     ``test`` ``*``
   ============ ======== =========

.. index::
   single: Push API
   single: API; Push

Push API
========

.. index::
   class: berrymq.Follower

Use with method receiver
------------------------

Any object can use as message receiver. In python, this mechanism is realized by mata class feature. Hear is a Python 3.x sample. It is a most common way to use berryMQ.

.. code-block:: python

  class Logger(metaclass=Follower):
      @following("*:log")
      def receive_log(self, message):
         ...

This is sample for Ruby.

.. code-block:: ruby

   # Ruby
   class Logger
     include BerryMQ::Follower
     
     following("*:log")
     def receive_log(message)
        ...
     end
   end

.. seealso::

   You can see detail information and sample codes for Python 2.x at :class:`Follower`.

Use with function receiver
--------------------------

.. note::

   This version supports python only.

This is the easiest way to use berryMQ. Show Python sample.

.. code-block:: python

   from berrymq import (following_function, twitter)
   import time

   @following_function("*:log")
   def receive_log(message):
       print("receive_log: %s @ %s" % (message.id, message.args[0]))

   @following_function("*:command")
   def run_command(message):
       # do job
       ...

   def do_something():
       twitter("do_something:log", time.ctime())
      
   def on_start_button_pressed():
       twitter("start:command")
   
There two sender functions and two receivers. :func:`twitter` is API for sending message. :func:`following_function` is a decorator for a receiver function. Message has a :ref:`identifier`. Senders and receivers assert which message will be sended or is needed by identifier. Both of parts of identifier can use wild card(*).

If you call ``do_something()`` function in above sample, this function send a message ``do_something:log``. This message matches ``*:log`` filter of ``receive_log()`` function. So ``receive_log()`` function will be called. If there are more than one matched functions, all functions will be called.

.. image:: sample_diagram_01.png

.. index::
   single: Pull API
   single: API; Pull

Pull API
========

Pull API feature is supported by :class:`berrymq.Queue`. 
Creating new queue is easy like this:

.. code-block:: python

   queue = berrymq.Queue("task:*")

After creating queue, berryMQ will store all massages which match first argument pattern to queue. You can pull that message when you like.

.. code-block:: python

   message = queue.get()

There are two methods to get message. :meth:`berryMQ.Queue.get` and :meth:`berryMQ.Queue.get_nowait`. If the queue was empty, :meth:`berryMQ.Queue.get` will block until any message will reach.

.. note::

   ``get(block=False)`` and ``get_nowait()`` are same. 

.. index::
   single: Inter-process communication

Inter-Process Communication
===========================

.. versionadded:: 0.2

berryMQ supports inter-process communication. berryMQ sends message via JSON-RPC. So any language which can speak JSON-RPC will be able to connect.

.. _inter_process_style01:

Style 01:
---------

This is an equality connection style. Both side of berryMQ transport all message to each other. Message senders and receivers don't take care which side messages come from/go to.

.. image:: sample_diagram_02.png

.. _inter_process_style02:

Style 02:
---------

One side process doesn't receive but send message. It is suitable style for logging. Server/Client model.

.. image:: sample_diagram_03.png

.. _inter_process_style03:

Style 03:
---------

Usual Message Queue style. Create queue at server side. Client can use only pull API.

.. image:: sample_diagram_05.png

Callback Style API
==================

.. warning::

   This is planning feature.

:func:`twitter` is a monologue function. Method sender doesn't know who listening to that message. Although it will encourage loose-coupling, it is not convenient in some case i.e. method-chain. I'm planning "talk-back" API:

.. code-block:: python

   from berrymq import (following_function, talk)

   @following_function("*:process")
   def do_process(message):
       ... do something

   @following_function("*:log_result")
   def receive_result(message):
       logging.info(message.name)

   def on_unittest_start_button_pressed(event):
       talk("test:process", "test:log_result")

:func:`talk` function has two identifiers. Second one is target about callback. After calling first function(in this case ``do_process()``), Second function will be called with the result of first function.
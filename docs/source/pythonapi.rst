==========
Python API
==========

.. module:: berrymq
   :synopsis: berryMQ module

.. index::
   single: decorator; Python

Decorators
==========

.. function:: following(identifier[, guard_condition])

   This is a decorator function. This decorator can use for only instanse methods of the classes which use :class:`Follower` metaclass.

   :param identifier: receive message filter :ref:`identifier`.
   :type  identifier: str
   :param guard_condition: if this guard function return False, message receive will be skipped
   :type  guard_condition: callable object with one paramater(message object)

   .. seealso:: class :class:`Follower`, function :func:`following_function`


.. function:: following_function(identifier[, guard_condition])

   This is a decorator function. This decorator can use for only class methods, static methods, functions. if you want to use for instance methods, use :func:`following` instead of this function.

   :param identifier: receive message filter :ref:`identifier`.
   :type  identifier: str
   :param guard_condition: if this guard function return False, message receive will be skipped
   :type  guard_condition: callable object with one paramater(message object)

   .. seealso:: function :func:`following_function`


.. function:: auto_twitter(identifier[, entry[, exit]])

   This is a decorator function. 
   The decorated function is called, automatically sends message.

   .. code-block:: python

      @auto_twitter("function")
      def sample_function():
          ... do something

   If this function is called, ``function:entry`` message will be sent before running function, and then ``function:exit`` message will be sent after running function.

   Use ``entry``, ``exit`` parameter for controlling message.

   ===== ===== ==================
   entry exit  action
   ===== ===== ==================
   False False send both.
   False True  exit message only
   True  False entry message only
   True  True  send both.
   ===== ===== ==================

   :param identifier: Send message :ref:``identifier``
   :type  identifier: str
   :param entry: Send message before calling function?(default: False)
   :type  entry: True or False
   :param exit: Send message after calling function?(default: False)
   :type  exit: True or False


.. function:: twitter_exception

   This is a decorator function. 
   If any exception raised in decorated function, send message.

.. index::
   single: function; Python

Functions
=========

Send Message
------------

.. function:: twitter(identifier[, ...])

   Send message. It is the most important function in berryMQ.
   This funciton can recieve any args and kwargs. These values are delivered
   via :class:`Message` object.

.. function:: talk(identifier, callback_identifier[, ...])

   Send message like :meth:`twitter` method. This function has callback 
   identifer. All receivers call back to this :ref:`identifier`.

   .. note::

      This is planning feature. It isn't implemented yet.

.. function:: send_message(token, identifier[, ...])

   Send message to other node. This function supports type02, type03 
   client/server style inter-process communication.

   :param token: return value of :func:`connect_oneway` or :func:`connect_via_queue`
   :type  token: str
   :param identifier: see :ref:`identifier`
   :type  identifier: str

Receive Message
---------------

Normally, you don't have to call receive functions. 
They are used in type03 inter-process communication context.

.. function:: get(token[, block[, timeout]])

.. function:: get_nowait(token)

Inter-process settings
----------------------

.. function:: init_connection(addr=("localhost", port=0))

   If you want to use style01 inter-process communication feature, 
   call this function first.

   .. versionadded:: 0.2

.. function:: interconnect(addr[, ttl=1000])

   Connect to other node in style01.
   
   :param addr: tuple which contains hostname and port number
   :type  addr: tuple

   .. versionadded:: 0.2

.. function:: connect_oneway(addr[, ttl=1000])

   Connect to other node in style02.

   :param addr: tuple which contains hostname and port number
   :type  addr: tuple

   .. versionadded:: 0.2

.. function:: connect_via_queue(addr, identfier[, ttl=1000])

   Connect to other node in style03. 
   :ref:`identifier` is a filter of queue input.

   :param addr: tuple which contains hostname and port number
   :type  addr: tuple
   :param identifier: filter of queue
   :type  identifier: str

   .. versionadded:: 0.2

.. function:: send_message(identifier[, ...])

   Send message to other nodes. If you use :func:`interconnect` to connect,
   you don't have to this method(forward twitter automatically).

   .. versionadded:: 0.2

.. function:: get([block=True[, timeout=1000]])

   :return: message
   :rtype:  :class:`Message`

   .. versionadded:: 0.2

.. function:: get_nowait()

   :return: message
   :rtype:  :class:`Message`

   .. versionadded:: 0.2

.. function:: close_connection([addr])

   Close connection.

   :param addr: tuple which contains hostname and port number
   :type  addr: tuple

   .. versionadded:: 0.2

Concurrency
-----------

.. function:: set_multiplicity(number)

   This function is set thread pool size.

Support Functions
-----------------

.. function:: regist_function(identifier, function)

.. function:: regist_method(identifier, method)

   These functions is used for changing identifier dynamically.

Classes
=======

.. class:: Follower

   If you want to use the method as receiver, set this class as metaclass.
   
   In python 2.4 - 2.6:

   .. code-block:: python

      # Python 2.4, 2.5, 2.6
      class Logger(object):
      	  __metaclass__ = Follower
      	  @following("*:log")
          def receive_log(self, message):
	          ...
	  
   In python 3.0 -:

   .. code-block:: python

      # Python 3.0, 3.1
      class Logger(metaclass=Follower):
          @following("*:log")
          def receive_log(self, message):
             ...

   If you use Ruby, This class provide special decorators. :func:`following` 
   and :func:`auto_twitter`. Use like this:

   .. code-block:: ruby

      # Ruby
      class Logger
        include BerryMQ::Follower
        
        following("*:log")
        def receive_log(message)
           ...
        end
      end

.. class:: Message

   This object is created in berryMQ automatically.
   User doesn't create this object directly.

   All of following attributes are readonly(defined as property).

   .. attribute:: name

      This is a front part of :ref:`identifier`.

   .. attribute:: action

      This is a back part of :ref:`identifier`.

   .. attribute:: id

      This is a string form of :ref:`identifier`

   .. attribute:: args

      If you pass any parameters at :func:`twitter`, this attribute stores them.

      .. code-block:: python

         .
         twitter("do_something:log", time.ctime())
         .
         
         @following("*:log)
         def receive_log(message):
             print(message.args[0])  # print time.ctime() value
         
   .. attribute:: kwargs

      It is similar to :attr:`args`. If you pass keyword argument, 
      you can access that value via this property.

      .. seealso:: :attr:`args`

.. class:: Queue

   This is a key class of pull API for message receiving.

   .. code-block:: python

      queue = berrymq.Queue("task:*")
      
      # wait until someone send "task:*" message
      message = queue.get()

   Method name of this class is similar to Python's standard library.
   This class doesn't have ``put()`` method, because of all stored items 
   are sent by berryMQ. User uses this object just as message receiver.

   .. method:: __init__(identifier[, shared=False])

      Create new method queue. 

      If you pass ``True`` at ``shared`` flag, 
      new object become a **shared** queue. If there are some objects which has 
      same :ref:`identifier`, they share only one queue. If some object
      :meth:`get` value, others can't get that message any more.

      In another case, new object become a **standalone** queue. If there are
      some objects which has same :ref:`identifier` and someone send
      message which matches that identifier, all queues will store a copy of 
      that message.
      
      :param identifier: works as a filter. see :ref:`identifier`.

   .. method:: empty

      Return ``True`` if the queue object is empty.

      If you use this class in concurrency envirionment, this result is not 
      reliable because other thread put new value after calling this method.

   .. method:: full

      Return ``True`` if the queue object is full. This return value is not
      reliable because of same reason of :meth:`empty`.

   .. method:: qsize

      Return stored item number. This return value is not
      reliable because of same reason of :meth:`empty`.

   .. method:: get([block=True[, timeout=None]])

      Return stored message. This is a FIFO queue.

      If ``block`` is ``True`` (defalut), function call is blocked while
      new message received. If ``False`` it returns immediately even if 
      the queue is empty.

      :param block: Blocking mode flag.
      :type  block: True of False
      :param timeout: Set timeout[sec]. It is used in blocking mode.     
      :return: stored :class:`Message` object

      .. note::

      	 Future release supports priority queue.

   .. method:: get_nowait

      This method is alias of ``get(block=False)``.

.. exception:: Empty

   This is a same class of :exc:`queue.Empty`. 
   Its object is raised by :meth:`Queue.get`

Adapters
========

.. module:: berrymq.adapter
   :synopsis: berryMQ adapter modules


.. module:: berrymq.adapter.growl
   :synopsis: berryMQ adapter for Growl

.. versionadded:: 0.2

Growl Adapter
-------------

.. class:: GrowlAdapter

   This is a adapter class for Growl.
   You can forward message to Growl.
   This class uses UDP protocol of Growl.

   .. note::

      Future release will support Growl Notification Transfer Protocol(GNTP).
      It supports call back mechanism.

   .. method:: __init__(identifier)

      
   .. method:: format(message)

      This is template method fou formatting message.
      Override this method. This method should return string.


.. module:: berrymq.adapter.fileobserver
   :synopsis: berryMQ adapter for observing file system

.. versionadded:: 0.3

File Observer
-------------

.. class:: FileObserver

   This is a adapter class for observing file system.
   This adapter can notify following change:
   
   * **created**
   * **modified**
   * **removed**
   
   sample:

   .. code-block:: python
   
      observer = berrymq.adapter.fileobserver.FileObserver("~/log/*.log", "local_log")
   
   If new log file is created, this object twitters ``local_log:created`` 
   message automatically. Anyone modify log files, ``local_log:modified`` will 
   be sent. Of course, ``local_log:removed`` message will be sent if 
   any file is removed.
   
   .. method:: __init__(target_dir, id_name[, interval=5])
   
      :param target_dir: Checking condition (see glob's document).
      :type  target_dir: str
      :param id_name: This value is used for message id
      :type  id_name: str
      :param interval: File system checking inteval
      :type  interval: int
   
   .. method:: stop()
   
      This method stop observing.

.. module:: berrymq.adapter.timer
   :synopsis: berryMQ adapter for timer

.. versionadded:: 0.3

Timer
-----

.. class:: IntervalTimer

   This is a simple intarval timer. Following adapter sends
   ``timer:tick`` message every 10 seconds.
   
   .. code-block:: python
   
      timer = berrymq.adapter.timer.IntervalTimer("timer", 10)
   
   .. method:: __init__(id_name, interval)
   
      :param id_name: This value is used for message id
      :type  id_name: str
      :param interval: This adapter send
      :type  interval: int
   
   .. method:: stop()
   
      This method stop observing.

.. module:: berrymq.adapter.wxpython
   :synopsis: berryMQ adapter for wxPython

.. versionadded:: 0.3

wxPython
--------

.. class:: wxPythonAdapter

   This class convert berryMQ message into wxPython's event.
   
   .. method:: __init__(window, id_filter)
   
      :param window: This is a wxPython's window that handles events.
      :type  window: wx.Window
      :param id_filter: The message will transfer to wxPython if matches it
      :type  id_filter: str
   
.. class:: BerryMQEvent

   This is event class of wxPython.

.. function:: EVT_BERRYMQ_MSG

   This is an event binder. See wxPython's document.
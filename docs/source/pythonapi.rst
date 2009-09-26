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

.. function:: init_connection([host="localhost"[, port=0]])

.. function:: connect_interactively(url[, ttl=1000])

.. function:: connect_oneway(url[, ttl=1000])

.. function:: connect_via_queue(url, identfier[, ttl=1000])

.. function:: close_connection([url])

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
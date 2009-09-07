========
Ruby API
========

Ruby API is similar to Python API. I this section show samples in Ruby. 
If you need detail information see Python API reference.

.. index::
   single: decorator; Ruby

Decorators
==========

berryMQ provides module methods ``following()`` and ``auto_twitter()``. They works like ``Class.public`` and ``Class.private`` and so on.
Use this like following:

.. code-block:: ruby

   require 'berrymq'

   class Logger
     include BerryMQ::Follower

     following("*:log")
     def receive_log(message)
       ...
     end
   end

``Class.public`` keeps effect until other module method will be called, 
But this functions effect only the next method definition.

.. seealso::

   Python decorator :func:`berrymq.following`
      Set target funcion as receiver.
   Python decorator :func:`berrymq.auto_twitter`
      Send message if target function will be called.
   Python meta class :class:`berrymq.Follower`
      This class adds berryMQ features to target class.

.. index::
   single: function; Ruby

.. warning::

   Ruby implementation uses module including mechanism to class.
   So you can't set module function receiver like Python.

Functions
=========

You can use :func:`berrymq.twitter` function like this:

.. code-block:: ruby

   require 'berrymq'

   def on_button_pressed
     BerryMQ::twitter("on_button_pressed:log")
     .
     .
   end

.. seealso:: :func:`berrymq.twitter`

.. note::

   In future release, if last paramter is ``Hash``, it will pass as kwargs.

.. index::
   single: class; Ruby

Classes
=======

now writing...
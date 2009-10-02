Welcome
=======

berryMQ is a on-memory tiny message queuing library. Project goal is *programmer friendly MQ*. This not aims reliability, persistency. It will support cross-languages messaging(Python, Ruby and so on).

Current version has following features:

* **Push API:** event driven style API like twitter:-)
* **Pull API:** simple queue object
* **Multi language support:** Python(2.4 - 3.1) and Ruby(1.8.7, 1.9.1)

Now following features are under construction:

* **Inter-process communication:** communicate via JSON-RPC
* **Call back API:** easy to use method-chain
* **More language support:** I'd like to support JavaScript and so on

Documentation
=============

.. toctree::
   :maxdepth: 2

   intro
   pythonapi
   rubyapi
   messages
   rpc_protocol
   features
   thanks

* :ref:`search`
  
  search the documentation

* :ref:`genindex`

  all functions, classes, terms

* :ref:`modindex`

  quick access to all documented modules

Get berryMQ
===========

If you use python, you can install via easy_install

.. code-block:: bash

   $ sudo easy_install berrymq

If you want to install Ruby version, download source code from bitbucket. And then unzip and type on your console:

.. code-block:: bash

   $ ruby setup.rb config
   $ sudo ruby setup.rb install

.. note::

   Gem package will be created ASAP.

The all files are in a Mercurial repository at http://bitbucket.org/shibu/berrymq/



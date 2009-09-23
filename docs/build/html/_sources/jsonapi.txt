====================
JSON-RPC backend API
====================

berryMQ uses JSON-RPC as a communication protocol.
Following class implements JSON-RPC interface.

.. currentmodule:: berrymq

.. class:: TransporterReceiver

   .. method:: connect_interactively(url, ttl)

      Connect to other node equality. 
      This is :ref:`inter-process style01 <inter_process_style01>`.

      Once you call this function, this node will callback to ``url``.

      :param url: client url
      :type  url: str
      :param ttl: if client haven't sent for this term, connection goes dead.
      :type  ttl: int
      :return: token
      :rtype: str

   .. method:: connect_oneway(ttl)

      Connect to other node. Target node won't call back to client.
      This is :ref:`inter-process style02 <inter_process_style02>`.

      :param ttl: if client haven't sent for this term, connection goes dead.
      :type  ttl: int
      :return: token
      :rtype: str

   .. method:: connect_via_queue(url, identifier, ttl)

      Connect to other node with queue. 
      This is :ref:`inter-process style03 <inter_process_style03>`.

      :param url: client url
      :type  url: str
      :param identifier: receive filter. see :ref:`identifier`
      :type  identifier: str
      :param ttl: if client haven't sent for this term, connection goes dead.
      :type  ttl: int
      :return: token
      :rtype: str

   .. method:: send_message(token, identifier, args, kwargs)

      It's key function for inter-process communication.

      :param token: return value of connection methods
      :type  token: str
      :param identifier: message identifier
      :type  identifier: str
      :param args: message args
      :type  args: list
      :param kwargs: message keyword args
      :type  kwargs: dict

      :return: status code
      :rtype: "ok" or "invalid token" or "timeout"

   .. method:: get(token, block, timeout):
   
      Get message from queue. 
      This function is available if you connect by :meth:`connect_via_queue`.

      .. seealso:: :meth:`berrymq.Queue.get`

      :return: message object or error code
      :rtype:  {id, args, kwargs} or "invalid token" or "timeout"

   .. method:: get_nowait(token)

      .. seealso:: :meth:`berrymq.Queue.get_nowait`

      :return: message object or error code
      :rtype:  {id, args, kwargs} or "invalid token" or "timeout"

   .. method:: close(token)

      close session.

      :param token: return value of connection methods
      :type  token: str

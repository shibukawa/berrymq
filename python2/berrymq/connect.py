import time
import uuid
import berrymq
import jsonrpc.client
import jsonrpc.server


class Timeout(object):
    def __init__(self, token):
        self.token = token


class UnInitializedServer(RuntimeError): pass


class AlreadyConnected(RuntimeError): pass


class NotConnectToServer(RuntimeError): 
    """This node has never been initialized as client"""
    pass


class UnAvialbleFunction(RuntimeError):
    """get(), get_nowait() are available if style03 client."""
    pass


class Connection(object):
    """This supports type02 connection and base class of other class.
    
    This object is used only client side.
    """
    def __init__(self, ttl=None):
        self.last_access = time.time()
        self.token = str(uuid.uuid1())
        self.ttl = ttl
        self.proxy = None
        self.url = None

    def connect(self, url):
        """This method is called at client side."""
        self.url = url
        self.proxy = jsonrpc.client.ServerProxy(url)
        self.token = self.proxy.connect_oneway(self.ttl)
        return self.token

    def check_ttl(self):
        if not self.ttl:
            return
        now = time.time()
        if now - self.last_access > self.ttl:
            raise Timeout(self.token)
        self.last_access = now


class InteractiveConnection(Connection):
    """This class supports type01 connection.
    
    This object is used both client and server sides.
    """
    __metaclass__ = berrymq.Follower
    def __init__(self, url, ttl):
        super(InteractiveConnection, self).__init__(ttl)
        self.proxy = jsonrpc.client.ServerProxy(url)

    def connnect(self, url):
        """This method is called at client side."""
        self.token = self.proxy.connect_interactively(url, self.ttl)
        return self.token

    @berrymq.following("*:*")
    def sender(self, message):
        self.check_ttl()
        self.proxy.send_message(self.token, message.id, message.args, 
                                message.kwargs)


class QueueConnection(Connection):
    """This class supports type03 server side connection"""
    def __init__(self, identifier, ttl):
        super(QueueConnection, self).__init__(ttl)
        self.queue = berrymq.Queue(identifier)

    def receive_get_request(self, block, timeout):
        self.check_ttl()
        return self.queue.get(block, timeout)

    def receive_get_nowait(self):
        self.check_ttl()
        return self.queue.get_nowait()


class QueueClientConnection(Connection):
    """This class supports type03 client side connection"""
    def __init__(self, ttl):
        super(QueueConnection, self).__init__(ttl)

    def connect(self, url, identifier):
        """This method is called at client side"""
        self.proxy = jsonrpc.client.ServerProxy(url)
        self.token = self.proxy.connect_via_queue(url, identifier, self.ttl)
        return self.token

    def send_get(self, block, timeout):
        return self.proxy.get(self.token, block, timeout)

    def send_get_nowait(self):
        return self.proxy.get_nowait(self.token)


class ExportedFunctions(object):
    """Exported JSON-RPC Server"""
    def connect_interactively(self, url, ttl):
        return ConnectionPoint.append(InteractiveConnection(url, ttl))

    def connect_oneway(self, ttl=1000):
        return ConnectionPoint.append(Connection(ttl))

    def connect_via_queue(self, identifier, ttl=1000):
        return ConnectionPoint.append(QueueConnection(identifier, ttl))

    def close_connection(self, token, url=None):
        return "ok"

    def send_message(self, token, identifier, args, kwargs):
        return ConnectionPoint.receive_message(token, identifier, args, kwargs)

    def get(self, token, block, timeout):
        return ConnectionPoint.receive_get(token, block, timeout)

    def get_nowait(self, token):
        return ConnectionPoint.receive_get(token, False, 0)

    def _twitter_to_other_process(self, id_obj, args, kwargs):
        for server in self.servers.itervalues():
            server.send_twitter(id_obj.id_str(), args, kwargs)
        return True


class ConnectionPoint(object):
    """This class manage network connection.
    """
    _server = None
    _connections = {}
    _url_to_token = {}
    _client_token = None

    @classmethod
    def init(cls, host, port):
        if self._server:
            raise RuntimeError("server is already initialized")
        cls._server = jsonrpc.server.SimpleJSONRPCServer((host, port))
        cls._server.register_instance(ExportedFunctions())
        cls._server.serve_forever(in_thread=True)
        berrymq.RootTransporter._connections = cls

    @classmethod
    def append(cls, connection, client=False):
        """Regist connection information.

        This method is work at both side of client and server.
        If you run this server at client side, turn on client parameter.

        @param connection: Connection information
        @type  connection: a kind of Connection's instance
        @param client: set True if this node is client
        @type  client: bool
        @return: token
        @rtype:  str
        """
        if client:
            if cls._client_token:
                raise UnInitializedServer()
            cls._client_token = connection.token
        cls._connections[connection.token] = connection
        if connection.url:
            cls._url_to_token[connection.url] = connection.token
        return connection.token

    @classmethod
    def remove_connection(cls, url):
        token = cls._url_to_token.get(url)
        if token:
            del cls._url_to_token[url]
            del cls._connections[token]

    @classmethod
    def close(cls):
        cls._server.shutdown()
        cls._server = None
        cls._connections = {}
        cls._url_to_token = {}
        berrymq.RootTransporter._connections = None

    @classmethod
    def send_message(cls, identifier, args, kwargs):
        if not self._client_token:
            raise NotConnectToServer()
        connection = self._connections[self._client_token]

    @classmethod
    def forward_message(cls, identifier, args, kwargs):
        """Forward message to style01 connection clients/server"""
        pass

    @classmethod
    def send_get(cls, block, timeout):
        if not self._client_token:
            raise NotConnectToServer()

    @classmethod
    def send_get_nowait(cls):
        if not self._client_token:
            raise NotConnectToServer()

    @classmethod
    def receive_get(cls, token, block, timeout):
        connection = cls._connections.get(token)
        if not isinstance(connection, QueueConnection):
            return "invalid token"
        try:
            connection.check_ttl()
        except Timeout, e:
            del cls._connections[e.token]
            return "timeout"
        message = connection.queue.get(block, timeout)
        return [message.id, message.args, message.kwargs]

    @classmethod
    def receive_message(cls, token, identifier, args, kwargs):
        connection = cls._connections.get(token)
        if connection is None:
            return "invalid token"
        try:
            connection.check_ttl()
        except Timeout, e:
            del self.connections[e.token]
            return "timeout"
        id_obj = berrymq.Identifier(identifier)
        berrymq.RootTransporter.twitter_local(id_obj, args, kwargs)
        return "ok"


# berryMQ API


def init_connection(host="localhost", port=0):
    ConnectionPoint.Init(host, port)


def connect_interactively(url, ttl=1000):
    connection = InteractiveConnection(url, ttl)
    connection.connect()
    ConnectionPoint.append(connection, client=True)


def connect_oneway(url, ttl=1000):
    connection = Connection(url, ttl)
    token = connection.connect()
    ConnectionPoint.append(connection, client=True)


def connect_via_queue(url, identfier, ttl=1000):
    connection = QueueConnection(url, identifier, ttl)
    token = connection.connect()
    ConnectionPoint.append(connection, client=True)


def send_message(identifier, *args, **kwargs):
    ConnectionPoint.send_message(identifier, args, kwargs)


def get(block=True, timeout=0):
    ConnectionPoint.send_get(block, timeout)


def get_nowait():
    ConnectionPoint.send_get_nowait()


def close_connection(url=None):
    if url:
        ConnectionPoint.remove_connection(url)
    else:
        ConnectionPoint.close()




import time
import uuid
from . import berrymq
from .jsonrpc import client
from .jsonrpc import server


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
    def __init__(self, ttl=None, client=False):
        self.last_access = time.time()
        self.token = None
        self.ttl = ttl
        self.proxy = None
        self.addr = None
        self.client = client
        
    def _generate_token(self):
        return str(uuid.uuid1())

    def connect(self, addr):
        """This method is called at client side."""
        self.addr = addr
        self.proxy = client.ServerProxy("http://%s:%d" % addr)
        self.token = self.proxy.connect_oneway(self.ttl)
        return self.token

    def check_ttl(self):
        if not self.ttl:
            return
        now = time.time()
        if now - self.last_access > self.ttl:
            raise Timeout(self.token)
        self.last_access = now

    def send_message(self, identifier, args, kwargs):
        if self.proxy is not None and self.client:
            self.proxy.send_message(self.token, identifier, args, kwargs)

    def forward_message(self, identifier, args, kwargs):
        pass


class Interconnection(Connection):
    """This class supports type01 connection.
    
    This object is used both client and server sides.
    """
    def __init__(self, ttl, client=False):
        super(Interconnection, self).__init__(ttl, client)

    def connect_at_client(self, addr):
        """This method is called at client side."""
        self.addr = addr
        self.token = self._generate_token()
        self.proxy = client.ServerProxy("http://%s:%d" % addr)
        my_addr = ConnectionPoint.get_addr()
        self.proxy.interconnect(my_addr, self.token, self.ttl)

    def connect_at_server(self, addr, token):
        self.addr = addr
        self.proxy = client.ServerProxy("http://%s:%d" % addr)
        self.token = token

    def forward_message(self, identifier, args, kwargs):
        if self.proxy is not None:
            self.proxy.send_message(self.token, identifier, args, kwargs)

    def send_message(self, identifier, args, kwargs):
        pass


class QueueConnection(Connection):
    """This class supports type03 server side connection"""
    def __init__(self, identifier, ttl):
        super(QueueConnection, self).__init__(ttl, client=False)
        self.queue = berrymq.Queue(identifier)
        self.token = self._generate_token()

    def receive_get_request(self, block, timeout):
        self.check_ttl()
        return self.queue.get(block, timeout)

    def receive_get_nowait(self):
        self.check_ttl()
        return self.queue.get_nowait()

    def send_message(self, identifier, args, kwargs):
        pass


class QueueClientConnection(Connection):
    """This class supports type03 client side connection"""
    def __init__(self, ttl):
        super(QueueClientConnection, self).__init__(ttl, client=True)

    def connect(self, addr, identifier):
        """This method is called at client side"""
        url = "http://%s:%d" % addr
        self.proxy = client.ServerProxy(url)
        self.token = self.proxy.connect_via_queue(identifier, self.ttl)
        self.addr = addr
        return self.token

    def send_get(self, block, timeout):
        return self.proxy.get(self.token, block, timeout)

    def send_get_nowait(self):
        return self.proxy.get_nowait(self.token)


class ExportedFunctions(object):
    """Exported JSON-RPC Server"""
    def interconnect(self, addr, his_token, ttl):
        connection = Interconnection(ttl, client=False)
        connection.connect_at_server(tuple(addr), his_token)
        return ConnectionPoint.append(connection)

    def connect_oneway(self, ttl=1000):
        return ConnectionPoint.append(Connection(ttl))

    def connect_via_queue(self, identifier, ttl):
        return ConnectionPoint.append(QueueConnection(identifier, ttl))

    def close_connection(self, token, addr=None):
        """
        :todo: implement
        """
        return "ok"

    def send_message(self, token, identifier, args, kwargs):
        return ConnectionPoint.receive_message(token, identifier, args, kwargs)

    def get(self, token, block, timeout):
        return ConnectionPoint.receive_get(token, block, timeout)

    def get_nowait(self, token):
        return ConnectionPoint.receive_get(token, False, 0)

    def __twitter_to_other_process(self, id_obj, args, kwargs):
        for server in self.servers.itervalues():
            server.send_twitter(id_obj.id_str(), args, kwargs)
        return True


class ConnectionPoint(object):
    """This class manage network connection.
    """
    _server = None
    _addr = None
    _connections = {}
    _url_to_token = {}

    @classmethod
    def init(cls, addr):
        if cls._server:
            raise RuntimeError("server is already initialized")
        cls._server = server.SimpleJSONRPCServer(addr)
        cls._server.register_instance(ExportedFunctions())
        cls._server.serve_forever(in_thread=True)
        cls.regist_exchanger()
        cls._addr = addr
        
    @classmethod
    def get_addr(cls):
        if cls._addr is None:
            raise RuntimeError("Please call init_connection() first.")
        return cls._addr

    @classmethod
    def regist_exchanger(cls):
        berrymq.RootTransporter._connections = cls

    @classmethod
    def clear_exchanger(cls):
        berrymq.RootTransporter._connections = None

    @classmethod
    def append(cls, connection):
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
        cls._connections[connection.token] = connection
        if connection.addr:
            cls._url_to_token[connection.addr] = connection.token
        return connection.token

    @classmethod
    def _allow_token(cls, token):
        """test method"""
        cls._connections[token] = "test"

    @classmethod
    def remove_connection(addr, url):
        token = cls._url_to_token.get(addr)
        if token:
            del cls._url_to_token[addr]
            del cls._connections[token]

    @classmethod
    def close(cls):
        if cls._server is not None:
            cls._server.shutdown()
        cls._server = None
        cls._connections = {}
        cls._url_to_token = {}
        cls.clear_exchanger()

    @classmethod
    def send_message(cls, identifier, args, kwargs):
        for connection in cls._connections.values():
            connection.send_message(identifier, args, kwargs)

    @classmethod
    def forward_message(cls, identifier, args, kwargs, except_token=None):
        """Forward message to style01 connection clients/server
        @todo: ttl check
        """
        for token, connection in cls._connections.items():
            if token == except_token:
                continue
            connection.forward_message(identifier, args, kwargs)

    @classmethod
    def send_get(cls, block, timeout):
        for connection in cls._connections.values():
            if isinstance(connection, QueueClientConnection):
                idstr, args, kwargs = connection.send_get(block, timeout)
                return berrymq.Message(berrymq.Identifier(idstr), 
                                       args, kwargs, 100)
        raise NotConnectToServer()

    @classmethod
    def receive_get(cls, token, block, timeout):
        connection = cls._connections.get(token)
        if not isinstance(connection, QueueConnection):
            return "invalid token"
        try:
            connection.check_ttl()
        except Timeout as e:
            del cls._connections[e.token]
            return "timeout"
        message = connection.queue.get(block, timeout)
        return [message.id, message.args, message.kwargs]

    @classmethod
    def receive_message(cls, token, identifier, args, kwargs):
        connection = cls._connections.get(token)
        if connection is None:
            return "invalid token"
        elif isinstance(connection, Connection):
            try:
                connection.check_ttl()
            except Timeout as e:
                del self.connections[e.token]
                return "timeout"
        id_obj = berrymq.Identifier(identifier)
        berrymq.RootTransporter.twitter_local(id_obj, args, kwargs)
        cls.forward_message(identifier, args, kwargs, token)
        return "ok"


# berryMQ API


def init_connection(addr=("localhost", 0)):
    ConnectionPoint.init(addr)


def interconnect(addr, ttl=1000):
    connection = Interconnection(ttl, client=True)
    connection.connect_at_client(addr)
    ConnectionPoint.append(connection)


def connect_oneway(addr, ttl=1000):
    connection = Connection(ttl, client=True)
    connection.connect(addr)
    ConnectionPoint.append(connection)


def connect_via_queue(addr, identifier, ttl=1000):
    connection = QueueClientConnection(ttl)
    token = connection.connect(addr, identifier)
    ConnectionPoint.append(connection)


def send_message(identifier, *args, **kwargs):
    ConnectionPoint.send_message(identifier, args, kwargs)


def get(block=True, timeout=1000):
    return ConnectionPoint.send_get(block, timeout)


def get_nowait():
    return ConnectionPoint.send_get(block=False, timeout=0)


def close_connection(url=None):
    if url:
        ConnectionPoint.remove_connection(url)
    else:
        ConnectionPoint.close()

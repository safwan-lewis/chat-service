import asyncio

class ChatServerProtocol(asyncio.Protocol):
    clients={}

    def __init__(self):
        pass

    def connection_made(self, transport: asyncio.Transport):
        """Called on new client connections"""
        self._remote_addr = transport.get_extra_info('peername')
        print('[+] client {} connected.'.format(self._remote_addr))
        self._transport = transport
        ChatServerProtocol.clients[transport] = self._remote_addr


    def data_received(self, data):
        """Handle data"""
        pass

    def connection_lost(self, exc):
        """remote closed connection"""
        print('[-] lost connectio to {}'.format(ChatServerProtocol.clients[self._transport]))
        self._transport.close()

class ChatServer:
    LOCAL_HOST = '0.0.0.0'
    def __init__(self, port):
        self._port: int = port

    def listen(self):
        """start listening"""
        pass

    def start(self):
        """start"""
        loop = asyncio.get_event_loop()
        server_coro = loop.create_server(lambda : ChatServerProtocol(),
                                 host=ChatServer.LOCAL_HOST,
                                 port=self._port)

        loop.run_until_complete(server_coro)
        loop.run_forever()


if __name__ == '__main__':
    chat_server = ChatServer(port=8080)
    chat_server.start()
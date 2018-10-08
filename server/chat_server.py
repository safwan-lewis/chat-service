import asyncio

class ChatServerProtocol(asyncio.Protocol):
    # master dict {transport: {'remote': ('127.0.0.1', 76678), 'login-name': 'omari'}
    clients={}

    def __init__(self):
        self._pieces = []

    def _handle_command(self):
        command = ''.join(self._pieces)
        self._pieces = []
        if command.startswith('/lru'):
            #get list of registered users
            lru = [r['login-name'] for r in ChatServerProtocol.clients.values() if r['login-name']]
            response = '/lru '
            for user in lru:
                response += (f'{user}, ')

            response.rstrip(', ')
            response = ''.join([response, '$'])
            self._transport.write(response.encode('utf-8'))

        if command.startswith('/login '):
            #TODO: check if login-name already exists

            login_name = command.lstrip('/login').rstrip('$')
            client_record = ChatServerProtocol.clients[self._transport]
            client_record['login-name'] = login_name

            response = '/login success$'
            self._transport.write(response.encode('utf-8'))


    def connection_made(self, transport: asyncio.Transport):
        """Called on new client connections"""
        self._remote_addr = transport.get_extra_info('peername')
        print('[+] client {} connected.'.format(self._remote_addr))
        self._transport = transport
        ChatServerProtocol.clients[transport] = {'remote': self._remote_addr, 'login-name': None}


    def data_received(self, data):
        """Handle data"""
        self._pieces.append(data.decode('utf-8'))
        if ''.join(self._pieces).endswith('$'):

            self._handle_command()


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
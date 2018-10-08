import asyncio
import threading

class NotConnectedError(Exception):
    pass

class LoginError(Exception):
    pass

class ChatClientProtocol(asyncio.Protocol):
    def __init__(self):
        self._pieces = []
        self._responses_q = asyncio.Queue(10)

    def connection_made(self, transport: asyncio.Transport):
        self._transport = transport

    def data_received(self, data):
        self._pieces.append(data.decode('utf-8'))

        if ''.join(self._pieces).endswith('$'):
            asyncio.ensure_future(self._responses_q.put(''.join(self._pieces).rstrip('$')))
            self._pieces = []

    def connection_lost(self, exc):
        self._transport.close()

class ChatClient:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._connected = False

    def disconnect(self):
        if not self._connected:
            raise NotConnectedError()

        self._transport.close()

    async def _connect(self):
        try:
            loop = asyncio.get_event_loop()
            self._transport, self._protocol = await loop.create_connection(
                lambda: ChatClientProtocol(),
                self._ip,
                self._port)

            self._connected = True
            print('connected to chat server')

        except ConnectionRefusedError:
            print('error connecting to chat server - connection refused')

        except TimeoutError:
            print('error connecting to chat server - connection timeout')

        except Exception as e:
            print('error connecting to chat server - fatal error')

    def connect(self):
        loop = asyncio.get_event_loop()
        try:
            asyncio.ensure_future(self._connect())

            loop.run_forever()
        except Exception as e:
            print(e)
        finally:
            print('{} - closing main event loop'.format(threading.current_thread().getName()))
            loop.close()

    async def lru(self):
        self._transport.write('/lru$'.encode('utf-8'))
        # await for response message from server
        lru_response = await self._protocol._responses_q.get()

        #unmarshel into list of registered users
        #/lru omari, nick, tom
        users = lru_response.lstrip('/lru ').split(', ')
        return users

    async def login(self, login_name):
        self._transport.write('/login {}$'.format(login_name).encode('utf-8'))
        login_response = await self._protocol._responses_q.get()
        success = login_response.lstrip('/login ')

        if success != 'success':
            raise LoginError()


if __name__ == '__main__':
    LOCAL_HOST = '127.0.0.1'
    PORT = 8080

    loop = asyncio.get_event_loop()
    chat_client = ChatClient(LOCAL_HOST, PORT)
    asyncio.ensure_future(chat_client._connect())


    chat_client.disconnect()

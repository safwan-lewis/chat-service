import aioconsole
import asyncio
import click
from remote_apis.tcp_api.tcp_server import TCPChatServer
from server.chat_server import ChatServer
from remote_apis.rest_api.rest_app import RestApp
from client.chat_client import (
    ChatClient,
    NotConnectedError,
    LoginConflictError,
    LoginError
)
from twitter.blk_client import TwitterDMClient

consumer_key = 'ew0pdIp6isx0OxnRsLuTdgRMp'
consumer_secret = 'YZNBeCwQOIZqj7dAgTmFykcwNWyTaf0QYYto6FgcEcRhafpcS9'
access_token = '4027843701-Fqs7VUBD6KQsjT8cwDfgrVhlh54ivS2FHLefAa5'
access_secret = 'mfMffOsw80FLx8KPjplogfytkBdE2KABGOeb656eKdAyT'


async def display_msgs(chat_client):
    while True:
        msg = await chat_client.get_user_msg()
        print('\n\n\t\tRECEIVED MESSAGE: {}'.format(msg))


async def handle_user_input(chat_client, twitter_client, loop):
    while True:
        print('\n\n')
        print('< 1 > closes connection and quits')
        print('< 2 > list logged-in users')
        print('< 3 > login')
        print('< 4 > list rooms')
        print('< 5 > post message to a room')
        print('< 6 > get twitter direct messages')

        print('\tchoice: ', end='', flush=True)

        command = await aioconsole.ainput()
        if command == '1':
            # disconnect
            try:
                chat_client.disconnect()
                print('disconnected')
                loop.stop()
            except NotConnectedError:
                print('client is not connected ...')
            except Exception as e:
                print('error disconnecting {}'.format(e))

        elif command == '2':  # list registered users
            users = await chat_client.lru()
            print('logged-in users: {}'.format(', '.join(users)))

        elif command == '3':
            login_name = await aioconsole.ainput('enter login-name: ')
            try:
                await chat_client.login(login_name)
                print(f'logged-in as {login_name}')

            except LoginConflictError:
                print('login name already exists, pick another name')
            except LoginError:
                print('error loggining in, try again')

        elif command == '4':
            try:
                rooms = await chat_client.lrooms()
                for room in rooms:
                    print('\n\t\troom name ({}), owner ({}): {}'.format(room['name'], room['owner'], room['description']))

            except Exception as e:
                print('error getting rooms from server {}'.format(e))

        elif command == '5':
            try:

                user_message = await aioconsole.ainput('enter your message: ')
                await chat_client.post(user_message, 'public')

            except Exception as e:
                print('error posting message {}'.format(e))

        elif command == '6':
            try:
                for msg in twitter_client.list_dms():
                    print(msg)

            except Exception as e:
                print('error getting direct messages {}'.format(e))


@click.group()
def cli():
    pass


@cli.command(help="run chat client")
@click.argument("host")
@click.argument("port", type=int)
def connect(host, port):
    chat_client = ChatClient(ip=host, port=port)
    loop = asyncio.get_event_loop()

    loop.run_until_complete(chat_client._connect())

    twitter_blk_client = TwitterDMClient(consumer_key=consumer_key,
                                         consumer_secret=consumer_secret,
                                         access_token=access_token,
                                         access_secret=access_secret)
    try:
        twitter_blk_client.init_auth()
    except Exception as e:
        print('error authenticating with twitter API: {}'.format(e))
        # sys.exit(1)

    # display menu, wait for command from user, invoke method on client
    asyncio.ensure_future(handle_user_input(chat_client=chat_client, twitter_client = twitter_blk_client, loop=loop))
    asyncio.ensure_future(display_msgs(chat_client=chat_client))

    loop.run_forever()


@cli.command(help='run chat server')
@click.argument('port', type=int)
def listen(port):
    loop = asyncio.get_event_loop()
    chat_server = ChatServer()
    tcp_api = TCPChatServer(port=port, chat_server=chat_server, loop=loop)
    rest_app = RestApp(chat_server=chat_server, port=8081, loop=loop)
    rest_app.start()
    tcp_api.start()
    loop.run_forever()


if __name__ == '__main__':
    cli()

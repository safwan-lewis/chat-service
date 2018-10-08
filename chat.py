import aioconsole
import asyncio
import click
from server.chat_server import ChatServer
from client.chat_client import (
    ChatClient,
    NotConnectedError,
    LoginConflictError,
    LoginError
)


async def handle_user_input(chat_client, loop):
    while True:
        print('\n\n')
        print('< 1 > closes connection and quits')
        print('< 2 > list logged-in users')
        print('< 3 > login')
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
            print(users)

        elif command == '3':
            login_name = await aioconsole.ainput('enter login-name')
            try:
                await chat_client.login(login_name)
                print(f'logged-in as {login_name}')

            except LoginConflictError:
                print('login name already exists, pick another name')
            except LoginError:
                print('error loggining in, try again')


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

    # display menu, wait for command from user, invoke method on client
    asyncio.ensure_future(handle_user_input(chat_client=chat_client, loop=loop))

    loop.run_forever()


@cli.command(help='run chat server')
@click.argument('port', type=int)
def listen(port):
    click.echo('starting chat server at {}'.format(port))
    chat_server = ChatServer(port=port)
    chat_server.start()


if __name__ == '__main__':
    cli()

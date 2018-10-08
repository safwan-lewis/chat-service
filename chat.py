import aioconsole
import asyncio
import click
from server.chat_server import ChatServer
from client.chat_client import ChatClient, NotConnectedError

async def handle_user_input(chat_client):
    while True:
        print('< 1 > disconnect')
        print('< 2 > list logged-in users')
        print('< 3 > login')

        command = await aioconsole.ainput()
        if command == '1':
            #disconnect
            try:
                chat_client.disconnect()
                print('disconnected')
            except NotConnectedError:
                print('client is not connected ...')
            except Exception as e:
                print('error disconnecting {}'.format(e))
        elif command == '2': #list registered users
            users = await chat_client.lru()
            print(users)

        elif command == '3':
            login_name = await aioconsole.ainput('enter login-name')
            try:
                await chat_client.login(login_name)
            except:
                print('error loggining in')


@click.group()
def cli():
    pass

@cli.command(help = "run chat client")
@click.argument("host")
@click.argument("port", type=int)
def connect(host, port):
    chat_client = ChatClient(ip = host, port=port)
    loop = asyncio.get_event_loop()

    asyncio.ensure_future(chat_client._connect())

    # display menu, wait for command from user, invoke method on client
    asyncio.ensure_future(handle_user_input(chat_client=chat_client))

    loop.run_forever()

@cli.command(help='run chat server')
@click.argument('port', type=int)
def listen(port):
    click.echo('starting chat server at {}'.format(port))
    chat_server = ChatServer(port=port)
    chat_server.start()


if __name__ == '__main__':
    cli()

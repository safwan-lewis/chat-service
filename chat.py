import aioconsole
import asyncio
import click
from server.chat_server import ChatServer
from client.chat_client import ChatClient, NotConnectedError

async def handle_user_input(chat_client):
    while True:
        print('1- enter for disconnect')
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


@click.group()
def cli():
    pass

@cli.command(help = "run chat client")
@click.argument("host")
@click.argument("port", type=int)
def connect(host, port):
    click.echo('connect to chat server at {}:{}'.format(host, port))
    chat_client = ChatClient(ip = host, port=port)
    # display menu, wait for command from user, invoke method on client

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(chat_client._connect())
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

import threading
import asyncio
import os
from unity_socket_server import UnitySocketServer
from common.dbms import DBMS
from common.discord_bot import DiscordBot

# Constants for configuration
IP = "0.0.0.0"
SOCKET = 65432
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

"""Initialize all the components for the server."""


async def start():
    # Database Management System
    dbms_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    dbms = DBMS(dbms_url)

    discord_bot = DiscordBot(DISCORD_TOKEN, "!", dbms)

    unity_socket_server = UnitySocketServer(IP, SOCKET, dbms, discord_bot)

    server_coroutine = asyncio.start_server(
        unity_socket_server.create_client,
        unity_socket_server.host,
        unity_socket_server.port
    )
    server = asyncio.run(server_coroutine)
    await server.serve_forever()

asyncio.run(start())
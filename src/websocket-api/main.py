import socket
import asyncio
import os
from websocket_server import WebSocketServer
from vuejs_socket_server import VuejsSocketServer
from common.dbms import DBMS

# Constants for configuration
IP = "0.0.0.0"
SOCKET = 65433
POSTGRES_HOST = 'localhost'#os.getenv("POSTGRES_HOST")
POSTGRES_USER = 'postgres'#os.getenv("POSTGRES_USER")
POSTGRES_DB = 'postgres'#os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = 'postgres'#os.getenv("POSTGRES_PASSWORD")

"""Initialize all the components for the server."""

print("Starting websocket api", flush=True)

async def start():
    # Database Management System
    dbms_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    print(f"Connecting to {dbms_url}")

    unity_socket_server = WebSocketServer(IP, SOCKET, DBMS(dbms_url))
    vuejs_socket_server = VuejsSocketServer(DBMS(dbms_url), unity_socket_server)

    async def start_tcp_server():
        server = await asyncio.start_server(
            unity_socket_server.handle_client,
            unity_socket_server.host,
            unity_socket_server.port
        )
        print("Serving on", server.sockets[0].getsockname())
        # also run in background unity_socket_server.check_lifes()
        asyncio.create_task(unity_socket_server.check_lifes())
        await server.serve_forever()

    await vuejs_socket_server.run_async()
    await start_tcp_server()


asyncio.run(start())

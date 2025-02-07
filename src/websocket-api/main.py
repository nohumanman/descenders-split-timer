import socket
import asyncio
import os
from unity_socket_server import UnitySocketServer
from common.dbms import DBMS

# Constants for configuration
IP = "0.0.0.0"
SOCKET = 65432
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

"""Initialize all the components for the server."""

print("Starting websocket api", flush=True)

# if another process running on SOCKET then quit
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((IP, SOCKET))
    except socket.error as e:
        print(f"Socket {SOCKET} is already in use. Exiting.")
        exit(1)

async def start():
    # Database Management System
    dbms_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    print(f"Connecting to {dbms_url}")
    dbms = DBMS(dbms_url)
    if not (await dbms.db_connected()):
        print("Failed to connet to database!")
        exit(1)

    unity_socket_server = UnitySocketServer(IP, SOCKET, dbms)
    
    server = await asyncio.start_server(
        unity_socket_server.create_client,
        unity_socket_server.host,
        unity_socket_server.port
    )
    print(f"Launching asyncio server on {IP}:{SOCKET}")
    async with server:
        await server.serve_forever()

asyncio.run(start())

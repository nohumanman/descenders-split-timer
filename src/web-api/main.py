""" Main.py for web-api"""
import threading
import asyncio
import os
from webserver import Webserver
from common.dbms import DBMS

# Constants for configuration
WEBSITE_IP = "0.0.0.0"
WEBSITE_PORT = 8082
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

"""Initialize all the components for the server."""
# Database Management System
dbms_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
dbms = DBMS(dbms_url)

webserver = Webserver(dbms)

webserver_app = webserver.webserver_app

def run_server_in_thread():
    # if no event loop, create one
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    threading.Thread(target=asyncio.get_event_loop().run_forever).start()
    print(f"Server available from http://localhost:{WEBSITE_PORT}/")
    webserver.webserver_app.run(
        WEBSITE_IP, port=WEBSITE_PORT
    )

if __name__ == "__main__":
    run_server_in_thread()

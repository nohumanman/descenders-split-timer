import os
import logging
import threading
import asyncio
from unity_socket_server import UnitySocketServer
from discord_bot import DiscordBot
from tokens import DISCORD_TOKEN
from webserver import Webserver
from dbms import DBMS

# Constants for configuration
UNITY_SOCKET_IP = "0.0.0.0"
UNITY_SOCKET_PORT = 65432
WEBSITE_IP = "0.0.0.0"
WEBSITE_PORT = 8082
WEBSITE_SOCKET_IP = "0.0.0.0"
WEBSITE_SOCKET_PORT = 65430
LOG_FILE = "modkit.log"

# Setup logging configuration
def setup_logging():
    """Setup logging for the server."""
    logging.basicConfig(
        level=logging.WARNING,
        format=(
            '%(asctime)s - %(name)s\t - %(levelname)s\t'
            ' - %(filename)s\t - Line %(lineno)d:\t %(message)s'
        ),
        filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), LOG_FILE)
    )

# Initialize and configure necessary components
def initialize_components():
    """Initialize all the components for the server."""
    # Database Management System
    dbms = DBMS("postgresql+asyncpg://postgres:postgres@postgres/postgres")

    # Unity Socket Server
    unity_socket_server = UnitySocketServer(UNITY_SOCKET_IP, UNITY_SOCKET_PORT, dbms)

    # Webserver and Discord Bot
    webserver = Webserver(unity_socket_server, dbms)
    discord_bot = DiscordBot(DISCORD_TOKEN, "!", unity_socket_server, dbms)

    # Assign discord bot to both Unity Socket Server and Webserver
    unity_socket_server.discord_bot = discord_bot
    webserver.discord_bot = discord_bot

    return unity_socket_server, webserver, discord_bot, dbms

# Start Unity Socket Server coroutine
def start_unity_socket_server(unity_socket_server):
    """Start the Unity Socket Server coroutine."""
    server_coroutine = asyncio.start_server(
        unity_socket_server.create_client,
        unity_socket_server.host,
        unity_socket_server.port
    )
    asyncio.get_event_loop().run_until_complete(server_coroutine)
    asyncio.get_event_loop().create_task(unity_socket_server.riders_gate())

# Start the webserver and Discord bot in a separate thread
def run_server_in_thread(webserver):
    """Run the server in a separate thread."""
    threading.Thread(target=asyncio.get_event_loop().run_forever).start()
    print(f"Server available from https://localhost:{WEBSITE_PORT}/")
    webserver.webserver_app.run(
        WEBSITE_IP, port=WEBSITE_PORT,
        debug=False, ssl_context='adhoc'
    )

# Main entry point
def main():
    """Main function to set up and run the server."""
    # Set the working directory to the script path
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Setup logging
    #setup_logging()

    # Initialize components
    unity_socket_server, webserver, discord_bot, dbms = initialize_components()

    # Start Unity Socket Server
    start_unity_socket_server(unity_socket_server)

    # Run the webserver in a separate thread
    run_server_in_thread(webserver)

# Entry point to execute the script
if __name__ == "__main__":
    main()

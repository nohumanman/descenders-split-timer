""" Used to host the socket server. """
from typing import Union
import time
import asyncio
from asyncio import StreamReader, StreamWriter
import logging
from unity_socket import UnitySocket
from common.dbms import DBMS

class PlayerNotFound(Exception):
    """ Exception called when the descenders unity client could not be found """

class DisconnectError(Exception):
    """ Exception called when the descenders unity client disconnects """

class UnitySocketServer():
    """ Used to communicate quickly with the Descenders Unity client. """
    def __init__(self, ip: str, port: int, dbms: DBMS):
        self.host = ip
        self.port = port
        self.dbms = dbms
        self.timeout = 120
        self.read_buffer_size = 100
        self.website_socket_server = None
        self.players: list[UnitySocket] = []

    def delete_player(self, player: UnitySocket):
        """ Deletes the player from the socket server """
        if player not in self.players:
            return # player already deleted
        self.players.remove(player)
        player.writer.close()
        del player

    async def handle_client(self, reader: StreamReader, writer: StreamWriter):
        """ Creates a client from their socket and address """        
        address = writer.get_extra_info('peername')
        player = UnitySocket(address, self, reader, writer)
        self.players.append(player)
        await player.send("SUCCESS")
        try:
            while True:
                # Read the data from the client
                data = await asyncio.wait_for(
                    reader.read(self.read_buffer_size),
                    timeout=self.timeout
                )
                # If no data is received, then the client has disconnected
                if not data:
                    raise DisconnectError("Client disconnected")
                message = data.decode()
                # If message does not end with a newline character, then read more data
                while not message.endswith("\n"):
                    data = await asyncio.wait_for(
                        reader.read(self.read_buffer_size),
                        timeout=self.timeout
                    )
                    message += data.decode()
                # Remove the newline character from the message
                message = message.rstrip("\n")
                # if the message is a heartbeat, then ignore it
                if message == "HEARTBEAT":
                    continue
                asyncio.create_task(player.handle_data(message))
        except asyncio.TimeoutError:
            print(f"Player {player} timed out")
        except DisconnectError as e:
            print(f"Player {player} disconnected")
        finally:
            writer.close()
            await writer.wait_closed()
            self.delete_player(player)

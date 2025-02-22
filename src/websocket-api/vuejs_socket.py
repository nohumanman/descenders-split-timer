""" Used to manipulate socket connection """
import asyncio

operations = {
    "GET_PLAYERS": lambda sock, data: sock.get_players(),
    "GET_PLAYER": lambda sock, data: sock.get_player(data),
}


class VuejsSocket():
    """ Used to handle the connection to the descenders unity client """
    def __init__(self,
            addr,
            parent,
            reader:  asyncio.StreamReader,
            writer: asyncio.StreamWriter,
            dbms
        ):
        self.addr = addr
        self.parent = parent
        self.reader = reader
        self.writer = writer
        self.dbms = dbms
        self.alive = True

    async def send(self, data: str):
        """ Send data to the descenders unity client """
        self.writer.write(data.encode())
        await self.writer.drain()

    async def handle_data(self, data: str):
        """ Handle data sent from the descenders unity client """
        try:
            # Parse the data
            operation_data = data.split("|")
            operation = operation_data[0]
            operands = operation_data[1:]
            # Perform the operation
            if operation not in operations:
                print(f"Operation {operation} not found")
                return
            result = await operations[operation](self, operands)
            # Send the result back to the client
            if result:
                await self.send(result)
        except Exception as e:
            print(f"Error: {e}")

    async def get_players(self):
        """ Get all the players in the database """
        return [{"steam_id": player.steam_id} for player in self.parent.players]
    
    async def get_player(self, data):
        """ Get a specific player from the database """
        return '{PLAYERINFOHERE}'

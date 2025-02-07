import asyncio
from common.dbms import DBMS
from websocket import WebSocket
import time
import socketio
from aiohttp import web

class VuejsSocketServer:
    def __init__(self, dbms: DBMS, web_socket: WebSocket, host='localhost', port=40000):
        self.dbms = dbms
        self.web_socket = web_socket

        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        self.app = web.Application()
        self.sio.attach(self.app)
        self.host = host
        self.port = port

        self.sio.event(self.connect)
        self.sio.event(self.disconnect)
        self.sio.event(self.message)

    async def connect(self, sid, environ):
        print('Client connected:', sid)

    async def disconnect(self, sid):
        print('Client disconnected:', sid)

    async def message(self, sid, data):
        if data == 'get_data':
            data = {
                'total_users_online': len(self.web_socket.players),
                'total_stored_times': await self.dbms.get_total_stored_times(),
                'total_replay_size': 3,
                'times_submitted_past_30_days': await self.dbms.get_total_stored_times(timestamp=time.time()-2592000)
            }
            await self.sio.emit('data_update', data, room=sid)
        if data == 'get_users':
            users = [{
                "steam_id": player.info.steam_id,
                "steam_name": player.info.steam_name,
                "reputation": player.info.reputation,
                "bike_type": player.info.bike_type,
                "world_name": player.info.world_name,
                "last_trick": player.info.last_trick,
                "time_started": player.info.time_started
            } for player in self.web_socket.players]
            await self.sio.emit('users_update', users, room=sid)

    def run(self):
        web.run_app(self.app, host=self.host, port=self.port)

    async def run_async(self):
        # This is to ensure the app is running inside an asyncio loop
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        print(f'Starting server on {self.host}:{self.port}')
        await site.start()

if __name__ == '__main__':
    server = VuejsSocketServer()
    server.run()

from quart import Quart, render_template, websocket


class MyQuart(Quart):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_url_rule("/", "hello", self.hello)
        self.add_url_rule("/api", "json", self.json)
        self.add_websocket("/ws", "ws", self.ws)

    async def hello(self):
        return await render_template("index.html")

    async def json(self):
        return {"hello": "world"}

    async def ws(self):
        while True:
            await websocket.send("hello")
            await websocket.send_json({"hello": "world"})


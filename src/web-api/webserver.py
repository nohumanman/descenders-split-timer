""" Used to host the website using flask """
from typing import TYPE_CHECKING
import os
import time
from datetime import datetime
import logging
import asyncio
from werkzeug.utils import secure_filename

# Flask imports
from quart import (
    Quart,
    session,
    request,
    redirect,
    jsonify,
    send_file
)
from quart_cors import cors

# Authlib imports
from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.base_client import MissingTokenError
from authlib.integrations.base_client.errors import InvalidTokenError

# Database Management System imports
from common.dbms import DBMS

# Tokens imports
from common.tokens import OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET

# Used to fix RuntimeError in using async from thread
import nest_asyncio
nest_asyncio.apply()

if TYPE_CHECKING:
    # Imports related to the Discord bot (if any)
    from common.discord_bot import DiscordBot

OAUTH2_REDIRECT_URI = 'https://modkit.nohumanman.com/callback'
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

'''
routes: /streaming/
/db/
/api/
'''

logging = logging.getLogger('DescendersSplitTimer')

webserver_app = Quart(__name__)

class WebserverRoute():
    """ Used to denote a webserver url to view function """
    def __init__(self, route, endpoint, view_func, methods):
        self.route = route
        self.endpoint = endpoint
        self.view_func = view_func
        self.methods = methods

    def is_valid(self):
        """ Function to check if the route is valid """
        return (
            self.route is not None
            and self.endpoint is not None
            and self.view_func is not None
            and self.methods is not None
        )

    def to_dict(self):
        """ Function to convert the route to a dictionary """
        return {
            "route": self.route,
            "endpoint": self.endpoint,
            "view_func": self.view_func,
            "methods": self.methods
        }

class Webserver():
    """ Used to host the website using flask """
    def __init__(self, dbms : DBMS):
        self.dbms = dbms
        self.webserver_app = webserver_app
        self.webserver_app = cors(self.webserver_app)
        self.webserver_app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
        self.discord_bot: DiscordBot | None = None
        self.routes = [
            WebserverRoute(
                "/callback", "callback",
                self.callback, ["GET"]
            ),
            WebserverRoute(
                "/me", "me",
                self.me, ["GET"]
            ),
            WebserverRoute(
                "/permission", "permission_check",
                self.permission, ["GET"]
            ),
            WebserverRoute(
                "/get-leaderboard", "get_leaderboard",
                self.get_leaderboard_for_trail, ["GET"]
            ),
            WebserverRoute(
                "/leaderboard/<trail>", "get_leaderboard_trail",
                self.get_leaderboard_trail, ["GET"]
            ),
            WebserverRoute(
                "/get-all-times", "get_all_times",
                self.get_all_times, ["GET"]
            ),
            WebserverRoute(
                "/verify_time/<time_id>", "verify_time",
                self.verify_time, ["GET"]
            ),
            WebserverRoute(
                "/login", "login",
                self.login, ["GET"]
            ),
            WebserverRoute(
                "/concurrency", "concurrency",
                self.concurrency, ["GET"]
            ),
            WebserverRoute(
                "/get-trails", "get_trails",
                self.get_trails, ["GET"]
            ),
            WebserverRoute(
                "/get-worlds", "get_worlds",
                self.get_worlds, ["GET"]
            ),
            WebserverRoute(
                "/upload-replay",
                "upload_replay",
                self.upload_replay,
                ["POST"]
            ),
            WebserverRoute(
                "/ignore-time/<time_id>/<value>",
                "ignore_time",
                self.ignore_time,
                ["GET"]
            ),
            WebserverRoute(
                "/get-output-log/<player_id>",
                "get_output_log",
                self.get_output_log,
                ["GET"]
            ),
            WebserverRoute(
                "/static/replays/<time_id>",
                "get_replay",
                self.get_replay,
                ["GET"]
            ),
            WebserverRoute(
                '/get-total-stored-times',
                'get_total_stored_times',
                self.get_total_stored_times,
                ['GET']
            ),
            WebserverRoute(
                '/get-gb-stored-replays',
                'get_gb_stored_replays',
                self.get_gb_stored_replays,
                ['GET']
            ),
        ]
        self.tokens_and_ids = {}
        import asyncio
        asyncio.run(self.add_routes())

    async def add_routes(self):
        """ Adds the routes to the flask app """
        for route in self.routes:
            self.webserver_app.add_url_rule(
                route.route,
                    endpoint=route.endpoint,
                view_func=route.view_func,
                methods=route.methods
            )

    async def get_gb_stored_replays(self):
        """Get the file size of replays in GB """
        return str(round(sum(
            os.path.getsize(f"replays/{f}")
            for f in os.listdir("replays")
        ) / 1_000_000_000, 2))
    
    async def get_total_stored_times(self):
        """Get the total number of stored times"""
        # extract timestamp
        timestamp = request.args.get("timestamp")
        try:
            if timestamp is not None:
                return str(await self.dbms.get_total_stored_times(int(round(float(timestamp)))))
            return str(await self.dbms.get_total_stored_times())
        except asyncio.exceptions.CancelledError:
            return jsonify({})

    async def get_replay(self, time_id):
        """ Function to get the replay of a time with id time_id """
        time_id = time_id.split(".")[0]
        try:
            return send_file("replays/" + time_id + ".replay")
        except FileNotFoundError:
            return "No replay found!"

    async def verify_time(self, time_id):
        """ Function to verify a time with id time_id """
        if await self.permission() == "AUTHORISED":
            our_discord_id = self.get_discord_id()
            await self.dbms.verify_time(time_id)
            try:
                details = await self.dbms.get_time_details(time_id)
                steam_name = details[1]
                time_id=details[4]
                total_time=details[6]
                trail_name=details[7]
                verified=details[14]
                if self.discord_bot is not None and verified == 1:
                    self.discord_bot.loop.run_until_complete(
                        self.discord_bot.send_message_to_channel(
                                f"[Time](https://modkit.nohumanman.com/time/{time_id})"
                                f" by {steam_name} of {total_time} on {trail_name} has been verified by <@{our_discord_id}>."
                                " This time will now display in leaderboards where appropriate. 🎉",
                                1213907351896334426
                        )
                    )
            except RuntimeError as e:
                logging.warning("Failed to submit time to discord server %s", e)
                return "ERROR: Failed to submit time to discord server"
            return "Toggled verification on time"
        else:
            return "ERROR: NO PERMISSION"

    async def get_output_log(self, player_id):
        """ Function to get the output log of a player with id player_id """
        if await self.permission() == "AUTHORISED":
            lines = ""
            try:
                with open(
                    f"{os.getcwd()}/output_log/{player_id}.txt",
                    "rt",
                    encoding="utf-8"
                ) as my_file:
                    file_lines = my_file.read().splitlines()
                    file_lines = file_lines[-50:]
                    for line in file_lines:
                        lines += f"> {line}<br>"
            except FileNotFoundError:
                lines = (
                    "Failed to get output log."
                    " One likely does not exist, has the user just loaded in?"
                )
            return lines
        return "You are not authorised to fetch output log."

    async def get_trails(self):
        """ Function to get the trails """ 
        return jsonify({"trails": (await self.dbms.get_trails())})

    async def ignore_time(self, time_id : int, value: str):
        """ Function to ignore a time with id time_id"""
        if await self.permission() == "AUTHORISED":
            # value should be 'False' or 'True
            await self.dbms.set_ignore_time(time_id, value)
            if self.discord_bot is not None:
                self.discord_bot.loop.run_until_complete(
                    self.discord_bot.new_time(
                        f"[Time](https://modkit.nohumanman.com/time/{time_id}) has been deleted."
                    )
                )
            return "success"
        return "INVALID_PERMS"
            
    async def upload_replay(self):
        """ Function to upload a replay """
        replay_file = request.files.get("replay")  # Using .get() to handle missing keys
        time_id = request.form.get('time_id')       # Using .get() to handle missing keys

        # Validate time_id
        if time_id is None:
            return "Error: Invalid time_id"

        # Ensure replay_file is not None
        if replay_file is None:
            return "Error: No replay file provided"

        # Securely save the file using a secure filename
        filename = secure_filename(f"{time_id}.replay")
        replay_path = os.path.join(os.getcwd(), 'static', 'replays', filename)

        # Save the file
        replay_file.save(replay_path)
        return "Success"

    async def get_worlds(self):
        """ Function to get the worlds """
        return jsonify({"worlds": await self.dbms.get_worlds()})

    async def concurrency(self):
        """ Function to get the concurrency of a map """
        map_name = request.args.get("map_name")
        if map_name == "" or map_name is None:
            return jsonify({})
        return jsonify({
            "concurrency": await self.dbms.get_daily_plays(
                map_name,
                datetime(2022, 5, 1),
                datetime.now()
            )
        })

    async def permission(self):
        """ Function to get the permission of a user """
        oauth2_token = session.get('oauth2_token')
        if oauth2_token is None:
            return "UNKNOWN"
        discord = await self.make_session(token=oauth2_token)
        user = discord.get(API_BASE_URL + '/users/@me').json()
        if user["id"] in [str(x[0]) for x in await self.dbms.get_valid_ids()]:
            return "AUTHORISED"
        return "UNAUTHORISED"

    async def logged_in(self):
        """ Function to check if a user is logged in """
        return (
            await self.permission() == "AUTHORISED"
            or await self.permission() == "UNAUTHORISED"
        )

    async def make_session(self, token=None, state=None, scope=None):
        """ Function to make a session """
        return OAuth2Session(
            client_id=OAUTH2_CLIENT_ID,
            token=token,
            state=state,
            scope=scope,
            redirect_uri=OAUTH2_REDIRECT_URI,
            auto_refresh_kwargs={
                'client_id': OAUTH2_CLIENT_ID,
                'client_secret': OAUTH2_CLIENT_SECRET,
            },
            auto_refresh_url=TOKEN_URL,
            refresh_token=self.token_updater
        )

    async def token_updater(self, token):
        """ Function to update the token """
        session['oauth2_token'] = token

    async def get_our_steam_id(self):
        """ Function to get the steam id of the user """
        discord = await self.make_session(token=session.get('oauth2_token'))
        connections = discord.get(
            API_BASE_URL + '/users/@me/connections'
        ).json()
        for connection in connections:
            if not isinstance(connection, dict):
                return "None"
            if connection["type"] == "steam":
                return connection["id"]
        return "None"

    async def get_discord_id(self):
        """ Function to get the discord name """
        discord = await self.make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        return user["id"]

    # routes
    async def callback(self):
        """ Function to handle the callback of the website """
        try:
            if request.values.get('error'):
                return request.values['error']
            if session.get('oauth2_state') is None:
                return "Invalid oauth2_state"
            discord = self.make_session(
                state=session.get('oauth2_state')
            )
            token = discord.fetch_token(
                TOKEN_URL,
                client_secret=OAUTH2_CLIENT_SECRET,
                authorization_response=request.url
            )
            session['oauth2_token'] = token
            user = discord.get(
                API_BASE_URL + '/users/@me'
            ).json()
            connections = discord.get(
                API_BASE_URL + '/users/@me/connections'
            ).json()
            try:
                user_id = user['id']
            except IndexError:
                return "User id not found on discord user?"
            try:
                user_id = user['id']
                try:
                    email = user['email']
                except KeyError:
                    email = ""
                username = user['username']
                steam_id = "NONE"
                try:
                    for connection in connections:
                        if connection['type'] == "steam":
                            steam_id = connection['id']
                except KeyError:
                    logging.info("Steam ID Not Found")
                await self.dbms.discord_login(user_id, username, email, steam_id)
            except Exception as e:
                logging.info("User %s with error %s", user, str(e))
            return redirect("/")
        except (IndexError, KeyError) as e:
            return str(e)
        except Exception as e:
            return str(e)

    async def me(self):
        """ Function to get the details of a user """
        try:
            discord = self.make_session(token=session.get('oauth2_token'))
            user = discord.get(API_BASE_URL + '/users/@me').json()
            connections = discord.get(
                API_BASE_URL + '/users/@me/connections'
            ).json()
            guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
            return jsonify(user=user, guilds=guilds, connections=connections)
        except MissingTokenError:
            return jsonify({})

    async def login(self):
        """ Function to login to the website """
        scope = request.args.get(
            'scope',
            'identify email connections guilds guilds.join'
        )
        scope = "identify connections"
        discord = self.make_session(scope=scope.split(' '))
        authorization_url, state = discord.create_authorization_url(
            AUTHORIZATION_BASE_URL
        )
        session['oauth2_state'] = state
        return redirect(authorization_url)

    async def get_leaderboard_for_trail(self):
        """ Function to get the leaderboard of the website"""

        trail_name = request.args.get("trail_name")
        world_name = request.args.get("world_name")
        if trail_name is None or world_name is None:
            return jsonify({})

        try:
            leaderboard = await self.dbms.get_leaderboard(trail_name, world_name)
        except asyncio.exceptions.CancelledError:
            return jsonify({})
        return jsonify([
                {
                    "place": player_time["place"],
                    "starting_speed": player_time["starting_speed"],
                    "name": player_time["name"],
                    "bike": player_time["bike"],
                    "version": player_time["version"],
                    "verified": player_time["verified"],
                    "deleted": player_time["deleted"],
                    "time_id": str(player_time["time_id"]),
                    "time": player_time["time"],
                    "submission_timestamp": player_time["submission_timestamp"],
                }
                for player_time in leaderboard
            ])

    async def get_leaderboard_trail(self, trail):
        """ Function to get the leaderboard of the website"""
        try:
            return jsonify(await self.dbms.get_leaderboard(trail))
        except asyncio.exceptions.CancelledError:
            return jsonify({})

    async def get_all_times(self):
        """ Function to get all the times of the website"""
        page = int(request.args.get("page"))
        items_per_page = int(request.args.get("items_per_page"))
        sort_by = request.args.get("sort_by")
        order = request.args.get("order")        
        return jsonify(
            await self.dbms.get_recent_times(
                page, items_per_page, sort_by, order == "desc"
            )
        )

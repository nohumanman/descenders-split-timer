from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, BigInteger, REAL, TIMESTAMP
from sqlalchemy.sql.expression import func
from sqlalchemy.future import select
from datetime import datetime, timedelta
import time
import logging

Base = declarative_base()

# Database Models
class Player(Base):
    __tablename__ = 'players'

    steam_id = Column(String, primary_key=True)
    steam_name = Column(String)

class BikeType(Base):
    __tablename__ = 'bike_types'

    bike_id = Column(Integer, primary_key=True)
    bike_name = Column(String)

class PlayerTime(Base):
    __tablename__ = 'player_times'

    player_time_id = Column(BigInteger, primary_key=True)
    steam_id = Column(String, ForeignKey('players.steam_id'))
    submission_timestamp = Column(Float)
    trail_id = Column(Integer, ForeignKey('trails.trail_id'))
    bike_id = Column(Integer)#, ForeignKey(BikeType.bike_id))
    starting_speed = Column(Float)
    version = Column(String)
    game_version = Column(String)
    deleted = Column(Boolean)

class CheckpointTime(Base):
    __tablename__ = 'checkpoint_times'

    player_time_id = Column(BigInteger, ForeignKey('player_times.player_time_id'), primary_key=True)
    checkpoint_num = Column(Integer, primary_key=True)
    checkpoint_time = Column(Float)


class Trail(Base):
    __tablename__ = 'trails'

    trail_id = Column(Integer, primary_key=True)
    trail_name = Column(String)
    world_name = Column(String)

class Verification(Base):
    __tablename__ = 'verifications'

    player_time_id = Column(BigInteger, primary_key=True)
    verifier_id = Column(BigInteger)
    verification_timestamp = Column(Float)
    verified = Column(Boolean)

class WebsiteUser(Base):
    __tablename__ = 'website_users'

    discord_id = Column(BigInteger, primary_key=True)
    steam_id = Column(String)
    discord_name = Column(String)
    authorised = Column(Boolean)

# Database Management System
class DBMS:
    """ A simple Database Management System (DBMS) class for managing data using SQLAlchemy. """

    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initialize the database and create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_id_from_name(self, steam_name):
        async with self.async_session() as session:
            result = await session.execute(select(Player).filter_by(steam_name=steam_name))
            player = result.scalar_one_or_none()
            return player.steam_id if player else None

    async def update_player(self, steam_id, steam_name):
        '''
        Update the player's steam name and id.
        '''
        async with self.async_session() as session:
            player = await session.get(Player, steam_id)
            if player:
                player.steam_name = steam_name
            else:
                print("CREATING NEW PLAYER")
                player = Player(steam_id=steam_id, steam_name=steam_name)
                session.add(player)
            print("QTS", player)
            await session.commit()

    async def get_player(self, steam_id):
        async with self.async_session() as session:
            player = await session.get(Player, steam_id)
            # if player does not exist, add it and return None
            if not player:
                player = Player(steam_id=steam_id, steam_name=None)
                session.add(player)
                await session.commit()
            return player.steam_name if player else None

    async def get_all_players(self):
        async with self.async_session() as session:
            result = await session.execute(select(Player))
            return result.scalars().all()

    async def get_trail_id(self, trail_name, world_name):
        async with self.async_session() as session:
            result = await session.execute(
                select(Trail).filter_by(
                    trail_name=trail_name,
                    world_name=world_name)
                )
            trail = result.scalar_one_or_none()
            # If trail does not exist, create it
            if not trail:
                trail = Trail(
                    trail_name=trail_name,
                    world_name=world_name
                )
                session.add(trail)
                await session.commit()
                # Return the trail id
                return await self.get_trail_id(trail_name, world_name) # recursive!
            return trail.trail_id if trail else None

    async def submit_time(
        self,
        steam_id: str,
        checkpoint_times: list[float],
        trail_name: str,
        current_world: str,
        bike_id : int,
        starting_speed: float,
        version: str,
        game_version: str,
        auto_verify: bool = True
    ):
        # print all from BikeType
        async with self.async_session() as session:
            result = await session.execute(select(BikeType))
            print("BIKES", result.scalars().all())

        player_time_id = hash(
            str(checkpoint_times[-1]) + str(steam_id) + str(time.time())
        ) # TODO: This hash function may have collisions
        await self.get_player(steam_id) # Ensure player exists
        if auto_verify:
            await self.submit_time_verification(player_time_id, 0, True)
        async with self.async_session() as session:
            new_time = PlayerTime(
                player_time_id=player_time_id,
                steam_id=steam_id,
                submission_timestamp=time.time(),
                trail_id=await self.get_trail_id(trail_name, current_world),
                bike_id=bike_id,
                starting_speed=starting_speed,
                version=version,
                game_version=game_version,
                deleted=False
            )
            session.add(new_time)
            await session.commit()

            for n, checkpoint_time in enumerate(checkpoint_times):
                split = CheckpointTime(
                    player_time_id=player_time_id,
                    checkpoint_num=n,
                    checkpoint_time=float(checkpoint_time),
                )
                session.add(split)

            await session.commit()
        return player_time_id

    async def get_trails(self) -> list[Trail]:
        async with self.async_session() as session:
            result = await session.execute(select(Trail))
            trails = result.scalars().all()
            return [
                {
                    "trail_name": trail.trail_name,
                    "world_name": trail.world_name
                }
                for trail in trails
            ]

    async def get_leaderboard(self, trail_name, world_name, num=10, verified_only=True):
        async with self.async_session() as session:
            ranked_times_subquery = (
                select(
                    PlayerTime,
                    CheckpointTime.checkpoint_time,
                    func.row_number()
                    .over(
                        partition_by=PlayerTime.steam_id,  # Partition by steam_id to rank within each steam_id group
                        order_by=func.min(CheckpointTime.checkpoint_time).asc()  # Order by the fastest time
                    )
                    .label("row_rank")
                )
                .join(
                    CheckpointTime, CheckpointTime.player_time_id == PlayerTime.player_time_id
                )
                .join(
                    Player,
                    Player.steam_id == PlayerTime.steam_id
                )
                .where(
                    PlayerTime.trail_id == await self.get_trail_id(trail_name, world_name),
                    # Add additional conditions as needed:
                    # PlayerTime.verified == True,  # Uncomment if verification check is required
                    PlayerTime.deleted == False  # Ensure time is not deleted
                )
                .group_by(
                    PlayerTime.player_time_id,  # Group by player_time_id to calculate min checkpoint_time
                    PlayerTime.steam_id,
                    CheckpointTime.checkpoint_time
                )
                .subquery()
            )

            # Main query: Select only the rows where row_rank = 1
            result = await session.execute(
                select(
                    ranked_times_subquery.c.starting_speed,
                    ranked_times_subquery.c.steam_id,
                    ranked_times_subquery.c.bike_id,
                    ranked_times_subquery.c.version,
                    ranked_times_subquery.c.checkpoint_time,
                    ranked_times_subquery.c.player_time_id
                )
                .where(ranked_times_subquery.c.row_rank == 1)  # Only take the top-ranked row for each steam_id
                .order_by(ranked_times_subquery.c.checkpoint_time.asc())  # Order by fastest time overall
                .limit(num)  # Limit the results if needed
            )

            times = result.all()
            return [
                {
                    "place": i + 1,
                    "starting_speed": starting_speed,
                    "name": (await session.get(Player, steam_id)).steam_name,
                    "bike": bike_id,
                    "version": version,
                    "verified":True,# verified,
                    "time_id": player_time_id,
                    "time": checkpoint_time,
                }
                for i, (starting_speed, steam_id, bike_id, version, checkpoint_time, player_time_id) in enumerate(times)
            ]
    
    async def delete_time(self, time_id):
        async with self.async_session() as session:
            time = await session.get(PlayerTime, time_id)
            time.deleted = True
            await session.commit()
    
    async def get_time(self, time_id):
        async with self.async_session() as session:
            time = await session.get(PlayerTime, time_id)
            return {
                "starting_speed": time.starting_speed,
                "name": (await session.get(Player, time.steam_id)).steam_name,
                "bike": time.bike_id,
                "version": time.version,
                "time_id": time.player_time_id,
                "time": time.submission_timestamp,
            }

    async def submit_time_verification(
            self,
            time_id: int,
            verifier_id: int,
            verified: bool
        ):
        async with self.async_session() as session:
            verification = Verification(
                verifier_id=verifier_id,
                verification_timestamp=time.time(),
                verified=verified,
                player_time_id=time_id
            )
            session.add(verification)
            await session.commit()

    async def authorise_discord_user(self, discord_id):
        async with self.async_session() as session:
            user = await session.get(WebsiteUser, discord_id)
            user.authorised = True
            await session.commit()
    
    async def get_discord_user(self, discord_id):
        async with self.async_session() as session:
            user = await session.get(WebsiteUser, discord_id)
            return user
    
    async def add_discord_user(self, discord_id, steam_id, discord_name):
        async with self.async_session() as session:
            user = WebsiteUser(
                discord_id=discord_id,
                steam_id=steam_id,
                discord_name=discord_name,
                authorised=False
            )
            session.add(user)
            await session.commit()

    async def get_personal_best_checkpoint_times(self, steam_id, trail_name, world_name):
        pass

    async def get_global_best_checkpoint_times(self, trail_name, world_name):
        pass

    async def get_recent_times(self, limit=10):
        return [{
            "avatar_src":"no.jpg",
            "bike_type":"downhill",
            "ignore":0,
            "starting_speed":3.266331,
            "steam_id":"76561199085553376",
            "steam_name":"Lawrence_R",
            "time_id":"-6495871202898393399",
            "timestamp":1737747771.6579456,
            "total_checkpoints":4,
            "total_time":43.7205352783203,
            "trail_name":"Fort William 4x",
            "verified":1,
            "version":"0.3.01",
            "world_name":"Fort William 4x (race)-0.48"
        }]

    async def get_trail_average_starting_speed(self, trail_name, world_name):
        async with self.async_session() as session:
            result = await session.execute(
                select(PlayerTime.starting_speed)
                .join(Trail, Trail.trail_id == PlayerTime.trail_id)
                .where(
                    Trail.trail_name == trail_name,
                    Trail.world_name == world_name
                )
            )
            speeds = result.scalars().all()
            return sum(speeds) / len(speeds) if speeds else None

    async def close(self):
        await self.engine.dispose()

# Example usage:
# dbms = DBMS("postgresql+asyncpg://user:password@localhost/modkit")
# await dbms.init_db()

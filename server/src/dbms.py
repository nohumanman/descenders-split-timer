from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, BigInteger, REAL
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

# Database Management System
class DBMS:
    """ A simple Database Management System (DBMS) class for managing data using SQLAlchemy. """

    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=True)
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
        steam_id,
        checkpoint_times,
        trail_name,
        current_world,
        bike_id : int,
        starting_speed: float,
        version,
        game_version
    ):
        # print all from BikeType
        async with self.async_session() as session:
            result = await session.execute(select(BikeType))
            print("BIKES", result.scalars().all())

        player_time_id = hash(
            str(checkpoint_times[-1]) + str(steam_id) + str(time.time())
        ) # TODO: This hash function may have collisions
        await self.get_player(steam_id) # Ensure player exists
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

    async def get_leaderboard(self, trail_name, num=10):
        async with self.async_session() as session:
            result = await session.execute(
                select(PlayerTime)
                .filter_by(trail_id=await self.get_trail_id(trail_name, "Test World"), deleted=False)
                .order_by(PlayerTime.submission_timestamp.asc())
                .limit(num)
            )
            times = result.scalars().all()
            return [
                {
                    "place": i + 1,
                    "starting_speed": time.starting_speed,
                    "name": (await session.get(Player, time.steam_id)).steam_name,
                    "bike": time.bike_id,
                    "version": time.version,
                    #"verified": time.verified,
                    "time_id": time.player_time_id,
                    "time": time.submission_timestamp,
                }
                for i, time in enumerate(times)
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

    

    async def close(self):
        await self.engine.dispose()

# Example usage:
# dbms = DBMS("postgresql+asyncpg://user:password@localhost/modkit")
# await dbms.init_db()

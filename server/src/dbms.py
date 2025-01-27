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

class FinalTimesDetailed(Base):
    __tablename__ = 'final_times_detailed'
    
    player_time_id = Column(Integer, primary_key=True)
    steam_id = Column(String, nullable=False)
    submission_timestamp = Column(TIMESTAMP, nullable=False)
    trail_id = Column(Integer, nullable=False)
    bike_id = Column(Integer, nullable=False)
    starting_speed = Column(Float, nullable=False)
    version = Column(String, nullable=False)
    game_version = Column(String, nullable=False)
    deleted = Column(Boolean, nullable=False)
    final_time = Column(Float, nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    verifier_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)  # Adjust ForeignKey table if necessary

class PendingItems(Base):
    __tablename__ = 'pending_items'

    steam_id = Column(String, ForeignKey('players.steam_id'))
    item_id = Column(String)
    time_redeemed = Column(Float, primary_key=True)

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
                player = Player(steam_id=steam_id, steam_name=steam_name)
                session.add(player)
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

    async def get_total_stored_times(self, timestamp: int = 0) -> int:
        async with self.async_session() as session:
            result = await session.execute(
                select(FinalTimesDetailed)
                .where(FinalTimesDetailed.submission_timestamp > timestamp)
            )
            return len(result.scalars().all())

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

    async def get_leaderboard(
            self,
            trail_name = None,
            world_name = None,
            num=10,
            verified=True
        ) -> list[dict]:
        async with self.async_session() as session:
            query = select(FinalTimesDetailed).filter_by(deleted=False, verified=verified)
            if trail_name is not None and world_name is not None:
                query = query.join(Trail, Trail.trail_id == FinalTimesDetailed.trail_id).filter(Trail.trail_name == trail_name and Trail.world_name == world_name)
            if num:
                query = query.order_by(FinalTimesDetailed.final_time).limit(num)
            else:
                query = query.order_by(FinalTimesDetailed.final_time)
            result = await session.execute(query)
            times = result.scalars().all()

            return [
                {
                    "place": i + 1,
                    "starting_speed": final_times_detailed.starting_speed,
                    "name": (await self.get_player(final_times_detailed.steam_id)),
                    "bike": final_times_detailed.bike_id,
                    "version": final_times_detailed.version,
                    "verified":final_times_detailed.verified,
                    "deleted":final_times_detailed.deleted,
                    "time_id": final_times_detailed.player_time_id,
                    "time": final_times_detailed.final_time,
                    "submission_timestamp": final_times_detailed.submission_timestamp
                }
                for i, final_times_detailed in enumerate(times)
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

    async def get_recent_times(self, page=1, itemsPerPage=10, sortBy="submission_timestamp", sortDesc=False):
        async with self.async_session() as session:
            query = select(FinalTimesDetailed)
            # TODO: This should be a dictionary
            if sortBy == "submission_timestamp":
                query = query.order_by(FinalTimesDetailed.submission_timestamp.desc() if sortDesc else FinalTimesDetailed.submission_timestamp)
            elif sortBy == "time":
                query = query.order_by(FinalTimesDetailed.final_time.desc() if sortDesc else FinalTimesDetailed.final_time)
            elif sortBy == "starting_speed":
                query = query.order_by(FinalTimesDetailed.starting_speed.desc() if sortDesc else FinalTimesDetailed.starting_speed)
            elif sortBy == "name":
                query = query.order_by(FinalTimesDetailed.steam_id.desc() if sortDesc else FinalTimesDetailed.steam_id)
            elif sortBy == "bike":
                query = query.order_by(FinalTimesDetailed.bike_id.desc() if sortDesc else FinalTimesDetailed.bike_id)
            elif sortBy == "version":
                query = query.order_by(FinalTimesDetailed.version.desc() if sortDesc else FinalTimesDetailed.version)

            if itemsPerPage != -1 and page and itemsPerPage:
                query = query.limit(itemsPerPage).offset((page - 1) * itemsPerPage)
            result = await session.execute(query)
            times = result.scalars().all()
            return [
                {
                    "starting_speed": final_times_detailed.starting_speed,
                    "name": await self.get_player(final_times_detailed.steam_id),
                    "bike": final_times_detailed.bike_id,
                    "version": final_times_detailed.version,
                    "verified":final_times_detailed.verified,
                    "deleted":final_times_detailed.deleted,
                    "time_id": str(final_times_detailed.player_time_id),
                    "time": final_times_detailed.final_time,
                    "submission_timestamp": final_times_detailed.submission_timestamp
                }
                for final_times_detailed in times
            ]

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
    
    async def get_pending_items(self, steam_id):
        async with self.async_session() as session:
            result = await session.execute(select(PendingItems).filter_by(steam_id=steam_id))
            return result.scalars().all()
    
    async def redeem_pending_item(self, steam_id, item_id):
        async with self.async_session() as session:
            item = await session.get(PendingItems, (steam_id, item_id))
            item.time_redeemed = time.time()
            await session.commit()

# Example usage:
# dbms = DBMS("postgresql+asyncpg://user:password@localhost/modkit")
# await dbms.init_db()

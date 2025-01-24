'''
Module to test DBMS
'''

import unittest
import time
from src.dbms import DBMS

class TestDbms(unittest.IsolatedAsyncioTestCase):

    def connect(self):
        import psycopg2
        conn = psycopg2.connect(
            database = "postgres", 
            user = "postgres", 
            host= 'localhost',
            password = "postgres",
            port = 5432
        )
        return conn

    def reset_database(self):
        drop_all = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(drop_all)
        with open('./server/src/database-schema/schema.sql') as f:
            schema = f.read()
            cur.execute(schema)
        conn.commit()
        conn.close()


    async def test_update_player(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        await dbms_instance.update_player("76561198000000000", "test_player")
        # check if player was added
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "test_player")
    
    async def test_update_player_with_existing_player(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        await dbms_instance.update_player("76561198000000000", "test_player")
        await dbms_instance.update_player("76561198000000000", "test_player2")
        # check if player was updated in dbms.py
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "test_player2")
        # check if player was updated in the database
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM players WHERE steam_id = '76561198000000000'")
        result = cur.fetchone()
        print("XQC", result)
        conn.close()
        self.assertEqual(result[1], "test_player2")

    async def test_update_player_with_existing_player_and_no_name(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        await dbms_instance.update_player("76561198000000000", "test_player")
        await dbms_instance.update_player("76561198000000000", "")
        # check if player was updated
        self.assertEqual(await dbms_instance.get_player("76561198000000000"), "")

    async def test_submit_time(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        await dbms_instance.submit_time(
            "76561198000000000", # steam_id
            [1, 2, 3, 4], # checkpoint_times
            "Test Trail", # trail_name
            "Test World", # world_name
            1, # bike_type_id
            8.34, # starting_speed
            "1.34", # version
            "", # game version
        )
    
    async def test_get_trails_empty(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [])

    async def test_get_trails_generated_by_submit_time(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [])
        # add trail
        await dbms_instance.submit_time(
            "76561198000000000", # steam_id
            [1, 2, 3, 4], # checkpoint_times
            "Test Trail", # trail_name
            "Test World", # world_name
            1, # bike_type_id
            8.34, # starting_speed
            "1.34", # version
            "", # game version
        )
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [{'trail_name': 'Test Trail', 'world_name': 'Test World'}])

    async def test_get_trails_generated_by_get_trail_id(self):
        self.reset_database()
        dbms_instance = DBMS("postgresql+asyncpg://postgres:postgres@localhost/postgres")
        await dbms_instance.init_db()
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [])
        # add trail
        await dbms_instance.get_trail_id("Test Trail", "Test World")
        trails = await dbms_instance.get_trails()
        self.assertEqual(trails, [{'trail_name': 'Test Trail', 'world_name': 'Test World'}])

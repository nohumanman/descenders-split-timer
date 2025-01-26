import unittest

'''
Module to test the Trail table:

CREATE TABLE Trail (
    "trail_id" SERIAL PRIMARY KEY,
    "world_name" TEXT,
    "trail_name" TEXT
);
'''

class TestTrail(unittest.TestCase):

    def reset_database(self):
        drop_all = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(drop_all)
        with open('./server/src/database-schema/schema.sql') as f:
            schema = f.read()
            cur.execute(schema)
        conn.commit()

    def connect(self):
        import psycopg2
        self.conn = psycopg2.connect(
            database = "postgres", 
            user = "postgres", 
            host= 'localhost',
            password = "postgres",
            port = 5432
        )
        return self.conn

    def test_insert(self):
        self.reset_database()
        self.connect()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO trails (world_name, trail_name) VALUES ('world1', 'trail1')")
        self.conn.commit()
        self.conn.close()
        # check if record was added
        self.conn = self.connect()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM trails")
        rows = cur.fetchall()
        self.assertEqual(len(rows), 1)
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
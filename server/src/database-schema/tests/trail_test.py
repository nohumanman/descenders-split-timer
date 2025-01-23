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

    def connect(self):
        import psycopg2
        self.conn = psycopg2.connect(
            database = "postgres", 
            user = "postgres", 
            host= 'localhost',
            password = "postgres",
            port = 5432
        )

    def test_insert(self):
        self.connect()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO Trail (world_name, trail_name) VALUES ('world1', 'trail1')")
        self.conn.commit()
        self.conn.close()
        print("Record Inserted!")

if __name__ == '__main__':
    unittest.main()
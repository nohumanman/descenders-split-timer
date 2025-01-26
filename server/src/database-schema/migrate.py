# export database to SQL dump file
#sqlite3 modkit.db .dump > database.sql
# import database to postgres
#psql postgresql://postgres:postgres@localhost/postgres < database.sql

import sqlite3
import psycopg2

# connect to sqlite
conn = sqlite3.connect('modkit.db')
cursor = conn.cursor()

# get all players
cursor.execute("SELECT * FROM Player")
players = cursor.fetchall()
players = [[player[0], player[1]] for player in players]

# connect to postgres
psycopg2_conn = psycopg2.connect("postgresql://postgres:postgres@localhost/postgres")
psycopg2_cursor = psycopg2_conn.cursor()

psycopg2_cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;") # TODO: DELETEME
with open("schema.sql", "r") as f:
    psycopg2_cursor.execute(f.read())

# insert into players

for player in players:
    psycopg2_cursor.execute(
        "INSERT INTO players (steam_id, steam_name) VALUES (%s, %s)", (int(player[0]), player[1])
    )
psycopg2_conn.commit()


# insert into trails
cursor.execute("SELECT * FROM Time")
times = cursor.fetchall()
trails = [[time[3], time[4]] for time in times]
# insert into trails
trails_encountered = []
for trail in trails:
    if trail in trails_encountered:
        continue
    psycopg2_cursor.execute(
        "INSERT INTO trails (world_name, trail_name) VALUES (%s, %s)", (trail[0], trail[1])
    )
    trails_encountered.append(trail)

psycopg2_conn.commit()


# insert into player_times
cursor.execute("SELECT * FROM Time")
times = cursor.fetchall()
for time in times:
    steam_id = time[0]
    time_id = int(time[1])
    timestamp = time[2]
    world_name = time[3]
    trail_name = time[4]
    bike_type = 0 if time[5] == "enduro" else 1 if time[5] == "downhill" else 2
    starting_speed = time[6]
    version = time[7]
    verified = time[8]
    deleted = time[9] == 1
    psycopg2_cursor.execute(
        '''
            INSERT INTO player_times
            (
                steam_id,
                player_time_id,
                submission_timestamp,
                trail_id, bike_id, starting_speed,
                version, game_version, deleted
            ) VALUES (
            %s, %s, %s, (SELECT trails.trail_id FROM trails WHERE trails.trail_name = %s AND trails.world_name = %s), %s, %s, %s, 0, %s) 
        ''',
        (steam_id, time_id, timestamp, trail_name, world_name, bike_type, starting_speed, version, deleted)
    )

psycopg2_conn.commit()
# insert split times into checkpoints
cursor.execute("SELECT * FROM SplitTime")
split_times = cursor.fetchall()
for split_time in split_times:
    try:
        psycopg2_cursor.execute(
            "INSERT INTO checkpoint_times (player_time_id, checkpoint_num, checkpoint_time) VALUES (%s, %s, %s)", (int(split_time[0]), int(split_time[1]), split_time[2])
        )
        psycopg2_conn.commit()
    except Exception as e:
        print(e)
        print(split_time)
psycopg2_conn.commit()


# now we do verification
cursor.execute("SELECT time_id, verified FROM Time")
times = cursor.fetchall()
for time in times:
    time_id = time[0]
    verified = time[1] == 1
    if verified:
        psycopg2_cursor.execute(
            '''
                INSERT INTO verifications (player_time_id, verifier_id, verified) VALUES (%s, -1, %s)
            ''',
            (time_id, verified)
        )
        psycopg2_conn.commit()

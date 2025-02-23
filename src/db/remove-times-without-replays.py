import psycopg2

# connect to postgres server
conn = psycopg2.connect("postgresql://postgres:postgres@localhost/postgres")
cursor = conn.cursor()
# iterate through every time, and check if the replay exists
cursor.execute("SELECT * FROM player_times")
times = cursor.fetchall()
for time in times:
    time_id = time[0]
    # check if ./replays/{time_id}.replay exists
    try:
        with open(f"./replays/{time_id}.replay", "r") as f:
            pass
    except FileNotFoundError:
        # if it doesn't exist, remove the time
        cursor.execute("UPDATE player_times SET deleted=true where player_time_id = %s", (time_id,))

print("Finished")
# commit and close connection
conn.commit()
cursor.close()

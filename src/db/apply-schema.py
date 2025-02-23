import psycopg2

# connect to postgres
conn = psycopg2.connect("postgresql://postgres:postgres@localhost/postgres")
cursor = conn.cursor()

cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;") # TODO: DELETEME
with open("schema.sql", "r") as f:
    cursor.execute(f.read())
conn.commit()
conn.close()

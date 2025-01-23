import psycopg2

# apply schema.sql to postgres://postgres:postgres@localhost:5432/postgres

with open('schema.sql') as f:
    schema = f.read()
    conn = psycopg2.connect(
        database = "postgres", 
        user = "postgres", 
        host= 'localhost',
        password = "postgres",
        port = 5432
    )
    cur = conn.cursor()
    cur.execute(schema)
    conn.commit()
    conn.close()

print("Schema Applied!")
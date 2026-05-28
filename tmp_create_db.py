import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect('postgresql://postgres:Zelaya1103@localhost:5432/postgres')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if exists first
    cur.execute("SELECT 1 FROM pg_database WHERE datname='mivoto'")
    exists = cur.fetchone()
    if not exists:
        cur.execute('CREATE DATABASE mivoto;')
        print("Base de datos mivoto creada exitosamente.")
    else:
        print("La base de datos mivoto ya existe.")
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)

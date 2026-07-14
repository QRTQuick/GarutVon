from dotenv import load_dotenv
import os
import psycopg2

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='users' ORDER BY ordinal_position;")
rows = cur.fetchall()
for col, typ, nul, dft in rows:
    print(f'{col}\t{typ}\t{nul}\t{dft}')
conn.close()

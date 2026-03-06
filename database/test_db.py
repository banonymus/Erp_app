import psycopg

conn = psycopg.connect(
    "postgresql://neondb_owner:npg_h6CQMYKVjRL3@ep-lingering-bird-alyu67ca-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

cur = conn.cursor()
cur.execute("SELECT 1;")
print(cur.fetchone())

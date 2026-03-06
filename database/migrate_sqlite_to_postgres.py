import sqlite3
from database.db import get_connection

sqlite_conn = sqlite3.connect("database/erp.db")
pg_conn = get_connection()

sqlite_cur = sqlite_conn.cursor()
pg_cur = pg_conn.cursor()

tables = ["users", "customers", "products", "sales_orders", "sales_items"]

for table in tables:
    rows = sqlite_cur.execute(f"SELECT * FROM {table}").fetchall()
    for row in rows:
        placeholders = ",".join(["%s"] * len(row))
        pg_cur.execute(f"INSERT INTO {table} VALUES (DEFAULT, {placeholders})", row)

pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

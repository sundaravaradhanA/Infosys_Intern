import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="banking_db",
    user="postgres",
    password="sundar@2005"
)

cur = conn.cursor()
cur.execute("SELECT id, description, category FROM transactions LIMIT 10;")
rows = cur.fetchall()

print("Transactions in database:")
for row in rows:
    print(f"  ID: {row[0]}, Description: {row[1]}, Category: {row[2]}")

cur.close()
conn.close()

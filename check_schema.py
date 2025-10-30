import sqlite3

# Check the actual column order in the tickets table
conn = sqlite3.connect("maintenance_tickets.db")
cursor = conn.cursor()

print("Tickets table schema:")
cursor.execute("PRAGMA table_info(tickets)")
columns = cursor.fetchall()

for col in columns:
    print(f"  {col[0]}: {col[1]} ({col[2]})")

print("\nSample ticket data:")
cursor.execute("SELECT * FROM tickets LIMIT 1")
ticket = cursor.fetchone()
if ticket:
    print(f"  Raw data: {ticket}")
    for i, value in enumerate(ticket):
        print(f"  Index {i}: {value}")
else:
    print("  No tickets found")

conn.close()

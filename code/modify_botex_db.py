import sqlite3

BOTEX_DB = 'data/generated/botex_db.sqlite3'

# Delete a session from the database
SESSION_TO_DELETE = "xjne3ft4"
conn = sqlite3.connect(BOTEX_DB)
cursor = conn.cursor()
cursor.execute("DELETE FROM participants WHERE session_id = ?", (SESSION_TO_DELETE,))
cursor.execute(f"DELETE FROM conversations WHERE bot_parms like '%{SESSION_TO_DELETE}%'")
conn.commit()
conn.close()
import sqlite3

connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
cursor = connect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS ChatGPT (
                id INT,
                personality TEXT,
                con TEXT,
                con2 TEXT
                )""")
connect.commit()
connect.close()
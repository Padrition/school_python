import sqlite3
from sqlite3 import Error

con = sqlite3.connect("vwa.db")

cur = con.cursor()

with open("db.sql", 'r') as db_file:
    sql_commands = db_file.read()
    cur.executescript(sql_commands)

con.commit()

with open("vwa.sql", 'r') as sql_file:
    sql_commands = sql_file.read()
    cur.executescript(sql_commands)

con.commit()

con.close()
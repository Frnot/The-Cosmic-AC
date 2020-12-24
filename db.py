import logging
import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor

def query(sql_query):
    cursor.execute(sql_query)
    conn.commit

def exit():
    conn.close()
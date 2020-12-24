import os
import sqlite3
import logging
log = logging.getLogger(__name__)

############
## TODO: make this async?

db_filename = 'data.db'


### "Constructor"
def load():
    global conn
    global cursor

    log.info("Initializing database")
    if not os.path.exists(db_filename):
        conn = new_db()
        cursor = conn.cursor()
    else:
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()


def new_db():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    log.info("Setting up database tables")
    log.debug("Creating database table 'snitch'")
    cursor.execute("CREATE TABLE 'snitch' (guild_id INT, hook_channel_id INT)")

    conn.commit()
    return conn


def select(row, table, symbol, value):
    sql = f"SELECT {row} FROM {table} WHERE {symbol}={value}"
    log.debug(f"Sending query: '{sql}' to database")
    cursor.execute(sql)
    result = cursor.fetchone()
    if result is None:
        return result
    else:
        return result[0]


def insert(table, columns, values):
    sql = f"INSERT INTO {table} {columns} VALUES {values}"
    log.debug(f"Sending query: '{sql}' to database")
    cursor.execute(sql)
    conn.commit()


def exit():
    conn.close()

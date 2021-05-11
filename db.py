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
    if os.path.exists(db_filename):
        try:
            conn = sqlite3.connect(db_filename)
        except Error as e:
            print(e)
            sys.exit("database error")
        cursor = conn.cursor()
    else:
        log.info("Creating new database")
        conn = new_db()
        cursor = conn.cursor()
    log.info("database loaded")

def exit():
    log.info("Closing database connection.")
    conn.close()

################


def new_db():
    try:
        conn = sqlite3.connect(db_filename)
    except Error as e:
        print(e)
        sys.exit("database error")
    cursor = conn.cursor()

    log.info("Setting up database tables")

    log.debug("Creating database table 'snitch'")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'snitch' (
        guild_id integer PRIMARY KEY, 
        hook_channel_id INT
        );""")

    log.debug("Creating database table 'voting'")
    cursor.execute("""CREATE TABLE IF NOT EXISTS 'voting' (
        guild_id integer PRIMARY KEY, 
        voting_role_id integer
        );""")

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


def insert(table, data):
    sql = f"INSERT INTO {table} ({', '.join(str(row[0]) for row in data)}) VALUES ({', '.join(str(row[1]) for row in data)})"
    log.debug(f"Sending query: '{sql}' to database")
    cursor.execute(sql)
    conn.commit()


def update(table, data):
    sql = f"UPDATE {table} SET ({', '.join(str(row[0]) for row in data)}) = ({', '.join(str(row[1]) for row in data)})"
    log.debug(f"Sending query: '{sql}' to database")
    cursor.execute(sql)
    conn.commit()


def delete(table, data):
    sql = f"DELETE FROM {table} WHERE {str(data[0])} = {str(data[1])}"
    log.debug(f"Sending query: '{sql}' to database")
    cursor.execute(sql)
    conn.commit()

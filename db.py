import os
import sqlite3
import sys
import logging
log = logging.getLogger(__name__)

############
## TODO: make this async?

db_filename = 'data.db'
init_tables = {
    "snitch":"CREATE TABLE IF NOT EXISTS 'snitch' (guild_id INT PRIMARY KEY, hook_channel_id INT);",
    "blacklist":"CREATE TABLE IF NOT EXISTS 'blacklist' (guild_id INT PRIMARY KEY, blacklist_set TEXT);",
    "voting":"CREATE TABLE IF NOT EXISTS 'voting' (guild_id INT PRIMARY KEY, voting_role_id INT);",
}

### "Constructor"
def load():
    global conn
    global cursor

    log.info("Initializing database")
    if os.path.exists(db_filename):
        try:
            conn = sqlite3.connect(db_filename)
        except Exception as e:
            print(e)
            sys.exit("database error")
        cursor = conn.cursor()
        reload_tables(cursor)
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
    except Exception as e:
        print(e)
        sys.exit("database error")
    cursor = conn.cursor()

    log.info("Setting up database tables")

    for key, value in init_tables.items():
        log.debug(f"Creating database table {key}")
        cursor.execute(value)

    conn.commit()
    return conn



def reload_tables(cursor):
    log.info("Updating database tables")
    for key, value in init_tables.items():
        log.debug(f"Updating database table {key}")
        cursor.execute(value)
    
    conn.commit()



def select(row, table, symbol, value):
    sql = f"SELECT {row} FROM {table} WHERE {symbol}={value}"
    log.debug(f"Sending query: '{sql}' to database")

    try:
        cursor.execute(sql)
    except Exception as e:
        log.error(f"SQL query failed: {e}")

    result = cursor.fetchone()
    if result is None:
        return result
    else:
        return result[0]


# TODO: make the (?, ?) parameter variable length based on data rows
def insert(table, data):
    #sql = f"INSERT INTO {table} ({', '.join(str(row[0]) for row in data)}) VALUES ({', '.join(str(row[1]) for row in data)})"
    sql = f"INSERT INTO {table} ({', '.join(str(row[0]) for row in data)}) VALUES (?, ?)"
    payload = [row[1] for row in data]

    log.debug(f"Sending query: '{sql}, ({', '.join(str(word) for word in payload)})' to database")
    try:
        cursor.execute(sql, payload)
        conn.commit()
    except Exception as e:
        log.error(f"SQL query failed: {e}")


# TODO: make the (?, ?) parameter variable length based on data rows
def update(table, data):
    #sql = f"UPDATE {table} SET ({', '.join(str(row[0]) for row in data)}) = ({', '.join(str(row[1]) for row in data)})"
    sql = f"UPDATE {table} SET ({', '.join(str(row[0]) for row in data)}) = (?, ?)"
    payload = [row[1] for row in data]

    log.debug(f"Sending query: '{sql}, ({', '.join(str(word) for word in payload)})' to database")
    try:
        cursor.execute(sql, payload)
        conn.commit()
    except Exception as e:
        log.error(f"SQL query failed: {e}")



def delete(table, data):
    sql = f"DELETE FROM {table} WHERE {data[0]} = {data[1]}"
    log.debug(f"Sending query: '{sql}' to database")
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        log.error(f"SQL query failed: {e}")

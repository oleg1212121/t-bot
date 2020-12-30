import sqlite3


def init_db(refresh: bool = False):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        if refresh:
            cursor.execute('DROP TABLE IF EXISTS messages')
            cursor.execute('DROP TABLE IF EXISTS secrets')
            cursor.execute('DROP TABLE IF EXISTS users')

        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER UNIQUE,
                            first_name text,
                            user_name text,
                            message text,
                            date DATE
                            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS secrets (
                            id INTEGER PRIMARY KEY,
                            secret text
                            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            id INTEGER UNIQUE,
                            first_name text,
                            user_name text,
                            is_admin BOOLEAN,
                            date DATE
                            )""")
        connection.commit()


def get_message(identifier):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM messages WHERE id = {identifier} LIMIT 1""")
            res = cursor.fetchone()
    except:
        pass
    return res


def get_messages():
    res = []
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM messages""")
            res = cursor.fetchall()
    except:
        pass
    return res


def create_or_update_message(item):
    res = False
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO messages (id, first_name, user_name, message, date) VALUES {item}
                                ON CONFLICT(id) DO UPDATE SET first_name = excluded.first_name,
                                user_name = excluded.user_name, message = excluded.message, date = excluded.date""")
            connection.commit()
            res = True
    except:
        pass
    return res


def delete_message(identifier):
    res = False
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""DELETE FROM messages WHERE id = {identifier}""")
            connection.commit()
            res = True
    except:
        pass
    return res


def get_secret(identifier):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM secrets WHERE id = {identifier} LIMIT 1""")
            res = cursor.fetchone()
    except:
        pass
    return res


def get_secrets():
    res = []
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM secrets""")
            res = cursor.fetchall()
    except:
        pass
    return res


def create_or_update_secret(item):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO secrets(id, secret) VALUES (?, ?)", item)
            connection.commit()
            res = True
    except:
        pass
    return res


def delete_secret(identifier):
    res = False
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""DELETE FROM secrets WHERE id = {identifier}""")
            connection.commit()
            res = True
    except:
        pass
    return res


def get_user(identifier):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM users WHERE id = {identifier} LIMIT 1""")
            res = cursor.fetchone()
    except:
        pass
    return res


def get_users():
    res = []
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM users""")
            res = cursor.fetchall()
    except:
        pass
    return res


def create_or_update_user(item):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""INSERT INTO users (id, first_name, user_name, is_admin, date) VALUES {item}
                                ON CONFLICT(id) DO UPDATE SET first_name = excluded.first_name,
                                user_name = excluded.user_name, is_admin = excluded.is_admin, date = excluded.date""")
            connection.commit()
            res = True
    except:
        pass
    return res


def admin_remove(identifier):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""UPDATE users SET is_admin = 0 where id = {identifier} LIMIT 1""")
            connection.commit()
            res = True
    except:
        pass
    return res


def admin_add(identifier):
    res = None
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""UPDATE users SET is_admin = 1 where id = {identifier} LIMIT 1""")
            connection.commit()
            res = True
    except:
        pass
    return res


def add_users(items):
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            for item in items:
                cursor.execute(f"""INSERT INTO users (id, first_name, user_name, is_admin, date) VALUES {item}
                                ON CONFLICT(id) DO UPDATE SET first_name = excluded.first_name,
                                user_name = excluded.user_name""")
            connection.commit()
    except:
        pass


def delete_user(identifier):
    res = False
    try:
        with sqlite3.connect("database.db") as connection:
            cursor = connection.cursor()
            cursor.execute(f"""DELETE FROM users WHERE id = {identifier}""")
            connection.commit()
            res = True
    except:
        pass
    return res

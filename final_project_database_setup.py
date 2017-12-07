import psycopg2
import psycopg2.extras
from config import *

db_connection, db_cursor = None, None

def get_connection_and_cursor():
    global db_connection, db_cursor
    if not db_connection:
        try:
            if db_password != "":
                db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
                print("Success connecting to database")
            else:
                db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
        except:
            print("Unable to connect to the database. Check server and credentials.")
            sys.exit(1)

    if not db_cursor:
        db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

db_connection, db_cursor = get_connection_and_cursor()
print(db_connection, db_cursor)

def setup_database():

    db_cursor.execute("CREATE TABLE Sites(id SERIAL PRIMARY KEY, name VARCHAR(40))")
    db_cursor.execute("CREATE TABLE Headlines(id SERIAL PRIMARY KEY, title VARCHAR(128) NOT NULL UNIQUE, author VARCHAR(128), site_id INTEGER REFERENCES Sites(id) NOT NULL, url VARCHAR(255))")

    # Save all changes
    db_connection.commit()
    print('Setup database complete')

setup_database()

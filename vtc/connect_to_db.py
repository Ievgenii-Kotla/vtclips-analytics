import psycopg2
from psycopg2 import Error
import os


def connect_to_db():
    """ Connect to the main PostgreSQL database. """
    user, password, host, port, database = os.getenv("VC_conn_info").split(',')
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        print("Connected to the MAIN database successfully\n")
    except (Exception, Error) as error:
        print("Error while connecting to the MAIN database:", error)
        connection = None
    return connection


def connect_to_test_db():
    """ Connect to the test PostgreSQL database. """
    user, password, host, port, database = os.getenv("test_VC_v0.1_conn_info").split(',')
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        print("Connected to the TEST database successfully\n")
    except (Exception, Error) as error:
        print("Error while connecting to the TEST database:", error)
        connection = None
    return connection


def connection_close(connection):
    if not connection.closed:
        connection.close()
        print("Connection closed.\n")


# Main function
def main():
    # Connect to the database
    connection = connect_to_db()
    print("Connection: ", connection)
    if connection:
        connection.close()


if __name__ == "__main__":
    main()

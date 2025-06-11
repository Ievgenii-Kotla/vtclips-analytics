# first try to work with DB through python scripts
# Standalone script, that populates a 'talent' table in DB with talents info

from psycopg2 import Error
import datetime as dt
from vtc import connect_to_db


def pick_talent() -> str:
    """Returns the first name of a talent"""
    talent = 'Ouro'
    return talent


def pick_keyword(talent) -> str:
    keyword = ''
    return keyword
    pass


def pick_time_period(keyword) -> (dt.datetime, dt.datetime):
    pass


# Function to insert data into a table
def insert_data(connection, data_to_insert):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # SQL statement for inserting data into the table
        insert_query = """
        INSERT INTO talent (first_name_eng, last_name_eng, group_name, debut_datetime)
        SELECT %(name)s, %(sur)s, %(gen)s, %(debut)s
        WHERE 
        NOT EXISTS (
        SELECT first_name_eng FROM talent WHERE first_name_eng = %(name)s
        );
        """

        # Execute the SQL statement
        cursor.executemany(insert_query, data_to_insert)

        # Commit the transaction
        connection.commit()

        print("Data inserted successfully")
        print(f"Inserted {cursor.rowcount} rows")
    except (Exception, Error) as error:
        print("Error while inserting data:", error)
    finally:
        # Close the cursor and connection
        if connection:
            cursor.close()
            connection.close()
            print("Connection closed")


# Main function
def main():
    # TODO: Add a functionality that updates existing rows in case some new info is added
    data_to_insert = [
        {'name': 'Kiara', 'sur': 'Takanashi', 'gen': 'myth', 'debut': '2020-09-12 00:00:00+00'},
        {'name': 'Amelia', 'sur': 'Watson', 'gen': 'myth', 'debut': '2020-09-13 00:00:00+00'},
        {'name': "Ina'nis", 'sur': 'Ninomae', 'gen': 'myth', 'debut': '2020-09-13 00:00:00+00'},
        {'name': 'Gura', 'sur': 'Gawr', 'gen': 'myth', 'debut': '2020-09-13 00:00:00+00'},
        {'name': 'Calliope', 'sur': 'Mori', 'gen': 'myth', 'debut': '2020-09-12 00:00:00+00'},
        {'name': 'Kronii', 'sur': 'Ouro', 'gen': 'promise', 'debut': '2021-08-23 00:00:00+00'},
        {'name': 'Fauna', 'sur': 'Ceres', 'gen': 'promise', 'debut': '2021-08-23 00:00:00+00'},
        {'name': 'Mumei', 'sur': 'Nanashi', 'gen': 'promise', 'debut': '2021-08-23 00:00:00+00'},
        {'name': 'Baelz', 'sur': 'Hakos', 'gen': 'promise', 'debut': '2021-08-23 00:00:00+00'},
        {'name': 'Sana', 'sur': 'Tsukumo', 'gen': 'council', 'debut': '2021-08-23 00:00:00+00'},
        {'name': 'IRyS', 'sur': '', 'gen': 'promise', 'debut': '2021-07-11 00:00:00+00'},
        {'name': 'Bijou', 'sur': 'Koseki', 'gen': 'advent', 'debut': '2023-07-30 00:00:00+00'},
        {'name': 'Nerissa', 'sur': 'Ravencroft', 'gen': 'advent', 'debut': '2023-07-31 00:00:00+00'},
        {'name': 'Shiori', 'sur': 'Novella', 'gen': 'advent', 'debut': '2023-07-30 00:00:00+00'},
        {'name': 'Fuwawa', 'sur': 'Abyssgard', 'gen': 'advent', 'debut': '2023-07-31 00:00:00+00'},
        {'name': 'Mococo', 'sur': 'Abyssgard', 'gen': 'advent', 'debut': '2023-07-31 00:00:00+00'},
        {'name': 'Elizabeth', 'sur': 'Rose Bloodflame', 'gen': 'justice', 'debut': '2024-06-21 00:00:00+00'},
        {'name': 'Gigi', 'sur': 'Murin', 'gen': 'justice', 'debut': '2024-06-21 00:00:00+00'},
        {'name': 'Cecilia', 'sur': 'Immergreen', 'gen': 'justice', 'debut': '2024-06-22 00:00:00+00'},
        {'name': 'Raora', 'sur': 'Panthera', 'gen': 'justice', 'debut': '2024-06-22 00:00:00+00'},
    ]
    # Connect to the database
    connection = connect_to_db.connect_to_db()

    if connection:
        # Insert data into the table
        insert_data(connection, data_to_insert)


if __name__ == "__main__":
    main()

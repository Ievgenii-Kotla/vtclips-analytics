"""
DEPRECATED

Single use script that migrates some data from 'keyword' table to 'keyword_talent' table.
transition of the data to the new table is necessary to implement many-to-many relationship
between 'keyword' and 'talent' tables.
"""
import connect_to_db


def get_data(connection) -> list[tuple]:
    """Get necessary data from keyword table"""
    get_data_query = """
    SELECT keyword_id, talent_id
    FROM keyword;
    """
    cur = connection.cursor()
    cur.execute(get_data_query)
    data = cur.fetchall()
    cur.close()
    return data


def set_data(data: list[tuple], connection):
    set_data_query = """
    INSERT INTO keyword_talent (keyword_id, talent_id)
    VALUES (%s, %s)
    """
    cur = connection.cursor()
    cur.executemany(set_data_query, data)
    connection.commit()
    print('data is set')
    cur.close()


def main():
    connection = connect_to_db.connect_to_db()
    data = get_data(connection)
    print("data: \n")
    for i in data:
        print(i)
    answer = input("set data? y/n: ").strip()
    if answer == 'y':
        set_data(data, connection)
    else:
        print("setting the data was aborted")
    if connection:
        connection.close()


if __name__ == '__main__':
    main()

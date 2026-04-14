# first try to work with DB through python scripts
# Standalone script, that populates a 'talent' table in DB with talents info

import os
import datetime as dt
import psycopg2
from psycopg2 import Error

def main():
    data_to_insert = [
        {'name': 'Kiara', 'sur': 'Takanashi', 'gen': 'myth', 'debut': '2020-09-12 01:00:00+00', 'display_name': 'Takanashi Kiara'},
        {'name': 'Amelia', 'sur': 'Watson', 'gen': 'myth', 'debut': '2020-09-13 02:00:00+00', 'display_name': 'Amelia Watson'},
        {'name': "Ina'nis", 'sur': 'Ninomae', 'gen': 'myth', 'debut': '2020-09-13 00:00:00+00', 'display_name': "Ninomae Ina’nis"},
        {'name': 'Gura', 'sur': 'Gawr', 'gen': 'myth', 'debut': '2020-09-13 01:00:00+00', 'display_name': 'Gawr Gura'},
        {'name': 'Calliope', 'sur': 'Mori', 'gen': 'myth', 'debut': '2020-09-12 00:00:00+00', 'display_name': 'Mori Calliope'},
        {'name': 'Kronii', 'sur': 'Ouro', 'gen': 'promise', 'debut': '2021-08-23 02:00:00+00', 'display_name': 'Ouro Kronii'},
        {'name': 'Fauna', 'sur': 'Ceres', 'gen': 'promise', 'debut': '2021-08-23 01:00:00+00', 'display_name': 'Ceres Fauna'},
        {'name': 'Mumei', 'sur': 'Nanashi', 'gen': 'promise', 'debut': '2021-08-23 03:00:00+00', 'display_name': 'Nanashi Mumei'},
        {'name': 'Baelz', 'sur': 'Hakos', 'gen': 'promise', 'debut': '2021-08-23 00:04:00+00', 'display_name': 'Hakos Baelz'},
        {'name': 'Sana', 'sur': 'Tsukumo', 'gen': 'council', 'debut': '2021-08-23 00:00:00+00', 'display_name': 'Sana Tsukumo'},
        {'name': 'IRyS', 'sur': '', 'gen': 'promise', 'debut': '2021-07-11 00:00:00+00', 'display_name': 'IRyS'},
        {'name': 'Bijou', 'sur': 'Koseki', 'gen': 'advent', 'debut': '2023-07-30 01:00:00+00', 'display_name': 'Koseki Bijou'},
        {'name': 'Nerissa', 'sur': 'Ravencroft', 'gen': 'advent', 'debut': '2023-07-31 00:00:00+00', 'display_name': 'Nerissa Ravencroft'},
        {'name': 'Shiori', 'sur': 'Novella', 'gen': 'advent', 'debut': '2023-07-30 00:00:00+00', 'display_name': 'Shiori Novella'},
        {'name': 'Fuwawa', 'sur': 'Abyssgard', 'gen': 'advent', 'debut': '2023-07-31 01:00:00+00', 'display_name': 'Fuwawa Abyssgard'},
        {'name': 'Mococo', 'sur': 'Abyssgard', 'gen': 'advent', 'debut': '2023-07-31 01:00:00+00', 'display_name': 'Mococo Abyssgard'},
        {'name': 'Elizabeth', 'sur': 'Rose Bloodflame', 'gen': 'justice', 'debut': '2024-06-21 00:00:00+00', 'display_name': 'Elizabeth Rose Bloodflame'},
        {'name': 'Gigi', 'sur': 'Murin', 'gen': 'justice', 'debut': '2024-06-21 01:00:00+00', 'display_name': 'Gigi Murin'},
        {'name': 'Cecilia', 'sur': 'Immergreen', 'gen': 'justice', 'debut': '2024-06-22 00:00:00+00', 'display_name': 'Cecilia Immergreen'},
        {'name': 'Raora', 'sur': 'Panthera', 'gen': 'justice', 'debut': '2024-06-22 01:00:00+00', 'display_name': 'Raora Panthera'},
        {'name': 'HololiveEnglish', 'sur': None, 'gen': None, 'debut': '2020-09-07 00:00:00+00', 'display_name': 'Hololive English'},
    ]
    with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
        with connection.cursor() as cursor:
            # add talents that are not already added
            insert_query = """
            INSERT INTO talent (first_name_eng, last_name_eng, group_name, debut_datetime, display_name)
            SELECT %(name)s, %(sur)s, %(gen)s, %(debut)s, %(display_name)s
            WHERE NOT EXISTS (
                SELECT first_name_eng FROM talent WHERE first_name_eng = %(name)s
            );
            """
            try:
                cursor.executemany(insert_query, data_to_insert)
                connection.commit()
            except Exception as error:
                connection.rollback()
                print("Error while inserting data:", error)
            else:
                print("Data inserted successfully")
                print(f"Inserted {cursor.rowcount} rows")

if __name__ == "__main__":
    main()

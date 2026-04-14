import os
import psycopg2
import sys

display_names = [
    {'name': 'Kiara', 'display_name': 'Takanashi Kiara'},
    {'name': 'Amelia', 'display_name': 'Amelia Watson'},
    {'name': "Ina'nis", 'display_name': "Ninomae Ina’nis"},
    {'name': 'Gura', 'display_name': 'Gawr Gura'},
    {'name': 'Calliope', 'display_name': 'Mori Calliope'},
    {'name': 'Kronii', 'display_name': 'Ouro Kronii'},
    {'name': 'Fauna', 'display_name': 'Ceres Fauna'},
    {'name': 'Mumei', 'display_name': 'Nanashi Mumei'},
    {'name': 'Baelz', 'display_name': 'Hakos Baelz'},
    {'name': 'Sana', 'display_name': 'Sana Tsukumo'},
    {'name': 'IRyS', 'display_name': 'IRyS'},
    {'name': 'Bijou', 'display_name': 'Koseki Bijou'},
    {'name': 'Nerissa', 'display_name': 'Nerissa Ravencroft'},
    {'name': 'Shiori', 'display_name': 'Shiori Novella'},
    {'name': 'Fuwawa', 'display_name': 'Fuwawa Abyssgard'},
    {'name': 'Mococo', 'display_name': 'Mococo Abyssgard'},
    {'name': 'Elizabeth', 'display_name': 'Elizabeth Rose Bloodflame'},
    {'name': 'Gigi', 'display_name': 'Gigi Murin'},
    {'name': 'Cecilia', 'display_name': 'Cecilia Immergreen'},
    {'name': 'Raora', 'display_name': 'Raora Panthera'},
    {'name': 'HololiveEnglish', 'display_name': 'Hololive English'},
]
with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
    add_display_name = """
                           UPDATE talent
                           SET display_name = %(display_name)s
                           WHERE LOWER(first_name_eng) = LOWER(%(name)s)
                           RETURNING talent_id; 
                           """
    count = 0
    with connection.cursor() as cursor:
        for display_name in display_names:
            cursor.execute(add_display_name, display_name)
            result = cursor.fetchall()
            if len(result) != 1:
                connection.rollback()
                print(f"Error adding display_name for {display_name['name']}")
                print(f"Connection rolled back")
                sys.exit(1)
            count += 1
        connection.commit()
        print(f"Added display_names to {count} talents")
    print('Connection closed')
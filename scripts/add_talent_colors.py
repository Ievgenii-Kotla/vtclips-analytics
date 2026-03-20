import os
import psycopg2

color_values = [
    {"first_name":"calliope", "dark":"a1020b", "light":"c90d40", "neutral":"b50826"},
    {"first_name":"kiara", "dark":"dc3907", "light":"ff511c", "neutral":"ee4512"},
    {"first_name":"ina'nis", "dark":"3f3e69", "light":"62567e", "neutral":"514a74"},
    {"first_name":"amelia", "dark":"f2bd36", "light":"f8db92", "neutral":"f5cc64"},
    {"first_name":"gura", "dark":"3a69b2", "light":"5d81c7", "neutral":"4c75bd"},
    {"first_name":"irys", "dark":"991150", "light":"e10e5b", "neutral":"bd1056"},
    {"first_name":"kronii", "dark":"1d1797", "light":"6879c7", "neutral":"4348af"},
    {"first_name":"baelz", "dark":"fe3a2d", "light":"ff938d", "neutral":"ff675d"},
    {"first_name":"mumei", "dark":"c29371", "light":"dcc4b2", "neutral":"cfac92"},
    {"first_name":"fauna", "dark":"33ca66", "light":"b4e4c7", "neutral":"74d797"},
    {"first_name":"sana", "dark":"d583ab", "light":"e7bbd2", "neutral":"de9fbf"},
    {"first_name":"shiori", "dark":"8c80ae", "light":"b8a0cd", "neutral":"a290be"},
    {"first_name":"bijou", "dark":"4b43df", "light":"6e5bf4", "neutral":"5d4fea"},
    {"first_name":"nerissa", "dark":"1e27ac", "light":"2233fb", "neutral":"202dd4"},
    {"first_name":"fuwawa", "dark":"3f91dd", "light":"67b2ff", "neutral":"53a2ee"},
    {"first_name":"mococo", "dark":"ff82c9", "light":"f7a6ca", "neutral":"fb94ca"},
    {"first_name":"elizabeth", "dark":"97303a", "light":"c7383b", "neutral":"af343b"},
    {"first_name":"gigi", "dark":"cd9328", "light":"fdb440", "neutral":"e5a434"},
    {"first_name":"cecilia", "dark":"137a42", "light":"119a5c", "neutral":"128a4f"},
    {"first_name":"raora", "dark":"e75786", "light":"f087a9", "neutral":"ec6f98"},
    {"first_name":"hololiveenglish", "dark":"39abe0", "light":"c2f2fe", "neutral":"7ecfef"},
]


with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
    if connection:
        add_color_query = """
                               UPDATE talent
                               SET dark_color = %(dark)s, light_color = %(light)s, neutral_color = %(neutral)s
                               WHERE LOWER(first_name_eng) = LOWER(%(first_name)s)
                               RETURNING talent_id; 
                               """
        count = 0
        with connection.cursor() as cursor:
            for talent in color_values:
                cursor.execute(add_color_query, talent)
                result = cursor.fetchall()
                if len(result) != 1:
                    connection.rollback()
                    print(f"Error adding color for {talent['first_name']}")
                    print(f"Connection rolled back")
                    raise SystemExit
                count += 1
            connection.commit()
            print(f"Added colors to {count} talents")

    else:
        print('Could not connect to the database')
    print('Connection closed')
"""
add_keyword.py
A tool to add keywords to the DB.

"""

import datetime
from vtc import connect_to_db


# value = [keyword, talent_first_name, usage_enabled, priority, date_since_relevant, purity]
default_keywords = [
    ["@TakanashiKiara", "Kiara",True, 0, None, "pure"],
    ["UCHsx4Hqa-1ORjQTh9TYDhww" , "Kiara",True, 1, None, "pure"],
    ["@MoriCalliope", "Calliope", True, 0, None, "pure"],
    ["UCL_qhgtOy0dy1Agp8vkySQg", "Calliope", True, 1, None, "pure"],
    ["@WatsonAmelia","Amelia", True, 0, None, "pure"],
    ["UCyl1z3jo3XHR1riLFKG5UAg", "Amelia", True, 1, None, "pure"],
    ["@NinomaeInanis", "Ina'nis", True, 0, None, "pure"],
    ["UCMwGHR0BTZuLsmjY_NT5Pwg", "Ina'nis", True, 1, None, "pure"],
    ["@GawrGura", "Gura", True, 0, None, "pure"],
    ["UCoSrY_IQQVpmIRZ9Xf-y93g", "Gura", True, 1, None, "pure"],
    ["@IRyS", "IRyS", True, 0, None, "pure"],
    ["UC8rcEBzJSleTkf_-agPM20g", "IRys", True, 1, None, "pure"],
    ["@CeresFauna", "Fauna", True, 0, None, "pure"],
    ["UCO_aKKYxn4tvrqPjcTzZ6EQ", "Fauna", True, 1, None, "pure"],
    ["@NanashiMumei", "Mumei", True, 0, None, "pure"],
    ["UC3n5uGu18FoCy23ggWWp8tA", "Mumei", True, 1, None, "pure"],
    ["@HakosBaelz", "Baelz", True, 0, None, "pure"],
    ["UCgmPnx-EEeOrZSg5Tiw7ZRQ", "Baelz", True, 1, None, "pure"],
    ["@OuroKronii", "Kronii", True, 0, None, "pure"],
    ["UCmbs8T6MWqUHP1tIQvSgKrg", "Kronii", True, 1, None, "pure"],
    ["@TsukumoSana", "Sana", True, 0, None, "pure"],
    ["UCsUj0dszADCGbF3gNrQEuSQ", "Sana", True, 1, None, "pure"],
    ["@KosekiBijou", "Bijou", True, 0, None, "pure"],
    ["UC9p_lqQ0FEDz327Vgf5JwqA", "Bijou", True, 1, None, "pure"],
    ["@ShioriNovella", "Shiori", True, 0, None, "pure"],
    ["UCgnfPPb9JI3e9A4cXHnWbyg", "Shiori", True, 1, None, "pure"],
    ["@NerissaRavencroft", "Nerissa", True, 0, None, "pure"],
    ["UC_sFNM0z0MWm9A6WlKPuMMg", "Nerissa", True, 1, None, "pure"],
    ["@holoen_gigimurin","Gigi", True, 0, None, "pure"],
    ["UCDHABijvPBnJm7F-KlNME3w", "Gigi", True, 1, None, "pure"],
    ["@holoen_erbloodflame", "Elizabeth", True, 0, None, "pure"],
    ["UCW5uhrG1eCBYditmhL0Ykjw", "Elizabeth", True, 1, None, "pure"],
    ["@holoen_ceciliaimmergreen", "Cecilia", True, 0, None, "pure"],
    ["UCvN5h1ShZtc7nly3pezRayg", "Cecilia", True, 1, None, "pure"],
    ["@holoen_raorapanthera", "Raora", True, 0, None, "pure"],
    ["UCl69AEx4MdqMZH7Jtsm7Tig", "Raora", True, 1, None, "pure"],
    ["@FUWAMOCOch", "Fuwawa", True, 0, None, "pure"],
    ["@FUWAMOCOch", "Mococo", True, 0, None, "pure"],
    ["UCt9H_RpQzhxzlyBxFqrdHqA", "Fuwawa", True, 1, None, "pure"],
    ["UCt9H_RpQzhxzlyBxFqrdHqA", "Mococo", True, 1, None, "pure"],
]


def show_info():
    """
    Display info about what data will be requested from the user.

    Guidelines for priority values:
    0 - channel id
    1 - channel alt id
    2 - firstname last name
    3 - last name first name
    4 - first name
    5 - last name
    6 - middle name
    7 - nicknames popular
    8 - nicknames rare
    9 - other
    """
    print("keyword:                 keyword itself",
          "talent's name:           first name of the associated talent",
          "usage enabled:           y or n, default = y",
          "priority:                top is 0, low is 9, default = 9",
          "date since relevant:     date since keyword became relevant;",
          "                         format: 'YYYY-MM-DD'; ",
          "                         default = 3 months before talent's debut",
          "purity:                  pure, mixed or dirt. Estimation of how relevant search result is",
          "answers are not case sensitive",
          "enter empty line for a default value (where applicable)\n",
          sep='\n')


def input_values():
    """ Prompt the user to enter all the necessary info. Then pack it and return."""
    # todo: add an option to discard input and retry
    # todo: add an option to input the next keyword
    # todo: add check on empty string
    # todo: add getting a default value when necessary
    # todo: add behavior on invalid input
    # todo: add constrains for in

    # prompt the user to enter all the necessary info.
    keyword = input("keyword: ").strip().lower()
    talent = input("talent's name: ").strip().lower()
    usage_enabled = input("usage_enabled y/n: ").strip().lower()
    priority = input("priority: ").strip()
    date_since_relevant = input("date since relevant: ").strip()
    purity = input("purity: ").strip().lower()
    values = [keyword, talent, usage_enabled, priority, date_since_relevant, purity]
    print()
    return values


def prepare_values(values: list, connection):
    """ Adapt the values to the necessary state to write to db.
    - default values when requested
    - shortcuts for some options
    """
    values = values[:]

    # Prepare talent_id value. Change talent's name to talent's id.
    retrieve_fk_query = """
    SELECT talent_id
    FROM talent AS t
    WHERE lower(t.first_name_eng) = %s
    """
    cur = connection.cursor()
    cur.execute(retrieve_fk_query, (values[1],))
    # todo: check if more than one value
    # todo: use context manager for the cursor
    if cur.rowcount > 1:
        print('There is more than one talent with this name')  # todo: raise an error?
    elif cur.rowcount == 0:
        # todo: check if rowcount() returns zero when there are zero rows
        print(f'There are no talents in the DB with the name {values[1]}. Talent id will be set to NULL')
        values[1] = None
    else:
        values[1] = cur.fetchone()[0]
    cur.close()

    # Prepare usage_enabled value.
    if not values[2]:
        values[2] = True
    elif values[2][0] == "y":
        values[2] = True
    else:
        values[2] = False

    # Prepare priority value.
    if not values[3]:
        values[3] = 9
    else:
        values[3] = int(values[3])

    # TODO: figure out how I would test all of this
    # todo: fix error when no talent found
    # Prepare date_since_relevant value.
    if not values[4]:
        retrieve_debut_date_query = """
        SELECT debut_datetime - INTERVAL '3 months' AS date_since_relevant
        FROM talent
        WHERE talent_id = %s
        """
        # todo: use context manager for the cursor
        cur = connection.cursor()
        cur.execute(retrieve_debut_date_query, (values[1],))
        if not cur.rowcount:
            print("Since this keyword is not bound to any talent, "
                  "you must enter the date when this keyword became relevant.")
        values[4] = cur.fetchone()[0]
        cur.close()
    else:
        values[4] = datetime.datetime.fromisoformat(values[4])

    # todo: add a feature that would allow using only the first letter of a word
    # Prepare purity value.
    if values[5] not in ['pure', 'mixed', 'dirt', 'p', 'm', 'd']:
        values[5] = None
        print('Priority is set to NULL')
    elif values[5] in ['p', 'm', 'd']:
        vmap = {'p': 'pure', 'm': 'mixed', 'd': 'dirt'}
        values[5] = vmap[values[5]]

    return values


def show_values(values):
    """ Display resulting values that will be written to the db. """
    print("The keyword with the following values is ready to be added:")
    print(f"keyword: {values[0]}\n"
          f"talent's id: {values[1]}\n"
          f"usage enabled: {values[2]}\n"
          f"priority: {values[3]}\n"
          f"date since relevant: {values[4]}\n"
          f"purity: {values[5]}\n")


def write_to_keyword(values: list, connection):
    """ Write main info about the keyword to the 'keyword' table of the db. """
    # Check if keyword already exists in the DB.
    check_keyword_unique_query = """
    SELECT *
    FROM keyword
    WHERE keyword_word = %s;
    """
    cur = connection.cursor()
    cur.execute(check_keyword_unique_query, (values[0],))
    if cur.fetchone():
        print("The keyword already exists in the db.")
        cur.close()
        return None

    insert_query = """
    INSERT INTO keyword(keyword_word, usage_enabled, priority, date_since_relevant, purity)
    VALUES (%s, %s, %s, %s, %s);
    """
    # todo: use context manager for the cursor
    cur = connection.cursor()
    cur.execute(insert_query, (values[0], values[2], values[3], values[4], values[5]))
    cur.close()
    print('Keyword added successfully.')


def write_to_keyword_talent(values: list, connection):
    """ Write the relation between the keyword and the talent to the 'keyword_talent' junction table of the db. """
    # Get keyword_id for the keyword.
    get_keyword_id_query = """
    SELECT keyword_id
    FROM keyword
    WHERE keyword_word = %s;
    """
    cur = connection.cursor()
    cur.execute(get_keyword_id_query, (values[0],))
    values.append(cur.fetchone()[0])

    # Check if the record already exists in the junction table.
    check_record_unique_query = """
    SELECT *
    FROM keyword_talent
    WHERE keyword_id = %s AND talent_id = %s;
    """
    cur.execute(check_record_unique_query, (values[6], values[1]))
    if cur.fetchone():
        print("This combination of a talent and a keyword already exists in the db.")
        cur.close()
        return None

    # Add new record into keyword_talent junction table.
    set_keyword_talent = """
    INSERT INTO keyword_talent(keyword_id, talent_id)
    VALUES (%s, %s);
    """
    cur.execute(set_keyword_talent, (values[6], values[1]))
    print("Keyword-talent relation added successfully.")
    cur.close()


def main():
    connection = connect_to_db.connect_to_db()
    if connection:
        while True:
            show_info()
            values_raw = input_values()
            values_clean = prepare_values(values_raw, connection)
            show_values(values_clean)
            if not input('Enter an empty line to write to db, enter anything to discard. '):
                write_to_keyword(values_clean, connection)
                write_to_keyword_talent(values_clean, connection)
                connection.commit()
            if input('Enter an empty line to continue, enter anything to quit. '):
                break
    else:
        print('Could not connect to the database')
    connection.close()
    print('Connection closed')


main()

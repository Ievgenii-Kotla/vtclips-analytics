"""
add_keyword.py
A tool to add keywords to the DB.

"""

import datetime
from vtc import connect_to_db


# value = [keyword, talent_first_name, usage_enabled, priority, date_since_relevant, purity]
default_keywords = [
    ['@TakanashiKiara', 'Kiara', 'y', 0, '', 'pure'],
    ['@MoriCalliope', 'Calliope', 'y', 0, '', 'pure'],
    ['@WatsonAmelia', 'Amelia', 'y', 0, '', 'pure'],
    ['@NinomaeInanis', "Ina'nis", 'y', 0, '', 'pure'],
    ['@GawrGura', 'Gura', 'y', 0, '', 'pure'],
    ['@IRyS', 'IRyS', 'y', 0, '', 'pure'],
    ['@CeresFauna', 'Fauna', 'y', 0, '', 'pure'],
    ['@NanashiMumei', 'Mumei', 'y', 0, '', 'pure'],
    ['@HakosBaelz', 'Baelz', 'y', 0, '', 'pure'],
    ['@OuroKronii', 'Kronii', 'y', 0, '', 'pure'],
    ['@TsukumoSana', 'Sana', 'y', 0, '', 'pure'],
    ['@KosekiBijou', 'Bijou', 'y', 0, '', 'pure'],
    ['@ShioriNovella', 'Shiori', 'y', 0, '', 'pure'],
    ['@NerissaRavencroft', 'Nerissa', 'y', 0, '', 'pure'],
    ['@holoen_gigimurin', 'Gigi', 'y', 0, '', 'pure'],
    ['@holoen_erbloodflame', 'Elizabeth', 'y', 0, '', 'pure'],
    ['@holoen_ceciliaimmergreen', 'Cecilia', 'y', 0, '', 'pure'],
    ['@holoen_raorapanthera', 'Raora', 'y', 0, '', 'pure'],
    ['@FUWAMOCOch', 'Fuwawa', 'y', 0, '', 'pure'],
    ['@FUWAMOCOch', 'Mococo', 'y', 0, '', 'pure'],
    ['UCHsx4Hqa-1ORjQTh9TYDhww', 'Kiara', 'y', 1, '', 'pure'],
    ['UCL_qhgtOy0dy1Agp8vkySQg', 'Calliope', 'y', 1, '', 'pure'],
    ['UCyl1z3jo3XHR1riLFKG5UAg', 'Amelia', 'y', 1, '', 'pure'],
    ['UCMwGHR0BTZuLsmjY_NT5Pwg', "Ina'nis", 'y', 1, '', 'pure'],
    ['UCoSrY_IQQVpmIRZ9Xf-y93g', 'Gura', 'y', 1, '', 'pure'],
    ['UC8rcEBzJSleTkf_-agPM20g', 'IRys', 'y', 1, '', 'pure'],
    ['UCO_aKKYxn4tvrqPjcTzZ6EQ', 'Fauna', 'y', 1, '', 'pure'],
    ['UC3n5uGu18FoCy23ggWWp8tA', 'Mumei', 'y', 1, '', 'pure'],
    ['UCgmPnx-EEeOrZSg5Tiw7ZRQ', 'Baelz', 'y', 1, '', 'pure'],
    ['UCmbs8T6MWqUHP1tIQvSgKrg', 'Kronii', 'y', 1, '', 'pure'],
    ['UCsUj0dszADCGbF3gNrQEuSQ', 'Sana', 'y', 1, '', 'pure'],
    ['UC9p_lqQ0FEDz327Vgf5JwqA', 'Bijou', 'y', 1, '', 'pure'],
    ['UCgnfPPb9JI3e9A4cXHnWbyg', 'Shiori', 'y', 1, '', 'pure'],
    ['UC_sFNM0z0MWm9A6WlKPuMMg', 'Nerissa', 'y', 1, '', 'pure'],
    ['UCDHABijvPBnJm7F-KlNME3w', 'Gigi', 'y', 1, '', 'pure'],
    ['UCW5uhrG1eCBYditmhL0Ykjw', 'Elizabeth', 'y', 1, '', 'pure'],
    ['UCvN5h1ShZtc7nly3pezRayg', 'Cecilia', 'y', 1, '', 'pure'],
    ['UCl69AEx4MdqMZH7Jtsm7Tig', 'Raora', 'y', 1, '', 'pure'],
    ['UCt9H_RpQzhxzlyBxFqrdHqA', 'Fuwawa', 'y', 1, '', 'pure'],
    ['UCt9H_RpQzhxzlyBxFqrdHqA', 'Mococo', 'y', 1, '', 'pure'],
    ['KiaraTakanashi', 'Kiara', 'y', 2, '', 'pure'],
    ['AmeliaWatson', 'Amelia', 'y', 2, '', 'pure'],
    ["Ina'nisNinomae", "Ina'nis", 'y', 2, '', 'pure'],
    ['GuraGawr', 'Gura', 'y', 2, '', 'pure'],
    ['CalliopeMori', 'Calliope', 'y', 2, '', 'pure'],
    ['KroniiOuro', 'Kronii', 'y', 2, '', 'pure'],
    ['FaunaCeres', 'Fauna', 'y', 2, '', 'pure'],
    ['MumeiNanashi', 'Mumei', 'y', 2, '', 'pure'],
    ['BaelzHakos', 'Baelz', 'y', 2, '', 'pure'],
    ['SanaTsukumo', 'Sana', 'y', 2, '', 'pure'],
    ['IRyS', 'IRyS', 'y', 2, '', 'dirty'],
    ['BijouKoseki', 'Bijou', 'y', 2, '', 'pure'],
    ['NerissaRavencroft', 'Nerissa', 'y', 2, '', 'pure'],
    ['ShioriNovella', 'Shiori', 'y', 2, '', 'pure'],
    ['FuwawaAbyssgard', 'Fuwawa', 'y', 2, '', 'pure'],
    ['MococoAbyssgard', 'Mococo', 'y', 2, '', 'pure'],
    ['ElizabethRoseBloodflame', 'Elizabeth', 'y', 2, '', 'pure'],
    ['GigiMurin', 'Gigi', 'y', 2, '', 'pure'],
    ['CeciliaImmergreen', 'Cecilia', 'y', 2, '', 'pure'],
    ['RaoraPanthera', 'Raora', 'y', 2, '', 'pure'],
    ['TakanashiKiara', 'Kiara', 'y', 3, '', 'pure'],
    ['WatsonAmelia', 'Amelia', 'y', 3, '', 'pure'],
    ["NinomaeIna'nis", "Ina'nis", 'y', 3, '', 'pure'],
    ['GawrGura', 'Gura', 'y', 3, '', 'pure'],
    ['MoriCalliope', 'Calliope', 'y', 3, '', 'pure'],
    ['OuroKronii', 'Kronii', 'y', 3, '', 'pure'],
    ['CeresFauna', 'Fauna', 'y', 3, '', 'pure'],
    ['NanashiMumei', 'Mumei', 'y', 3, '', 'pure'],
    ['HakosBaelz', 'Baelz', 'y', 3, '', 'pure'],
    ['TsukumoSana', 'Sana', 'y', 3, '', 'pure'],
    ['IRyS', 'IRyS', 'y', 3, '', 'dirty'],
    ['KosekiBijou', 'Bijou', 'y', 3, '', 'pure'],
    ['RavencroftNerissa', 'Nerissa', 'y', 3, '', 'pure'],
    ['NovellaShiori', 'Shiori', 'y', 3, '', 'pure'],
    ['AbyssgardFuwawa', 'Fuwawa', 'y', 3, '', 'pure'],
    ['AbyssgardMococo', 'Mococo', 'y', 3, '', 'pure'],
    ['BloodflameRoseElizabeth', 'Elizabeth', 'y', 3, '', 'pure'],
    ['MurinGigi', 'Gigi', 'y', 3, '', 'pure'],
    ['ImmergreenCecilia', 'Cecilia', 'y', 3, '', 'pure'],
    ['PantheraRaora', 'Raora', 'y', 3, '', 'pure'],
]


def show_info():
    """
    Display info about what data will be requested from the user.

    Guidelines for priority values:
    0 - channel id (@channelID)
    1 - channel alt id (line of random characters)
    2 - firstname last name
    3 - last name first name
    4 - first name
    5 - last name
    6 - middle name
    7 - channel alt id without '@'
    100+ - nicknames popular
    200+ - nicknames rare
    300+ - other
    """
    print("keyword:                 keyword itself",
          "talent's name:           first name of the associated talent",
          "usage enabled:           y or n, default = y",
          "priority:                top is 0, low is 9, default = 9",
          "date since relevant:     date since keyword became relevant;",
          "                         format: 'YYYY-MM-DD'; ",
          "                         default = 1 month before talent's debut",
          "purity:                  pure, mixed or dirty. Estimation of how relevant search result is",
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
    if values[2] == "":
        values[2] = True
    elif values[2][0] == "y":
        values[2] = True
    else:
        values[2] = False

    # Prepare priority value.
    if values[3] == "":
        values[3] = 9
    else:
        values[3] = int(values[3])

    # TODO: figure out how I would test all of this
    # todo: fix error when no talent found
    # Prepare date_since_relevant value.
    if values[4] == "":
        retrieve_debut_date_query = """
        SELECT debut_datetime - INTERVAL '1 months' AS date_since_relevant
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
    if values[5] not in ['pure', 'mixed', 'dirty', 'p', 'm', 'd']:
        values[5] = None
        print('Priority is set to NULL')
    elif values[5] in ['p', 'm', 'd']:
        vmap = {'p': 'pure', 'm': 'mixed', 'd': 'dirty'}
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
        print(f"The keyword already exists in the db.    "
              f"keyword: {values[0]}")
        cur.close()
        return 0

    insert_query = """
    INSERT INTO keyword(keyword_word, usage_enabled, priority, date_since_relevant, purity)
    VALUES (%s, %s, %s, %s, %s);
    """
    # todo: use context manager for the cursor
    cur = connection.cursor()
    cur.execute(insert_query, (values[0], values[2], values[3], values[4], values[5]))
    cur.close()
    print('Keyword added successfully.')
    return 1


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
        print(f"This combination of a talent and a keyword already exists in the db.    "
              f"keyword: {values[0]}; talent_id: {values[1]}")
        cur.close()
        return 0

    # Add new record into keyword_talent junction table.
    set_keyword_talent = """
    INSERT INTO keyword_talent(keyword_id, talent_id)
    VALUES (%s, %s);
    """
    cur.execute(set_keyword_talent, (values[6], values[1]))
    print("Keyword-talent relation added successfully.")
    cur.close()
    return 1


def main():
    connection = connect_to_db.connect_to_db()
    if connection:
        choice = input("0 - add default keywords\n1 - add keywords manually\n: ")
        if choice == "0":
            default_keywords_lower_case = [[item.lower() if isinstance(item, str) else item for item in sublist]
                                           for sublist in default_keywords]
            keyword_counter = 0
            keyword_talent_counter = 0
            for keyword in default_keywords_lower_case:
                values_clean = prepare_values(keyword, connection)
                keyword_counter += write_to_keyword(values_clean, connection)
                keyword_talent_counter += write_to_keyword_talent(values_clean, connection)
                connection.commit()
            print(f"Added {keyword_counter} keywords, and {keyword_talent_counter} keyword-talent links")
        elif choice == "1":
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

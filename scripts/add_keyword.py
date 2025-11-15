"""
add_keyword.py
A tool to add keywords to the DB.

"""

import datetime
import os
import psycopg2


# value = [keyword, talent_first_name, usage_enabled (for search endpoint?), priority, date_since_relevant, purity]
keywords = {
    'handle': [
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
    ],
    'channel_id': [
        ['UCHsx4Hqa-1ORjQTh9TYDhww', 'Kiara', 'y', 1, '', 'pure'],
        ['UCL_qhgtOy0dy1Agp8vkySQg', 'Calliope', 'y', 1, '', 'pure'],
        ['UCyl1z3jo3XHR1riLFKG5UAg', 'Amelia', 'y', 1, '', 'pure'],
        ['UCMwGHR0BTZuLsmjY_NT5Pwg', "Ina'nis", 'y', 1, '', 'pure'],
        ['UCoSrY_IQQVpmIRZ9Xf-y93g', 'Gura', 'y', 1, '', 'pure'],
        ['UC8rcEBzJSleTkf_-agPM20g', 'IRyS', 'y', 1, '', 'pure'],
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
    ],
    'first_middle_last_name' : [
        ['KiaraTakanashi', 'Kiara', 'y', 2, '', 'pure'],
        ['AmeliaWatson', 'Amelia', 'y', 2, '', 'pure'],
        ["Ina'nisNinomae", "Ina'nis", 'y', 2, '', 'pure'],
        ["InanisNinomae", "Ina'nis", 'n', 2, '', 'pure'],
        ['GuraGawr', 'Gura', 'y', 2, '', 'pure'],
        ['CalliopeMori', 'Calliope', 'y', 2, '', 'pure'],
        ['KroniiOuro', 'Kronii', 'y', 2, '', 'pure'],
        ['FaunaCeres', 'Fauna', 'y', 2, '', 'pure'],
        ['MumeiNanashi', 'Mumei', 'y', 2, '', 'pure'],
        ['BaelzHakos', 'Baelz', 'y', 2, '', 'pure'],
        ['SanaTsukumo', 'Sana', 'y', 2, '', 'pure'],
        # ['IRyS', 'IRyS', 'n', 2, '', 'dirty'],  excluding to avoid overcounting
        ['BijouKoseki', 'Bijou', 'y', 2, '', 'pure'],
        ['NerissaRavencroft', 'Nerissa', 'y', 2, '', 'pure'],
        ['ShioriNovella', 'Shiori', 'y', 2, '', 'pure'],
        ['FuwawaAbyssgard', 'Fuwawa', 'y', 2, '', 'pure'],
        ['MococoAbyssgard', 'Mococo', 'y', 2, '', 'pure'],
        ['ElizabethRoseBloodflame', 'Elizabeth', 'y', 2, '', 'pure'],
        ['GigiMurin', 'Gigi', 'y', 2, '', 'pure'],
        ['CeciliaImmergreen', 'Cecilia', 'y', 2, '', 'pure'],
        ['RaoraPanthera', 'Raora', 'y', 2, '', 'pure'],
    ],
    'last_middle_first_name': [
        ['TakanashiKiara', 'Kiara', 'y', 3, '', 'pure'],
        ['WatsonAmelia', 'Amelia', 'y', 3, '', 'pure'],
        ["NinomaeIna'nis", "Ina'nis", 'y', 3, '', 'pure'],
        ["NinomaeInanis", "Ina'nis", 'n', 3, '', 'pure'],
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
    ],
    'first_middle_last_name_spaced': [
        ['Kiara Takanashi', 'Kiara', 'n', 4, '', 'pure'],
        ['Amelia Watson', 'Amelia', 'n', 4, '', 'pure'],
        ["Ina'nis Ninomae", "Ina'nis", 'n', 4, '', 'pure'],
        ["Inanis Ninomae", "Ina'nis", 'n', 4, '', 'pure'],
        ['Gura Gawr', 'Gura', 'n', 4, '', 'pure'],
        ['Calliope Mori', 'Calliope', 'n', 4, '', 'pure'],
        ['Kronii Ouro', 'Kronii', 'n', 4, '', 'pure'],
        ['Fauna Ceres', 'Fauna', 'n', 4, '', 'pure'],
        ['Mumei Nanashi', 'Mumei', 'n', 4, '', 'pure'],
        ['Baelz Hakos', 'Baelz', 'n', 4, '', 'pure'],
        ['Sana Tsukumo', 'Sana', 'n', 4, '', 'pure'],
        # ['IRyS', 'IRyS', 'n', 4, '', 'dirty'],  excluding to avoid overcounting
        ['Bijou Koseki', 'Bijou', 'n', 4, '', 'pure'],
        ['Nerissa Ravencroft', 'Nerissa', 'n', 4, '', 'pure'],
        ['Shiori Novella', 'Shiori', 'n', 4, '', 'pure'],
        ['Fuwawa Abyssgard', 'Fuwawa', 'n', 4, '', 'pure'],
        ['Mococo Abyssgard', 'Mococo', 'n', 4, '', 'pure'],
        ['Elizabeth Rose Bloodflame', 'Elizabeth', 'n', 4, '', 'pure'],
        ['Gigi Murin', 'Gigi', 'n', 4, '', 'pure'],
        ['Cecilia Immergreen', 'Cecilia', 'n', 4, '', 'pure'],
        ['Raora Panthera', 'Raora', 'n', 4, '', 'pure'],
    ],
    'last_middle_first_name_spaced': [
        ['Takanashi Kiara', 'Kiara', 'n', 5, '', 'pure'],
        ['Watson Amelia', 'Amelia', 'n', 5, '', 'pure'],
        ["Ninomae Ina'nis", "Ina'nis", 'n', 5, '', 'pure'],
        ["Ninomae Inanis", "Ina'nis", 'n', 5, '', 'pure'],
        ['Gawr Gura', 'Gura', 'n', 5, '', 'pure'],
        ['Mori Calliope', 'Calliope', 'n', 5, '', 'pure'],
        ['Ouro Kronii', 'Kronii', 'n', 5, '', 'pure'],
        ['Ceres Fauna', 'Fauna', 'n', 5, '', 'pure'],
        ['Nanashi Mumei', 'Mumei', 'n', 5, '', 'pure'],
        ['Hakos Baelz', 'Baelz', 'n', 5, '', 'pure'],
        ['Tsukumo Sana', 'Sana', 'n', 5, '', 'pure'],
        # ['IRyS', 'IRyS', 'n', 5, '', 'dirty'],  excluded in an attempt to balance points across talents
        ['Koseki Bijou', 'Bijou', 'n', 5, '', 'pure'],
        ['Ravencroft Nerissa', 'Nerissa', 'n', 5, '', 'pure'],
        ['Novella Shiori', 'Shiori', 'n', 5, '', 'pure'],
        ['Abyssgard Fuwawa', 'Fuwawa', 'n', 5, '', 'pure'],
        ['Abyssgard Mococo', 'Mococo', 'n', 5, '', 'pure'],
        ['Bloodflame Rose Elizabeth', 'Elizabeth', 'n', 5, '', 'pure'],
        ['Murin Gigi', 'Gigi', 'n', 5, '', 'pure'],
        ['Immergreen Cecilia', 'Cecilia', 'n', 5, '', 'pure'],
        ['Panthera Raora', 'Raora', 'n', 5, '', 'pure'],
    ],
    'first_name': [
        ['kiara', 'Kiara', 'n', 6, '', 'pure'],
        ['calliope', 'Calliope', 'n', 6, '', 'pure'],
        ['amelia', 'Amelia', 'n', 6, '', 'pure'],
        ["ina'nis", "Ina'nis", 'n', 6, '', 'pure'],
        ["inanis", "Ina'nis", 'n', 6, '', 'pure'],
        ['gura', 'Gura', 'n', 6, '', 'pure'],
        ['irys', 'IRyS', 'n', 6, '', 'pure'],
        ['fauna', 'Fauna', 'n', 6, '', 'pure'],
        ['mumei', 'Mumei', 'n', 6, '', 'pure'],
        ['baelz', 'Baelz', 'n', 6, '', 'pure'],
        ['kronii', 'Kronii', 'n', 6, '', 'pure'],
        ['sana', 'Sana', 'n', 6, '', 'pure'],
        ['bijou', 'Bijou', 'n', 6, '', 'pure'],
        ['shiori', 'Shiori', 'n', 6, '', 'pure'],
        ['nerissa', 'Nerissa', 'n', 6, '', 'pure'],
        ['gigi', 'Gigi', 'n', 6, '', 'pure'],
        ['elizabeth', 'Elizabeth', 'n', 6, '', 'pure'],
        ['cecilia', 'Cecilia', 'n', 6, '', 'pure'],
        ['raora', 'Raora', 'n', 6, '', 'pure'],
        ['fuwawa', 'Fuwawa', 'n', 6, '', 'pure'],
        ['mococo', 'Mococo', 'n', 6, '', 'pure'],
    ],
    'last_name': [
        ['takanashi', 'Kiara', 'n', 7, '', 'pure'],
        ['mori', 'Calliope', 'n', 7, '', 'pure'],
        ['watson', 'Amelia', 'n', 7, '', 'pure'],
        ['ninomae', "Ina'nis", 'n', 7, '', 'pure'],
        ['gawr', 'Gura', 'n', 7, '', 'pure'],
        # ['irys', 'IRyS', 'n', 7, '', 'pure'],  excluding to avoid overcounting
        ['ceres', 'Fauna', 'n', 7, '', 'pure'],
        ['nanashi', 'Mumei', 'n', 7, '', 'pure'],
        ['hakos', 'Baelz', 'n', 7, '', 'pure'],
        ['ouro', 'Kronii', 'n', 7, '', 'pure'],
        ['tsukumo', 'Sana', 'n', 7, '', 'pure'],
        ['koseki', 'Bijou', 'n', 7, '', 'pure'],
        ['novella', 'Shiori', 'n', 7, '', 'pure'],
        ['ravencroft', 'Nerissa', 'n', 7, '', 'pure'],
        ['murin', 'Gigi', 'n', 7, '', 'pure'],
        ['bloodflame', 'Elizabeth', 'n', 7, '', 'pure'],
        ['Immergreen', 'Cecilia', 'n', 7, '', 'pure'],
        ['panthera', 'Raora', 'n', 7, '', 'pure'],
        ['abyssgard', 'Fuwawa', 'n', 7, '', 'pure'],
        ['abyssgard', 'Mococo', 'n', 7, '', 'pure'],
    ],
    'middle_name': [

    ],
    'nickname_popular': [
        ['kiwawa', 'Kiara', 'n', 9, '', 'pure'],
        ['calli', 'Calliope', 'n', 9, '', 'pure'],
        ["ina", "Ina'nis", 'n', 9, '', 'pure'],
        ['bae', 'Baelz', 'n', 9, '', 'pure'],
        ['biboo', 'Bijou', 'n', 9, '', 'pure'],
        ['rissa', 'Nerissa', 'n', 9, '', 'pure'],
        ['liz', 'Elizabeth', 'n', 9, '', 'pure'],
        ['ceci', 'Cecilia', 'n', 9, '', 'pure'],
        ['cece', 'Cecilia', 'n', 9, '', 'pure'],
    ],
    'nickname_somewhat_common': [

    ],
    'nickname_rare': [

    ],
    'first_name_in_japanese': [
        ['キアラ', 'Kiara', 'n', 26, '', 'pure'],
        ['カリオペ', 'Calliope', 'n', 26, '', 'pure'],
        ['アメリア', 'Amelia', 'n', 26, '', 'pure'],
        # ["栖", "Ina'nis", 'n', 26, '', 'pure'],  some false matches
        # ['ぐら', 'Gura', 'n', 26, '', 'pure'],  matches with hologra
        ['アイリス', 'IRyS', 'n', 26, '', 'pure'],
        ['ファウナ', 'Fauna', 'n', 26, '', 'pure'],
        ['ムメイ', 'Mumei', 'n', 26, '', 'pure'],
        ['ベールズ', 'Baelz', 'n', 26, '', 'pure'],
        ['クロニー', 'Kronii', 'n', 26, '', 'pure'],
        ['佐命', 'Sana', 'n', 26, '', 'pure'],
        ['ビジュ―', 'Bijou', 'n', 26, '', 'pure'],
        ['ビブー', 'Bijou', 'n', 26, '', 'pure'],  # it's a nickname, should be in japanese nickname category, but oh well
        ['シオリ', 'Shiori', 'n', 26, '', 'pure'],
        ['ネリッサ', 'Nerissa', 'n', 26, '', 'pure'],
        # ['ジジ', 'Gigi', 'n', 26, '', 'pure'],  some false matches
        ['エリザベス', 'Elizabeth', 'n', 26, '', 'pure'],
        ['セシリア', 'Cecilia', 'n', 26, '', 'pure'],
        ['ラオーラ', 'Raora', 'n', 26, '', 'pure'],
        ['フワワ', 'Fuwawa', 'n', 26, '', 'pure'],
        ['モココ', 'Mococo', 'n', 26, '', 'pure'],
    ],
    'last_name_in_japanese': [
        ['小鳥遊', 'Kiara', 'n', 27, '', 'pure'],
        # ['森', 'Calliope', 'n', 27, '', 'pure'], too generic
        ['ワトソン', 'Amelia', 'n', 27, '', 'pure'],
        ['一伊那尓', "Ina'nis", 'n', 27, '', 'pure'],
        ['がうる', 'Gura', 'n', 27, '', 'pure'],
        # ['irys', 'IRyS', 'n', 27, '', 'pure'],  excluding to avoid overcounting
        ['セレス', 'Fauna', 'n', 27, '', 'pure'],
        ['七詩', 'Mumei', 'n', 27, '', 'pure'],
        ['ハコス', 'Baelz', 'n', 27, '', 'pure'],
        ['オーロ', 'Kronii', 'n', 27, '', 'pure'],
        ['九十九', 'Sana', 'n', 27, '', 'pure'],
        ['古石', 'Bijou', 'n', 27, '', 'pure'],
        ['ノヴェラ', 'Shiori', 'n', 27, '', 'pure'],
        ['レイヴンクロフト', 'Nerissa', 'n', 27, '', 'pure'],
        ['ムリン', 'Gigi', 'n', 27, '', 'pure'],
        ['ブラッドフレイム', 'Elizabeth', 'n', 27, '', 'pure'],
        ['イマーグリーン', 'Cecilia', 'n', 27, '', 'pure'],
        ['パンテーラ', 'Raora', 'n', 27, '', 'pure'],
        ['アビスガード', 'Fuwawa', 'n', 27, '', 'pure'],
        ['アビスガード', 'Mococo', 'n', 27, '', 'pure'],
    ],
}



def show_info():
    """
    Display info about what data will be requested from the user.

    Guidelines:
    0 - channel's handle
    1 - channel's ID (str of seemingly random characters)
    2 - first name last name (no space)
    3 - last name first name (no space)
    4 - first name last name (with space inbetween)
    5 - last name first name (with space inbetween)
    6 - first name
    7 - last name
    8 - middle name
    9 - nicknames popular
    10 - nicknames somewhat common
    11 - nicknames rare
    12 - channel handle without '@'
    13 - group name
    14 - branch name (holoen, hololiveEN, etc.)
    26 - first name in japanese
    27 - last name in japanese
    99 - video_id of a video made by a talent
    """

    print("keyword:                 keyword itself",
          "talent's name:           first name of the associated talent",
          "usage enabled:           y or n, default = y",
          "priority:                keyword category represented by a number"
          "                         (important, consult documentation) "
          "                         default = 9",
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
    WHERE keyword_word = %s and priority = %s;
    """
    cur = connection.cursor()
    cur.execute(check_keyword_unique_query, (values[0], values[3]))
    if cur.fetchone():
        print(f"The keyword_word - priority pair already exists in the db. "
              f"keyword: {values[0]}, pair: {values[3]}")
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
    WHERE keyword_word = %s AND priority = %s;
    """
    cur = connection.cursor()
    cur.execute(get_keyword_id_query, (values[0], values[3]))
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
    with psycopg2.connect(os.environ['DATABASE_URL']) as connection:
        if connection:
            choice = input("0 - add default keywords\n1 - add keywords manually\n: ")
            if choice == "0":
                # convert keywords data from the dictionary to a flat list
                default_keywords = [
                    keyword_info_list for list_of_lists in keywords.values() for keyword_info_list in list_of_lists
                ]
                # make all text lower case
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
        print('Connection closed')


main()

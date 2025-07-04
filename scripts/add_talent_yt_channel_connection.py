"""
A tool to link talents with their channels
"""

import os
import psycopg2
from psycopg2 import errors

CHANNEL_TALENT_PAIRS = [
    ['UCHsx4Hqa-1ORjQTh9TYDhww', 'Kiara'],
    ['UCL_qhgtOy0dy1Agp8vkySQg', 'Calliope'],
    ['UCyl1z3jo3XHR1riLFKG5UAg', 'Amelia'],
    ['UCMwGHR0BTZuLsmjY_NT5Pwg', "Ina'nis"],
    ['UCoSrY_IQQVpmIRZ9Xf-y93g', 'Gura'],
    ['UC8rcEBzJSleTkf_-agPM20g', 'IRyS'],
    ['UCO_aKKYxn4tvrqPjcTzZ6EQ', 'Fauna'],
    ['UC3n5uGu18FoCy23ggWWp8tA', 'Mumei'],
    ['UCgmPnx-EEeOrZSg5Tiw7ZRQ', 'Baelz'],
    ['UCmbs8T6MWqUHP1tIQvSgKrg', 'Kronii'],
    ['UCsUj0dszADCGbF3gNrQEuSQ', 'Sana'],
    ['UC9p_lqQ0FEDz327Vgf5JwqA', 'Bijou'],
    ['UCgnfPPb9JI3e9A4cXHnWbyg', 'Shiori'],
    ['UC_sFNM0z0MWm9A6WlKPuMMg', 'Nerissa'],
    ['UCDHABijvPBnJm7F-KlNME3w', 'Gigi'],
    ['UCW5uhrG1eCBYditmhL0Ykjw', 'Elizabeth'],
    ['UCvN5h1ShZtc7nly3pezRayg', 'Cecilia'],
    ['UCl69AEx4MdqMZH7Jtsm7Tig', 'Raora'],
    ['UCt9H_RpQzhxzlyBxFqrdHqA', 'Fuwawa'],
    ['UCt9H_RpQzhxzlyBxFqrdHqA', 'Mococo'],
    ['UCotXwY6s8pWmuWd_snKYjhg', 'HololiveEnglish'],
]


def write_to_talent_youtube_channel(conn, channel, talent):
    query = """
    INSERT INTO youtube_channel_talent (youtube_channel_id, talent_id)
    VALUES (
        %s, 
        (SELECT talent_id FROM talent WHERE first_name_eng = %s)
    );
    """
    with conn.cursor() as cur:
        try:
            cur.execute(query, (channel, talent))
        except errors.ForeignKeyViolation as e:
            print(f"FK violation for ({channel}, {talent}): {e}")
        except errors.UniqueViolation:
            print(f"Entry ({channel}, {talent}) already exists, skipping")
        else:
            print(f"Inserted ({channel}, {talent})")


def main():
    with psycopg2.connect(os.environ['DATABASE_URL']) as conn:
        for channel, talent in CHANNEL_TALENT_PAIRS:
            write_to_talent_youtube_channel(conn, channel, talent)
        conn.commit()


if __name__ == '__main__':
    main()

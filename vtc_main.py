from __future__ import annotations
import argparse
import datetime
import logging

from vtc import db_yt_interface, connect_to_db, vtc_logging


def search_yt_by_keyword(args: dict):
    connection = connect_to_db.connect_to_db()
    repetitions = args.pop('repetitions')
    do_subsearch = not args.pop('no_subsearch')
    search_instance = db_yt_interface.SearchYTByKeyword(connection, **args)
    while do_subsearch:
        if not search_instance.subsearch_next_and_save():
            break

    if repetitions == 0:
        while True:
            try:
                search_instance.search_next_and_save()
            # todo: add exception that occurs on no quota left or YT server connection error
            except Exception as err:
                print(f'Sequence of searches stopped because: \n {err}')
                break
    else:
        for _ in range(repetitions):
            search_instance.search_next_and_save()
    search_instance.session_stats()
    connect_to_db.connection_close(search_instance.connection)


def parse_arguments() -> dict:
    def validate_datetime(value: str) -> str:
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S%z')
            return value
        except ValueError as err:
            raise argparse.ArgumentTypeError(f'Wrong date, time, timezone format. '
                                             f'Should be: "YYYY-MM-DD HH:MM:SS+HH:SS" \n'
                                             f'Received: {value}. \n'
                                             f'Error: {err}')

    def parse_usage_enabled(value) -> bool:
        if value in ['FALSE', 'False', 'false', 'F', 'f', '0', 'N', 'n', 'NO', 'No', 'no']:
            return False
        else:
            return True

    global_parser = argparse.ArgumentParser()
    subparsers = global_parser.add_subparsers(title='Available Actions', dest='command')
    keyword_parser = subparsers.add_parser(
        'keyword',
        help='search youtube using a keyword and add the results to the DB'
    )
    keyword_parser.add_argument('-tn',
                                '--talents_names',
                                nargs='+',
                                default=argparse.SUPPRESS,
                                help='Searches will use only keywords related to talents with specified names.'
                                )
    keyword_parser.add_argument('-ssd',
                                '--start_search_datetime',
                                type=validate_datetime,
                                default=argparse.SUPPRESS,
                                help='Date and time. "YYYY-MM-DD HH:MM:SS+HH:SS"'
                                     'Searches will start no earlier than this point in time.'
                                )
    keyword_parser.add_argument('-esd',
                                '--end_search_datetime',
                                type=validate_datetime,
                                default=argparse.SUPPRESS,
                                help='Date and time. "YYYY-MM-DD HH:MM:SS+HH:SS"'
                                     'Searches will end no later than this point in time.'
                                )
    keyword_parser.add_argument('-pr',
                                '--priority',
                                nargs='+',
                                type=int,
                                default=argparse.SUPPRESS,
                                help='Only the keywords with those priority values will be searched.'
                                )
    keyword_parser.add_argument('-ue',
                                '--usage_enabled',
                                type=parse_usage_enabled,
                                default=argparse.SUPPRESS,
                                help='If set to FALSE, will ONLY use keywords that where not cleared for usage. '
                                     'Just avoid using this one.'
                                )
    keyword_parser.add_argument('-pu',
                                '--purity',
                                nargs='+',
                                default=argparse.SUPPRESS,
                                help='Only the keywords with those purity values will be searched.'
                                )
    keyword_parser.add_argument('-r',
                                '--repetitions',
                                type=int,
                                default=0,
                                help='Number of searches that will be conducted. (if 0, then as many as possible)'
                                )
    keyword_parser.add_argument('-sl',
                                '--search_layer',
                                type=int,
                                default=argparse.SUPPRESS,
                                help='Layer of the search. Allows searching over timeperiod that has already been '
                                     'searched in other layers, by having a separate search_map for each layer.'
                                     'default: current top layer'
                                )
    keyword_parser.add_argument('-ns',
                                '--no_subsearch',
                                action='store_true',
                                help='Disable sub-searches. Default: does sub-searches'
                                )

    args = vars(global_parser.parse_args())

    # Change data type, because future usage requires tuples instead of lists.
    for key, value in args.items():
        if isinstance(value, list):
            args[key] = tuple(value)

    return args


if __name__ == '__main__':
    vtc_logging.setup_logger()
    args = parse_arguments()
    print('Received arguments: ', args)
    command = args.pop('command')
    if command == 'keyword':
        search_yt_by_keyword(args)

import unittest
from unittest.mock import patch

import vtc_main
from vtc import db_yt_interface

class testParseArguments(unittest.TestCase):
    @patch('sys.argv', [
        'vtc_main.py',
        'keyword',
        '-tn',
        'name1',
        'name2',
        '-ssd',
        '2024-01-01 01:01:01+00:00',
        '-esd',
        '2024-02-01 01:01:01+00:00',
        '-pr',
        '0',
        '-ue',
        't',
        '-pu',
        'pure',
        'mixed',
        '-r',
        '0'
    ])
    def test_parse_arguments_single_dash(self):
        args = vtc_main.parse_arguments()
        self.assertEqual('keyword', args['command'])
        self.assertEqual(('name1', 'name2'), args['talents_names'])
        self.assertEqual('2024-01-01 01:01:01+00:00', args['start_search_date'])
        self.assertEqual('2024-02-01 01:01:01+00:00', args['end_search_date'])
        self.assertEqual((0,), args['priority'])
        self.assertEqual(True, args['usage_enabled'])
        self.assertEqual(('pure', 'mixed'), args['purity'])
        self.assertEqual(0, args['repetitions'])

    @patch('sys.argv', [
        'vtc_main.py',
        'keyword'
    ])
    def test_parse_arguments_no_arguments(self):
        args = vtc_main.parse_arguments()
        self.assertNotIn('talents_names', args)
        self.assertNotIn('start_search_date', args)
        self.assertNotIn('start_search_date', args)
        self.assertNotIn('priority', args)
        self.assertNotIn('usage_enabled', args)
        self.assertNotIn('purity', args)
        self.assertEqual(0, args['repetitions'])
#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from app.helpers.utils import *
from app import db, app
from app.models import Shaker
from datetime import datetime
from decimal import *

class TestUtils(BaseTestCase):

    def test_is_valid_email(self):
        actual = is_valid_email('cthanh@autonomous.nyc')
        result = True
        self.assertEqual(actual, result)

        actual = is_valid_email(' cthanh@autonomous.nyc')
        result = False
        self.assertEqual(actual, result)

        actual = is_valid_email('CTHANH@autonomous.nyc')
        result = False
        self.assertEqual(actual, result)

        actual = is_valid_email('phuong1@autonomous.nyc')
        result = True
        self.assertEqual(actual, result)

    def test_is_number(self):
        actual = isnumber(0)
        expected = True
        self.assertEqual(actual, expected)

        actual = isnumber(0.1)
        expected = True
        self.assertEqual(actual, expected)

        actual = isnumber(0.0000001)
        expected = True
        self.assertEqual(actual, expected)

        actual = isnumber(-1000)
        expected = True
        self.assertEqual(actual, expected)

        actual = isnumber(-0.1000)
        expected = True
        self.assertEqual(actual, expected)

        a = '-a.0'
        actual = isnumber(a)
        expected = False
        self.assertEqual(actual, expected)

    def test_formalize_desc(self):
        actual = formalize_description('123')
        expected = '123.'
        self.assertEqual(actual, expected)

        actual = formalize_description('')
        expected = ''
        self.assertEqual(actual, expected)

        actual = formalize_description('.')
        expected = '.'
        self.assertEqual(actual, expected)

        actual = formalize_description(None)
        expected = None
        self.assertEqual(actual, expected)

    def test_parse_str_to_array(self):
        actual = parse_str_to_array(None)
        expected = []
        self.assertEqual(actual, expected)

        actual = parse_str_to_array('')
        expected = []
        self.assertEqual(actual, expected)

        actual = parse_str_to_array([1,2])
        expected = []
        self.assertEqual(actual, expected)

        actual = parse_str_to_array("[1, 2]")
        expected = [1, 2]
        self.assertEqual(actual, expected)

        actual = parse_str_to_array("['1', '2']")
        expected = []
        self.assertEqual(actual, expected)

        actual = parse_str_to_array("[\"1\", \"2\"]")
        expected = ["1", "2"]
        self.assertEqual(actual, expected)

    def test_parse_date_string_to_timestamp(self):
        actual = parse_date_string_to_timestamp('2018-06-14T15:00:00Z')
        # UTC time
        expected = 1528963200 
        self.assertEqual(actual, expected)

    def test_local_to_utc(self):
        actual = local_to_utc(datetime.now().timetuple())
        local_time = (datetime.now()-datetime(1970,1,1)).total_seconds()
        self.assertGreater(local_time, actual + 6*60*60 )

    def test_utc_to_local(self):
        actual = utc_to_local(datetime.fromtimestamp(1528963200).timetuple())
        local_time = (datetime.now()-datetime(1970,1,1)).total_seconds()
        self.assertGreater(actual, local_time)

    def test_second_to_strftime(self):
        # Tue Jan 01 2019 23:59:59
        seconds = 1546361999
        str_time = second_to_strftime(seconds, '%Y-%m-%d %H:%M:%S')
        self.assertEqual(str_time, "2019-01-01 23:59:59")
        
        str_time = second_to_strftime(seconds, '%b %d %Y %I:%M:%S %p')
        self.assertEqual(str_time, "Jan 01 2019 11:59:59 PM")

        str_time = second_to_strftime(seconds)
        self.assertEqual(str_time, "Jan 01 2019 11:59:59 PM")

    def test_parse_shakers_array(self):
        shakers = []
        
        expected = []
        actual = parse_shakers_array(shakers)
        self.assertEqual(expected, actual)

        expected = []
        actual = parse_shakers_array(None)
        self.assertEqual(expected, actual)


        shaker = Shaker(
            shaker_id=1
        )
        shakers.append(shaker)
        shaker = Shaker(
            shaker_id=2
        )
        shakers.append(shaker)

        expected = [1, 2]
        actual = parse_shakers_array(shakers)
        self.assertEqual(expected, actual)

    def test_is_equal(self):
        a = Decimal('2.40') * Decimal('0.000003')
        b = Decimal('1.71') * Decimal('0.0000042')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)

        a = Decimal('2.40') * Decimal('0.000003')
        b = Decimal('1.70') * Decimal('0.0000042')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)

        a = Decimal('3') * Decimal('1')
        b = Decimal('2') * Decimal('1.5')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)

        a = Decimal('3') * Decimal('1')
        b = Decimal('1.99') * Decimal('1.5')
        actual = is_equal(a, b)
        expected = False
        self.assertEqual(actual, expected)

        a = Decimal('2.5') * Decimal('0.001')
        b = Decimal('1.67') * Decimal('0.0015')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)

        a = Decimal('2.5') * Decimal('0.001')
        b = Decimal('1.66') * Decimal('0.0015')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)

        a = Decimal('4') * Decimal('0.001')
        b = Decimal('1.33') * Decimal('0.003')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)

        a = Decimal('4') * Decimal('0.001')
        b = Decimal('1.34') * Decimal('0.003')
        actual = is_equal(a, b)
        expected = True
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from app.helpers.utils import is_valid_email, isnumber, formalize_description, parse_str_to_array
from app import db, app


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


if __name__ == '__main__':
    unittest.main()
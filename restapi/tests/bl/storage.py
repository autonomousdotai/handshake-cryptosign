#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from mock import patch
from datetime import datetime
from tests.routes.base import BaseTestCase
from app import db, app
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.storage as storage_bl

class TestTask(BaseTestCase):

    def setUp(self):
        pass

    def clear_data_before_test(self):
        pass
        

    def test_validate_extension(self):
        self.clear_data_before_test()
        filename = '2018-09-02 10.12.10.jpg'

        actual = storage_bl.validate_extension(filename)
        expected = True
        self.assertEqual(actual, expected) 

        filename = '2018-09-02 10.12.10'
        actual = storage_bl.validate_extension(filename)
        expected = False
        self.assertEqual(actual, expected) 

        filename = ''
        actual = storage_bl.validate_extension(filename)
        expected = False
        self.assertEqual(actual, expected)

        filename = None
        actual = storage_bl.validate_extension(filename)
        expected = False
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
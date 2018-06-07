#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome

import app.bl.match as match_bl
import app.constants as CONST
import mock
import json


class TestMatchBl(BaseTestCase):

    def setUp(self):
        pass


    def test_all_matches(self):
        matches = match_bl.find_all_markets()        
        print matches
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
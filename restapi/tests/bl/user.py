#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from mock import patch
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import User, Handshake
from app.helpers.message import MESSAGE

import mock
import json
import time

class TestUser(BaseTestCase):

    def setUp(self):
        pass

    def test_insert_user(self):
        pass


if __name__ == '__main__':
    unittest.main()
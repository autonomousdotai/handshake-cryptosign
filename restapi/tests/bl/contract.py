#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome, Match, Contract
from app.helpers.utils import local_to_utc

import app.bl.contract as contract_bl
import app.constants as CONST
import mock
import json


class TestContractBl(BaseTestCase):

    def setUp(self):
        pass

    def clear_data_before_test(self):
        pass

    def test_filter_contract_id_in_contracts(self):
        self.clear_data_before_test()

        contracts = [
                        {
                            '': ''
                        }
                    ]


if __name__ == '__main__':
    unittest.main()
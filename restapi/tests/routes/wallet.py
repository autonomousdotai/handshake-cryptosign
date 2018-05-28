# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models.user import User, Handshake
from app import db, app
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestWallletBluePrint(BaseTestCase):

    def test_get_list_wallet_based_on_chain_id(self):
        with self.client:
           pass

if __name__ == '__main__':
    unittest.main()
# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models.user import User, Handshake
import app.bl.user as user_bl
from app import db, app
from app.helpers.message import MESSAGE

import mock
import json
import time

class TestUserBluePrint(BaseTestCase):
            
    def setUp(self):
        pass
    
if __name__ == '__main__':
    unittest.main()
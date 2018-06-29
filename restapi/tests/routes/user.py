# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import User, Handshake
from app import db, app
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestUserBluePrint(BaseTestCase):
            
    def setUp(self):
        pass
    
if __name__ == '__main__':
    unittest.main()
from app import app, db
from flask_testing import TestCase
import json


class BaseTestCase(TestCase):
    def create_app(self):
        """
        Create an instance of the app with the testing configuration
        :return:
        """
        app.config.from_object('app.settings.TestingConfig') # object-based default configuration
        app.config.from_pyfile('settings.cfg', silent=True) # instance-folders configuration
        return app

    def setUp(self):
        """
        Create the database
        :return:
        """
        db.create_all()
        db.session.commit()

    def tearDown(self):
        """
        Drop the database tables and also remove the session
        :return:
        """
        db.session.remove()
        # db.drop_all()

    def register_user(self, email, password, name=''):
        """
        Helper method for registering a user with dummy data. This method is used for mobile
        :return:
        """
        return self.client.post(
            'sign-in',
            data={"email": email, "password": password, "name": name})

    def auth_user(self, email, _id, name):
        """
        Helper method for auth a user with dummy data. This method is used for web
        :return:
        """
        return self.client.post(
            'auth',
            data={"email": email, "name": name, "id": _id})

    def get_user_token(self):
        """
        Get a user token
        :return:
        """
        auth_res = self.register_user('trong1@autonomous.nyc', '1')
        return json.loads(auth_res.data.decode())['data']['access_token']
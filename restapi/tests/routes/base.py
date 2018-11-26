from app import app, db
from app.models import Handshake, User, Outcome, Match, Contract, Token, Redeem
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

        # init data first
        self.init_data_before_test()


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


    def init_data_before_test(self):
        # create token
        token = Token.find_token_by_id(1)
        if token is None:
            token = Token(
                id=1,
                name="SHURIKEN",
                symbol="SHURI",
                decimal=18
            )
            db.session.add(token)
            db.session.commit()

        # create contract
        contract = Contract.find_contract_by_id(1)
        if contract is None:
            contract = Contract(
                id=1,
                contract_name="contract1",
                contract_address="0x123",
                json_name="name1"
            )
            db.session.add(contract)
            db.session.commit()

        # create match
        match = Match.find_match_by_id(1)
        if match is None:
            match = Match(
                id=1
            )
            db.session.add(match)
            db.session.commit()

        # create user
        user = User.find_user_with_id(88)
        if user is None:
            user = User(
                id=88
            )
            db.session.add(user)
            db.session.commit()

        user = User.find_user_with_id(99)
        if user is None:
            user = User(
                id=99
            )
            db.session.add(user)
            db.session.commit()

        user = User.find_user_with_id(100)
        if user is None:
            user = User(
                id=100
            )
            db.session.add(user)
            db.session.commit() 
        
        user = User.find_user_with_id(109)
        if user is None:
            user = User(
                id=109
            )
            db.session.add(user)
            db.session.commit()


        user = User.find_user_with_id(66)
        if user is None:
            user = User(
                id=66
            )
            db.session.add(user)
            db.session.commit()

        # create outcome
        outcome = Outcome.find_outcome_by_id(88)
        if outcome is None:
            outcome = Outcome(
                id=88,
                match_id=1,
                hid=88,
                contract_id=contract.id
            )
            db.session.add(outcome)
            db.session.commit()
        else:
            outcome.result = -1
            outcome.contract_id=contract.id
            db.session.commit()

        # add redeem
        try:
			for i in range(1, 3):
				chars = string.ascii_uppercase + string.ascii_lowercase
				code = ''.join(random.choice(chars) for _ in range(i))
				if Redeem.find_redeem_by_code(code) is None:
					r = Redeem(
						code=code
					)
					db.session.add(r)
					db.session.commit()
        except Exception as ex:
            db.session.rollback()
        
# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import User, Handshake, Shaker, Outcome, Token
from app import db, app
from sqlalchemy import bindparam, literal_column, func
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl

class TestUserBluePrint(BaseTestCase):
            
    def setUp(self):
        # create token
        token = Token.find_token_by_id(1)
        if token is None:
            token = Token(
                id=1,
                name="SHURIKEN",
                symbol="SHURI",
                decimal=18,
                contract_address='0x123'
            )
            db.session.add(token)
            db.session.commit()
        
        else:
            token.tid = None
            token.status = -1
            db.session.flush()
            db.session.commit()

        token = Token.find_token_by_id(2)
        if token is None:
            token = Token(
                id=2,
                name="SHURIKEN",
                symbol="SHURI",
                decimal=18,
                contract_address='0x1234'
            )
            db.session.add(token)
            db.session.commit()
        
        else:
            token.tid = None
            token.status = -1
            db.session.flush()
            db.session.commit()


    def tearDown(self):
        pass


    def clear_data_before_test(self):
        token1 = Token.find_token_by_id(1)
        token1.tid = None
        token1.status = -1

        token2 = Token.find_token_by_id(2)
        token2.tid = None
        token2.status = -1

        user = User.find_user_with_id(66)
        user.tokens = []

        db.session.flush()
        db.session.commit()
        

    def test_user_approve_token(self):
        self.clear_data_before_test()

        with self.client:
            Uid = 66
            params = {
                "token_id": 1
            }
            response = self.client.post(
                                    '/approve_token',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # approve token first
            token = Token.find_token_by_id(1)
            token.tid = 0
            token.status = 1

            # call appprove token again
            response = self.client.post(
                                    '/approve_token',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

    def test_user_reputation(self):

        all_hs = db.session.query(Handshake).filter(Handshake.outcome_id.in_([1000, 1001, 1002])).all()
        for item in all_hs:
            db.session.delete(item)

        all_s = db.session.query(Shaker).filter(Shaker.handshake_id.in_(\
            db.session.query(Handshake.id).filter(Handshake.outcome_id.in_([1000, 1001, 1002]))\
        )).all()

        for item in all_s:
            db.session.delete(item)

        arr_hs = []
        outcome1 = Outcome.find_outcome_by_id(1000)
        db.session.delete(outcome1)
        outcome1 = Outcome(
            id=1000,
            match_id=1,
            result=1,
            name="1"
        )
        db.session.add(outcome1)
        db.session.commit()

        outcome2 = Outcome.find_outcome_by_id(1001)
        db.session.delete(outcome2)
        outcome2 = Outcome(
            id=1001,
            match_id=1,
            result=1,
            name="1"
        )
        db.session.add(outcome2)
        db.session.commit()

        outcome3 = Outcome.find_outcome_by_id(1002)
        db.session.delete(outcome3)
        outcome3 = Outcome(
            id=1002,
            match_id=2657,
            result=1,
            name="1"
        )
        db.session.add(outcome3)
        db.session.commit()

        user1 = User.find_user_with_id(88)
        if user1 is None:
            user1 = User(
                id=88
            )
            db.session.add(user1)
            db.session.commit()

        user2 = User.find_user_with_id(89)
        if user2 is None:
            user2 = User(
                id=89
            )
            db.session.add(user2)
            db.session.commit()

        user3 = User.find_user_with_id(100)
        if user3 is None:
            user3 = User(
                id=100
            )
            db.session.add(user3)
        db.session.commit()

        handshake1 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user1.id,
                outcome_id=outcome1.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                side=outcome1.result,
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE']
            )
        db.session.add(handshake1)
        arr_hs.append(handshake1)

        handshake2 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user1.id,
                outcome_id=outcome2.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE'],
                side=outcome2.result
            )
        db.session.add(handshake2)
        arr_hs.append(handshake2)

        handshake3 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user1.id,
                outcome_id=outcome2.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE'],
                side=outcome2.result
            )
        db.session.add(handshake3)
        arr_hs.append(handshake3)

        handshake4 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user2.id,
                outcome_id=outcome1.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE'],
                side=outcome1.result
            )
        db.session.add(handshake4)
        arr_hs.append(handshake4)

        handshake5 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user2.id,
                outcome_id=outcome1.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE'],
                side=outcome1.result
            )
        db.session.add(handshake5)
        arr_hs.append(handshake5)

        handshake6 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user3.id,
                outcome_id=outcome3.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE'],
                side=outcome3.result + 1
            )
        db.session.add(handshake6)
        arr_hs.append(handshake6)

        handshake7 = Handshake(
                hs_type=3,
                chain_id=4,
                user_id=user3.id,
                outcome_id=outcome3.id,
                odds=1.5,
                amount=1,
                currency='ETH',
                remaining_amount=0,
                from_address='0x123',
                status=HandshakeStatus['STATUS_DONE'],
                side=outcome3.result + 1
            )
        db.session.add(handshake7)
        arr_hs.append(handshake7)

        shaker1 = Shaker(
			shaker_id=user2.id,
			amount=0.2,
			currency='ETH',
			odds=6,
			side=outcome1.result,
			handshake_id=handshake1.id,
			from_address='0x123',
			chain_id=4,
			status=HandshakeStatus['STATUS_DONE']
		)
        db.session.add(shaker1)
        arr_hs.append(shaker1)
        db.session.commit()

        shaker2 = Shaker(
			shaker_id=user3.id,
			amount=0.2,
			currency='ETH',
			odds=6,
			side=outcome1.result,
			handshake_id=handshake1.id,
			from_address='0x123',
			chain_id=4,
			status=HandshakeStatus['STATUS_DONE']
		)
        db.session.add(shaker2)
        arr_hs.append(shaker2)

        db.session.commit()

        # hs_bets = db.session.query(Handshake.user_id.label("user_id"), bindparam("is_hs", 1), Handshake.free_bet, Handshake.status, Handshake.side, Handshake.from_address, Outcome.id, Outcome.name)\
        #     .filter(Handshake.outcome_id == Outcome.id)\
        #     .filter(Outcome.match_id == 1)\
        #     .filter(Handshake.user_id == user1.id)

        # s_bets = db.session.query(Shaker.shaker_id.label("user_id"), bindparam("is_hs", 0), Shaker.free_bet, Handshake.status, Shaker.side, Shaker.from_address, Outcome.id, Outcome.name)\
        #     .filter(Shaker.handshake_id == Handshake.id)\
        #     .filter(Handshake.outcome_id == Outcome.id)\
        #     .filter(Outcome.match_id == 1)\
        #     .filter(Shaker.shaker_id == user1.id)

        # bets = hs_bets.union_all(s_bets).order_by(Outcome.id.desc()).all()
        # print bets


        # Get all user betted this outcome
        hs_user = db.session.query(Handshake.user_id.label("user_id"))\
            .filter(Handshake.outcome_id == outcome1.id)

        s_user = db.session.query(Shaker.shaker_id.label("user_id"))\
            .filter(Shaker.handshake_id == Handshake.id)\
            .filter(Handshake.outcome_id == outcome1.id)

        total_users = hs_user.union_all(s_user).group_by('user_id')

        # users = db.session.query(User).filter(User.id.in_(hs_user.union_all(s_user).group_by('user_id'))).all()

        hs_all_bets = db.session.query(Handshake.user_id.label("user_id"), bindparam("is_hs", 1), Handshake.free_bet, Handshake.status.label("status"), Handshake.side.label('side'), Handshake.from_address, Outcome.result.label('outcome_result'))\
            .filter(Outcome.id == Handshake.outcome_id)

        s_all_bets = db.session.query(Shaker.shaker_id.label("user_id"), bindparam("is_hs", 0), Shaker.free_bet, Shaker.status.label("status"), Shaker.side.label('side'), Shaker.from_address, Outcome.result.label('outcome_result'))\
            .filter(Shaker.handshake_id == Handshake.id)\
            .filter(Outcome.id == Handshake.outcome_id)

        bets_query = hs_all_bets.union_all(s_all_bets).subquery()

        bets = db.session.query(
            bets_query.c.user_id.label('user_id'),
            func.count(bets_query.c.user_id).label('total_bets'),
            bindparam("total_bets_win", 0)
        )\
        .filter(bets_query.c.user_id.in_(total_users))\
        .filter(bets_query.c.status.in_([HandshakeStatus['STATUS_DONE'], HandshakeStatus['INDUSTRIES_NONE']]))\
        .group_by(bets_query.c.user_id)

        bets_win = db.session.query(
            bets_query.c.user_id.label('user_id'),
            bindparam("total_bets", 0),
            func.count(bets_query.c.user_id).label('total_bets_win'),
        )\
        .filter(bets_query.c.user_id.in_(total_users))\
        .filter(bets_query.c.status.in_([HandshakeStatus['STATUS_DONE'], HandshakeStatus['INDUSTRIES_NONE']]))\
        .filter(bets_query.c.side == bets_query.c.outcome_result)\
        .group_by(bets_query.c.user_id)

        result_query = bets.union_all(bets_win).subquery()
        adset_list = db.session.query(
            result_query.c.user_id,
            func.sum(result_query.c.total_bets_win).label('total_bets_win'),
            func.sum(result_query.c.total_bets).label('total_bets')
        ).group_by(result_query.c.user_id)

        results = adset_list.all()

        for item in results:
            if item.user_id ==  user1.id:
                self.assertTrue(item.total_bets_win == 3)

        for item in arr_hs:
            db.session.delete(item)
        db.session.commit()


if __name__ == '__main__':
    unittest.main()
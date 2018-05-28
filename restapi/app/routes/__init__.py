import requests
import json
import base64

from flask import request, g
from werkzeug.security import generate_password_hash
from app import db
from app.helpers.response import response_ok, response_error
from app.routes.handshake import handshake_routes
from app.routes.contact import contact_routes
from app.routes.wallet import wallet_routes
from app.routes.device import device_routes
from app.routes.event import event_routes
from app.routes.user import user_routes
from app.routes.tx import tx_routes
from flask_jwt_extended import (jwt_required, create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_refresh_token_required)


def init_routes(app):
    @app.route('/')
    def hello():
        return 'Cryptosign API'

    @app.route('/test-pdf/<handshake_id>')
    def test_pdf(handshake_id):
        import os
        from app import wm
        from app.models import Handshake
        from app.models import Tx
        import time
        import hashlib
        from flask import send_file
        handshake = Handshake.query.get(handshake_id)
        millis = int(round(time.time()))
        filename = '{}_{}.pdf'.format(millis, hashlib.md5(os.urandom(32)).hexdigest())
        file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
        # file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/1525938546_QmVTmeuxj75URdjSFaLT1gFYx58C4nLBZBXkciMfhLMkK2_decrypt.pdf'
        f = open(file_path, "w+")
        f.close()
        txs = Tx.find_tx_with_hand_shake_id(handshake.id)
        not_signed_file = os.path.abspath(
            wm.add_description("Lorem Ipsum is simply dummy text of the printing and typesetting",
                               handshake.industries_type, file_path))
        # not_signed_file = os.path.abspath(wm.add_payee_signature(file_path, handshake.industries_type, txs[0]))
        # not_signed_file = os.path.abspath(wm.add_payer_signature(file_path, handshake.industries_type, txs[0]))
        return send_file(not_signed_file, mimetype='application/pdf')

    @app.route('/refresh-token', methods=['GET'])
    @jwt_refresh_token_required
    def refresh():
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        ret = {'access_token': new_token}
        return response_ok(ret)

    @app.route('/private')
    @jwt_required
    def private():
        try:
            current_user = get_jwt_identity()
            return response_ok(current_user)
        except Exception, ex:
            return response_error(ex.message)

    app.register_blueprint(contact_routes, url_prefix='/contact')
    app.register_blueprint(handshake_routes, url_prefix='/handshake')
    app.register_blueprint(wallet_routes, url_prefix='/wallet')
    app.register_blueprint(device_routes, url_prefix='/device')
    app.register_blueprint(event_routes, url_prefix='/event')
    app.register_blueprint(tx_routes, url_prefix='/tx')
    app.register_blueprint(user_routes)

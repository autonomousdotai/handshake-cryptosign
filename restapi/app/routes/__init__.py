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

    app.register_blueprint(contact_routes, url_prefix='/contact')
    app.register_blueprint(handshake_routes, url_prefix='/handshake')
    app.register_blueprint(wallet_routes, url_prefix='/wallet')
    app.register_blueprint(device_routes, url_prefix='/device')
    app.register_blueprint(event_routes, url_prefix='/event')
    app.register_blueprint(tx_routes, url_prefix='/tx')
    app.register_blueprint(user_routes)

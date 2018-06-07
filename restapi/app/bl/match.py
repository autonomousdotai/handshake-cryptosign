from flask import g
from sqlalchemy import and_, func
from datetime import datetime

from app import db
from app.models import User, Handshake, Match
from app.helpers.message import MESSAGE

import app.constants as CONST
import requests
import json
import base64
import hashlib
import urllib


def find_all_markets():
	return db.session.query(Match).order_by(Match.date.asc()).all()
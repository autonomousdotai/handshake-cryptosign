from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User

contact_routes = Blueprint('contact', __name__)


@contact_routes.route('/', methods=['GET'])
@jwt_required
def contact():
	try:
		user_id = get_jwt_identity()

		user = User.query.get(user_id)
		contacts = user.contacts.all()
		data = []
		for contact in contacts:
			data.append(contact.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@contact_routes.route('/add', methods=['POST'])
@jwt_required
def add_contact():
	try:
		user_id = get_jwt_identity()
		address = request.form.get('address')

		user = User.query.get(user_id)
		wallet = Wallet.query.filter(Wallet.address == address).first()
		contact = wallet.user

		user.contacts.append(contact)

		db.session.commit()

		return response_ok(contact.to_json())
	except Exception, ex:
		return response_error(ex.message)


@contact_routes.route('/remove', methods=['POST'])
@jwt_required
def remove_contact():
	try:
		user_id = get_jwt_identity()
		contact_id = request.form.get('contact_id')

		user = User.query.get(user_id)
		contact = User.query.get(contact_id)

		user.contacts.remove(contact)

		db.session.commit()

		return response_ok()
	except Exception, ex:
		return response_error(ex.message)

#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import jsonify


def response_ok(value=None, message=''):
	result = {
		'status': 1,
		'message': message
	}

	if len(message) > 0:
		result['message'] = message

	if value is not None:
		result.update({'data': value})

	return jsonify(result)


def response_error(message='', status=0):
	result = {
		'status': status,
	}
	if message:
		result.update({'message': message})

	return jsonify(result)

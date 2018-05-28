#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import jsonify


def response_ok(value=None):
	result = {
		'status': 1
	}
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

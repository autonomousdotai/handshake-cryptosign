import os
from datetime import timedelta


class BaseConfig(object):
	ENV = 'DEV'
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	UPLOAD_DIR = os.path.join(BASE_DIR, 'files', 'temp')
	# Mobile
	MOBILE_CURRENT_VERSION = '2.0.1'
	MOBILE_MIN_VERSION = '2.0.1'
	# SQLALCHEMY
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	DATABASE_CONNECT_OPTIONS = {'charset': 'utf8'}
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	# JWT
	JWT_AUTH_USERNAME_KEY = 'email'
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=60)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=120)
	#
	SECRET_KEY = ''
	# SendGrid
	SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
	# AWS
	AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
	AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
	AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', '')

	# Autonomous server: user sso
	DISPATCHER_SERVICE_ENDPOINT = os.getenv('DISPATCHER_SERVICE_ENDPOINT', '')
	# Blockchain server: community blockchain eth
	BLOCKCHAIN_SERVER_ENDPOINT = os.getenv('BLOCKCHAIN_SERVER_ENDPOINT', 'http://localhost:3000')
	# IPFS
	IPFS_REST_HOST = os.environ.get('IPFS_REST_HOST', 'localhost')
	IPFS_REST_PORT = os.environ.get('IPFS_REST_PORT', '5001')

	PASSPHASE = ''
	EMAIL = ''
	AUTONOMOUS_WEB_PASSPHASE = ''

	FILE_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/files'
	REDIS_HOST = 'localhost'
	REDIS_PORT = 6379
	CELERY_BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	FCM_SERVER_KEY = os.getenv('FCM_SERVER_KEY', '')
	SOLR_SERVICE = os.getenv('SOLR_SERVICE', '')
	FCM_SERVICE = os.getenv('FCM_SERVICE', 'http://localhost:8082')
	FIREBASE_DATABASE_URL = ''
	FIREBASE_PROJECT_NAME = ''


class DevelopmentConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'


class TestingConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'


class StagingConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	REDIS_HOST = ''
	REDIS_PORT = 6379
	REDIS_PASSWORD = ''
	CELERY_BROKER_URL = 'redis://:%s@%s:%s/0' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
	CELERY_RESULT_BACKEND = 'redis://:%s@%s:%s/0' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
	SOLR_SERVICE = os.getenv('SOLR_SERVICE', '')
	FIREBASE_DATABASE_URL = ''
	FIREBASE_PROJECT_NAME = ''

class ProductionConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	REDIS_HOST = ''
	REDIS_PORT = 6379
	CELERY_BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	SOLR_SERVICE = os.getenv('SOLR_SERVICE', '')
	FIREBASE_DATABASE_URL = ''
	FIREBASE_PROJECT_NAME = ''
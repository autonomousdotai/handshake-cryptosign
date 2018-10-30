import os 
import google.auth

from google.cloud import storage
from google.oauth2 import service_account

dir_path = os.path.dirname(os.path.realpath(__file__))


class GoogleCloudStorage(object):
	def __init__(self, app=None):
		super(GoogleCloudStorage, self).__init__()
		if app:
			self.app = app
			self.init_gc_storage_client(app)


	def init_app(self, app):
		self.app = app
		self.init_gc_storage_client(app)


	def init_gc_storage_client(self, app):
		credentials = service_account.Credentials.from_service_account_file(dir_path + "/{}.json".format(app.config['GC_STORAGE_PROJECT_NAME']))
		credentials = credentials.with_scopes(['https://www.googleapis.com/auth/devstorage.full_control', 'https://www.googleapis.com/auth/devstorage.read_write'])
		self.gc_storage_client = storage.Client(project= app.config['GC_STORAGE_PROJECT_NAME'], credentials=credentials)


	def get_buckets(self):
		return client.list_buckets()
	

	def get_bucket_by_name(self, app, bucket_name):
		# return self.gc_storage_client.get_bucket(app.config['GC_STORAGE_BUCKET'])
		return self.gc_storage_client.get_bucket(bucket_name)

<<<<<<< Updated upstream

	def upload_blob(self, bucket_name, source_file_name, blob_name, image_name):
=======
	def upload_blob(self, bucket_name, path_to_file_upload, blob_name, image_name):
>>>>>>> Stashed changes
		try:
			storage_client = self.gc_storage_client
			bucket = storage_client.get_bucket(bucket_name)
			if bucket.exists() is False:
				print "Bucket is not exist"
				return False
			# print [b.name for b in bucket.list_blobs()]
			blob = bucket.blob(blob_name + '/' + image_name)
			if blob.exists() is True:
				print "Blod is not exist: {}".format(blob_name)
				return False

			blob.upload_from_filename(path_to_file_upload, content_type='image/jpeg')
			# blob.make_public()
			uri = "gs://%s/%s/%s" % (bucket_name, blob_name, image_name)
			print "Upload load to Google Storage success: {}".format(uri)
			return True

		except Exception as err:
			print err
			print err.message
			print err.args
			print("upload_data to Google Storage error: %s" % (err))
<<<<<<< Updated upstream


	'''KMS Key'''
	def upload_blob_with_kms(self, bucket_name, source_file_name, destination_blob_name, kms_key_name):
		# Uploads a file to the bucket, encrypting it with the given KMS key.
		storage_client = self.gc_storage_client
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(destination_blob_name, kms_key_name=kms_key_name)
		blob.upload_from_filename(source_file_name)

		print('File {} uploaded to {} with encryption key {}.'.format(
			source_file_name,
			destination_blob_name,
			kms_key_name))


	def enable_default_kms_key(self, bucket_name, kms_key_name):
		# Sets a bucket's default KMS key.
		storage_client = self.gc_storage_client
		bucket = storage_client.get_bucket(bucket_name)
		bucket.default_kms_key_name = kms_key_name
		bucket.patch()

		print('Set default KMS key for bucket {} to {}.'.format(
			bucket.name,
			bucket.default_kms_key_name))
		# [END storage_set_bucket_default_kms_key]

=======
>>>>>>> Stashed changes

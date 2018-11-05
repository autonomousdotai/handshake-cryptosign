from recombee_api_client.api_client import RecombeeClient
from recombee_api_client.api_requests import AddItemProperty, SetItemValues, AddPurchase, RecommendItemsToItem, Batch, ResetDatabase
import json

class Recombee(object):
	def __init__(self, app=None):
		super(Recombee, self).__init__()
		if app:
			self.app = app
			self.load_recombee()


	def init_app(self, app):
		self.app = app
		self.load_recombee()


	def load_recombee(self):
		self.recombee_client = RecombeeClient(self.app.config['RECOMBEE_DB'], self.app.config['RECOMBEE_KEY'])


	def init_match_database(self):
		self.recombee_client.send(ResetDatabase())

		# Add properties of matches
		self.recombee_client.send(AddItemProperty('matchID', 'int'))
		self.recombee_client.send(AddItemProperty('name', 'string'))
		"""
			Example: "Will BTC exceed $6,600 USD by Nov 6th? [Guess before Nov 4rd]"
			-> "tags" is ["BTC", "USD", "Nov 6th"]
		"""
		self.recombee_client.send(AddItemProperty('tags', 'set'))
		self.recombee_client.send(AddItemProperty('sourceID', 'int'))
		self.recombee_client.send(AddItemProperty('categoryID', 'int'))


	def sync_user_data(self, user_id, matches=[]):
		requests = []
		for match in matches:
			r = AddPurchase(match.id,
							user_id,
							match.name,
							[],
							match.source_id,
							match.category_id)
			requests.append(r)
		br = Batch(requests)
		result = self.recombee_client.send(br)
		print "========"
		print result

from recombee_api_client.api_client import RecombeeClient
from recombee_api_client.api_requests import AddItemProperty, SetItemValues, AddPurchase, RecommendItemsToUser, Batch, ResetDatabase
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
		self.recombee_client.send(AddItemProperty('name', 'string'))
		"""
			Example: "Will BTC exceed $6,600 USD by Nov 6th? [Guess before Nov 4rd]"
			-> "tags" is ["BTC", "USD", "Nov 6th"]
		"""
		self.recombee_client.send(AddItemProperty('tags', 'set'))
		self.recombee_client.send(AddItemProperty('sourceID', 'int'))
		self.recombee_client.send(AddItemProperty('categoryID', 'int'))
		self.recombee_client.send(AddItemProperty('closeTime', 'timestamp'))

	def sync_user_data(self, user_id, match_ids=[], timestamp=""):
		requests = []
		for match_id in match_ids:
			r = AddPurchase(user_id,
							match_id,
							timestamp=timestamp,
							cascade_create=True)
			requests.append(r)
		br = Batch(requests)
		result = self.recombee_client.send(br)
		print result

	def sync_item_data(self, matches=[]):
		requests = []
		for match in matches:
			r = SetItemValues(match["id"],
				{
					"name": match["name"],
					"tags": [],
					"sourceID": match["source_id"],
					"categoryID": match["category_id"],
					"closeTime": match["date"]
				},
				cascade_create=True
			)
			requests.append(r)

		br = Batch(requests)
		self.recombee_client.send(br)

	def user_recommended_data(self, user_id, count=5, optional=None):
		return self.recombee_client.send(RecommendItemsToUser(user_id, count,
			filter=optional["filter"] if optional is not None else None,
			# booster=None,
			# cascade_create=None,
			# scenario=None,
			# return_properties=None,
			# included_properties=None,
			# diversity=None,
			# min_relevance=None,
			# rotation_rate=None,
			# rotation_time=None
			)
		)

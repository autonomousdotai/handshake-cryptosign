from recombee_api_client.api_client import RecombeeClient
from recombee_api_client.api_requests import AddItemProperty, AddDetailView, SetViewPortion, SetItemValues, AddPurchase, RecommendItemsToUser, Batch, ResetDatabase
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

	def sync_user_data(self, user_id, data=[], timestamp=""):
		requests = []

		for item in data:
			if item["ids"] is not None and len(item["ids"]) > 0:
				if item["view_type"] == "bet":
					for match_id in item["ids"]:
						r = AddPurchase(
							user_id, 
							match_id, 
							timestamp=timestamp, 
							cascade_create=True
						)
						requests.append(r)
				elif item["view_type"] == "scroll":
					for match_id in item["ids"]:
						r = SetViewPortion(
							user_id, 
							match_id, 
							portion=item["options"]["portion"] if item["options"]is not None else None,
							timestamp=timestamp, 
							cascade_create=True
						)
						requests.append(r)
				else:
					for match_id in item["ids"]:
						r = AddDetailView(
							user_id, 
							match_id, 
							timestamp=timestamp, 
							cascade_create=True,
							duration=item["options"]["duration"] if item["options"] is not None else None
						)
						requests.append(r)

		br = Batch(requests)
		result = self.recombee_client.send(br)
		print result

	def sync_item_data(self, matches=[]):
		requests = []
		for match in matches:
			r = SetItemValues(
				match["id"],
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

	def user_recommended_data(self, user_id, count=5, options=None):
		return self.recombee_client.send(
			RecommendItemsToUser(
				user_id,
				count,
				filter=options["filter"] if options is not None else None
			)
		)

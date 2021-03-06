import os
from slackclient import SlackClient

class SlackService(object):
	def __init__(self, app=None):
		super(SlackService, self).__init__()
		if app:
			self.app = app
			self.sc = SlackClient(self.app.config['SLACK_API_TOKEN'])

	def init_app(self, app):
		self.app = app
		self.sc = SlackClient(self.app.config['SLACK_API_TOKEN'])
		

	def send_message(self, message, title='*Please review:*'):
		try:
			self.sc.api_call(
						"chat.postMessage",
						channel=self.app.config['SLACK_CHANNEL'],
						text='{} [{}] \n {}'.format(title, self.app.config['ENV'], message),
						mrkdwn=True
						)
		except Exception as ex:
			print str(ex)

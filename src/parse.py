class API(object):
	BASE_URL = 'https://dev-100-api.huntflow.ru/'


	def __init__(self, token=None):
		self.token = token
		self.headers = {
			"Authorization": f"Bearer {token}",
			'User-Agent': 'resume_grabber/1.0 (test@huntflow.ru)'
		}

	def me(self):
		"""info about current authorized user

		request /me

		response {
			"id": 3123123,
			"name": "Иванов Иван",
			"position": "HRD",
			"email": "hello@huntflow.ru",
			"phone": "84956478221",
			"locale": "ru_RU"
		}"""
		try:


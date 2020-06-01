import json
import logging
import time
from os import path
from mimetypes import MimeTypes

from settings import BASE_URL

import requests

TOO_MANY_REQUESTS_STATUS = 429


class Api:
	def me(self, *args, **kwargs):
		"""info about current authorized user"""
		return requests.get(BASE_URL + 'me', **kwargs)

	def accounts(self, *args, **kwargs):
		"""info about available organisations for user"""
		return requests.get(BASE_URL + 'accounts', **kwargs)

	def vacancies(self, *args, **kwargs):
		"""info about statuses"""
		return requests.get(BASE_URL + f'account/{args[0]}/vacancies',
							**kwargs)

	def statuses(self, *args, **kwargs):
		"""info about statuses"""
		return requests.get(BASE_URL + f'account/{args[0]}/vacancy/statuses',
							**kwargs)

	def upload_file(self, *args, **kwargs):
		"""info about statuses"""
		return requests.post(BASE_URL + f'account/{args[0]}/upload',
							**kwargs)

	def upload_applicant(self, *args, **kwargs):
		return requests.post(BASE_URL + f'account/{args[0]}/applicants',
							 **kwargs)

	def add_applicant_to_vacancy(self, *args, **kwargs):
		return requests.post(BASE_URL + f'account/{args[0]}/applicants',
							 **kwargs)


class ClientApi:
	def __init__(self, token, ratelimit=10):
		self.token = token
		self.api = Api()
		self.default_headers = {
			"Authorization": f"Bearer {token}",
			'User-Agent': 'resume_grabber/1.0 (more.pure.i@gmail.com)'
		}
		self.delay = 1 / ratelimit
		self.retries = 3
		# нужно отлавливать исключение при получении id
		r = self.api.accounts(headers=self.default_headers)
		if r.status_code == 401:
			logging.error('token invalid')
		self.account_id = r.json()['items'][0]['id']

	def __request_validation(self, api_call, params=None, headers=None, json_=None,
							 files=None):  # сделано не декоратором для облегчения тестирования
		delay = self.delay
		r = None
		headers = headers or {}
		headers.update(self.default_headers)
		for retry in range(self.retries):
			try:
				r = api_call(
					self.account_id,
					params=params,
					headers=headers,
					json=json_,
					files=files,
				)
			except Exception as e:
				logging.error(f'Error requesting: {e}')
				return None
			if r.status_code is TOO_MANY_REQUESTS_STATUS:  # нужно использовать ratelimiter
				logging.warning(f'Warning, too many requests, retry!')
				time.sleep(delay)
				delay *= 2
			else:
				break

		if r.status_code not in range(200, 300):
			logging.warning(f'Warning, status code of response is {r.status_code}!')

		try:
			json_object = r.json()
			if 'errors' in json_object:
				logging.error(json_object)
				return None
			return {
				'data': json_object,
				'status_code': r.status_code
			}
		except ValueError:
			logging.error('Error: Not valid json returned')
		return None

	def get_opened_vacancies_list(self):
		responce = self.__request_validation(self.api.vacancies)
		if responce is None:
			return None
		if 'items' not in responce['data']:
			return None
		# TODO deserialization
		vacancies = list()
		for vacancy in responce['data']['items']:
			if vacancy['state'] == 'OPEN' and vacancy['hidden'] is False:
				vacancies.append(vacancy)
		return vacancies

	def get_statuses_list(self):
		responce = self.__request_validation(self.api.statuses)
		if responce is None:
			return None
		if 'items' not in responce['data']:
			return None
		return responce['data']['items']

	def upload_resume(self, filepath):
		mime = MimeTypes()
		mime_type = mime.guess_type(filepath)
		responce = self.__request_validation(
			self.api.upload_file,
			headers={
				# 'Content-Type': 'multipart/form-data',
				'X-File-Parse': 'true'
			},
			files={
				'file': (path.basename(filepath), open(filepath, 'rb'), mime_type[0]),
			}
		)
		return responce

	def upload_candidate(self, candidate):
		responce = self.__request_validation(
			self.api.upload_applicant,
			json_=candidate
		)
		candidate['resume_id'] = responce.get('id', None)
		return responce

	def link_candidate_to_vacancy(self, candidate):
		link = {
			'vacancy': candidate['vacancy_id'],
			'status': candidate['status_id'],
			'files': [
				{
					'id': candidate['resume_id']
				}
			],
			'comment': candidate['comment'],
			"rejection_reason": None
		}
		responce = self.__request_validation(
			self.api.add_applicant_to_vacancy(),
			json_=link
		)
		return responce


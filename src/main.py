import argparse
import logging
from os import path
from api import ClientApi
from settings import IMPORT_PROGRESS_FILE
from candidates import get_candidates, add_vacancy_id, add_status_id


parser = argparse.ArgumentParser(description='Huntflow upload candidates script')
parser.add_argument('-t', '--token', help='API token', required=True)
parser.add_argument('-p', '--path', help='Path to database', required=False, default='../db/')
parser.add_argument('-f', '--filename', help='Excel db filename', required=False, default='Тестовая база.xlsx')
args = parser.parse_args()

# получаем данные из апи
try:
	api = ClientApi(args.token)
	vacancies = api.get_opened_vacancies_list()
	statuses = api.get_statuses_list()
except Exception:
	logging.error("Cant get data from api")
	exit(1)

# получаем список претендентов, которых необходимо обработать и добавляем нужные поля
candidates = get_candidates(args.path, args.filename)		# TODO прикрутить норм интерфейс
if candidates is None:
	logging.error("Cant get candidates from db")
	exit(1)
candidates = add_vacancy_id(candidates, vacancies)
if candidates is None:
	logging.error("Cant add vacancy_id")
	exit(1)
candidates = add_status_id(candidates, statuses)
if candidates is None:
	logging.error("Cant add vacancy_id")
	exit(1)

with open(IMPORT_PROGRESS_FILE, 'w+') as file:
	for candidate in candidates:
		cv_data = api.upload_resume(candidate['cv'])
		api.upload_candidate(candidate, cv_data)


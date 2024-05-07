import json

import requests
import requests_html
import bs4
from pprint import pprint
from fake_headers import Headers

'''
1. Нужно выбрать те вакансии, у которых в описании есть ключевые слова "Django" и "Flask".

Описание вакансии - span class=serp-item__title-link serp-item__title

Записать в json информацию о каждой вакансии - ссылка, вилка зп, название компании, город.

Ссылка = a class=bloko-link
ЗП = span class=bloko-header-section-2
Название компании = a class=bloko-link bloko-link_kind-tertiary
Город = div class=bloko-text
'''

def get_main_page(name):
    response = requests.get(name, headers=get_fake_headers())
    return bs4.BeautifulSoup(response.text, features='lxml')


def get_fake_headers():
    return Headers(browser="chrome", os="win").generate()


def find_jobs(main_page):
    jobs_list = main_page.find_all('div', class_='vacancy-serp-item-body__main-info')
    find_jobs_dict = {}
    for job in jobs_list:
        vacancy_name = job.find('span', class_='serp-item__title-link serp-item__title').text
        if str.find(vacancy_name.lower(), 'django') != -1 or str.find(vacancy_name.lower(), 'flask') != -1:
            find_jobs_dict[vacancy_name] = job
    return find_jobs_dict


def write_data_from_vacancies(find_jobs_dict):
    jobs_description = get_jobs_descriptions(find_jobs_dict)
    with open('python_jobs_from_hh.json', 'w', encoding='utf-8') as f:
        json.dump(jobs_description, f, ensure_ascii=False, indent=2)


def get_jobs_descriptions(find_jobs_dict):
    jobs_descriptions = {}
    for job_name, desc in find_jobs_dict.items():
        link = desc.find('a', class_='bloko-link')['href']
        salary = desc.find('span', class_='bloko-header-section-2')
        company_name = desc.find('a', class_='bloko-link bloko-link_kind-tertiary')
        city = desc.find_all('div', class_='bloko-text')
        job_description = {
            'Link': link,
            'Salary': salary.text.encode('utf-8').decode('utf-8').replace(u"\u202f", ".") if salary is not None else '',
            'Company_name': company_name.text.encode('utf-8').decode('utf-8').replace(u"\xa0", " "),
            'City': city[-1].text.encode('utf-8').decode('utf-8').replace(u"\xa02", ".").replace(u"\xa0", ".")
        }
        jobs_descriptions[job_name] = job_description
    return jobs_descriptions


def get_jobs_from_site(name):
    main_page = get_main_page(name)
    find_jobs_dict = find_jobs(main_page)
    write_data_from_vacancies(find_jobs_dict)


if __name__ == '__main__':
    get_jobs_from_site('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2')

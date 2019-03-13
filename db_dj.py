import os, sys
project_dir = os.path.dirname(os.path.abspath('db_dj.py'))
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'find_it.settings'
import django
django.setup()

from django.db import IntegrityError
import datetime
from scraping.utils import *
from scraping.models import *
from subscribers.models import *

def get_all_speciality():
    """Взять все специальности для определённого города"""
    qs = Subscriber.objects.filter(is_active = True)
    todo_list = {i.city: set() for i in qs}  # создаём первоначальный словарь,где ключ - id города
    for i in qs:
        todo_list[i.city].add(i.speciality)  # добавляем в словарь todo_list значения id специальностей
    return todo_list

def get_urls(todo_list):
    """Определяет список из словарей, в которых сгруппированы города и специальности
    с соответствующими им сайтами"""
    url_list = []
    for city in todo_list:  # проходим по ключам городов
        for sp in todo_list[city]:  # проходим в сете по всем значениям, sp - специальность
            tmp = {}  # создаём пустой словарь
            # у нас есть значение city и значение sp
            # выбираем из базы данных урл специальности где есть уже известное нам значение
            # city и sp - числовые значения id
            qs = Url.objects.filter(city=city, speciality=sp)
            if qs:
                tmp['city'] = city  # добавляем в словарь одно(!) значение id города с ключом city
                tmp['speciality'] = sp  # добавляем в словарь одно(!) значение id специальности с ключом speciality
                for item in qs:  # выбираем по одной специальности с перебором городов с этой специальностью из списка qs
                    tmp[item.site.name] = item.url_address #создаём ключ с доменом сайта и значением полным именем сайта
                url_list.append(tmp)
                # добавляем в url-list получившийся словарь с ключами: city, speciality, доменом сайта
    return url_list

def scraping_sites():
    todo_list = get_all_speciality()
    url_list = get_urls(todo_list)
    jobs = []
    for url in url_list:  # выбираем один из словарей в списке url_list
        tmp = {}
        tmp_content = []
        tmp_content.extend(djinni(url['djinni.co'])) if 'djinni.co' in url else None
        tmp_content.extend(rabota(url['rabota.ua'])) if 'rabota.ua' in url else None
        tmp_content.extend(work(url['work.ua'])) if 'work.ua' in url else None
        tmp_content.extend(dou(url['dou.ua'])) if 'dou.ua' in url else None
        tmp_content.extend(hh(url['hh.ru'])) if 'hh.ru' in url else None
        tmp['city'] = url['city']
        tmp['speciality'] = url['speciality']
        tmp['content'] = tmp_content
        jobs.append(tmp)
    return jobs

def save_to_db():
    all_data = scraping_sites()
    if all_data:
       for data in all_data:
           city = data['city']
           speciality = data['speciality']
           jobs = data['content']
           for job in jobs:
               vacancy = Vacancy(city=city, speciality=speciality, url=job['href'],
                                 title=job['title'], description=job['descript'], company=job['company'])
               try:
                   vacancy.save()
               except IntegrityError:
                   pass

    return True

print(save_to_db())
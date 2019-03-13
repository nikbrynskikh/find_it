import psycopg2
import logging
import datetime
from scraping.utils import *
from find_it.secret import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

today = datetime.date.today()
ten_days_ago = datetime.date.today() - datetime.timedelta(10)
try:
    conn = psycopg2.connect(dbname =DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD)
except:
    logging.exception('Unable to open DB - {}'.format(today))
else:
    cur = conn.cursor()
    cur.execute("""SELECT city_id, speciality_id FROM subscribers_subscriber WHERE is_active=%s;""", (True,))
    cities_qs = cur.fetchall() #создаём список кортежей: (город, специальность) из тех подписчиков, которые подписаны
    todo_list = {i[0]:set() for i in cities_qs} #создаём первоначальный словарь
    for i in cities_qs:
        todo_list[i[0]].add(i[1]) #добавляем в словарь todo_list значения специальностей
    cur.execute("""SELECT * FROM scraping_site;""") #сайты (главные страницы) с вакансиями
    sites_qs = cur.fetchall()
    cur.execute("""SELECT site_id, city_id FROM scraping_url;""")
    city_st = cur.fetchall() #выбираем сайты соответствующие городам
    city_site = {i[0]:i[1] for i in city_st} #делаем словарь, ключи - id сайта, значения - города
    sites_id = {i[0]:i[1] for i in sites_qs} #делаем словарь, ключи - id сайта, значения - адрес сайта
    sites = [(city_site[i],sites_id[i]) for i in sites_id] #список из кортежа, где id сайтов и домены сайта
    url_list = []
    for city in todo_list: #проходим по ключам городов
        for sp in todo_list[city]: #проходим в сете по всем значениям, sp - специальность
            tmp = {} #создаём пустой словарь
            # у нас есть значение city и значение sp
            # выбираем из базы данных урл специальности где есть уже известное нам значение
            # city и sp - числовые значения id
            cur.execute("""SELECT city_id, url_address FROM scraping_url
                            WHERE city_id=%s AND speciality_id=%s""", (city, sp))
            qs = cur.fetchall() #получаем несколько списков, каждый из которых состоит из кортежей
            if qs:
                tmp['city'] = city #добавляем в словарь одно(!) значение id города с ключом city
                tmp['speciality'] = sp #добавляем в словарь одно(!) значение id специальности с ключом speciality
                for item in qs: #выбираем по одному кортежу из списка qs
                    town_id = item[0] #выбираем из кортежа id города
                    #добавляем в словарь tmp одно значение, где ключ - домен сайта, а значение - путь сайта со специальностью
                    for i in sites:
                        if town_id == i[0] and (i[1] in item[1]):
                            tmp[i[1]] = item[1]
                url_list.append(tmp)
                #добавляем в url-list получившийся словарь с ключами: city, speciality, доменом сайта
    all_data = []
    if url_list:
        for url in url_list: #выбираем один из словарей в списке url_list
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
            all_data.append(tmp)
    if all_data:
       for data in all_data:
           city = data['city']
           speciality = data['speciality']
           jobs = data['content']
           for job in jobs:
               cur.execute("""SELECT * FROM scraping_vacancy WHERE url=%s;""", (job['href'],))
               qs = cur.fetchall()
               if not qs:
                   cur.execute("""INSERT INTO scraping_vacancy ( city_id, speciality_id, title, url, description, company, timestamp) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s);""", (city, speciality, job['title'], job['href'], job['descript'], job['company'], today ))

    cur.execute("""DELETE FROM scraping_vacancy WHERE timestamp<=%s;""", (ten_days_ago,))
    conn.commit()

    cur.close()
    conn.close()
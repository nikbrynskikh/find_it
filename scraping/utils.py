import requests
from bs4 import BeautifulSoup as BS
import codecs
import time
import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

def djinni(base_url):
    session = requests.Session()
    # base_url = 'https://djinni.co/jobs/?primary_keyword=Python&location=%D0%9A%D0%B8%D0%B5%D0%B2'
    domain = 'https://djinni.co'

    jobs = []
    urls =[]
    urls.append(base_url)
    urls.append(base_url+'&page=2')

    for url in urls:
        time.sleep(2)
        req = session.get(url, headers=headers)
        if  req.status_code == 200:
            bsobj = BS(req.content, 'html.parser')
            li_list = bsobj.find_all('li', attrs={'class':'list-jobs__item'})
            for li in li_list:
                div = li.find('div', attrs={'class': 'list-jobs__title'})
                title = div.a.text
                href = div.a['href']
                short = 'No description'
                descr = li.find('div', attrs={'class': 'list-jobs__description'})
                if descr:
                    short = descr.p.text
                jobs.append({'href': domain+href,
                             'title': title,
                             'descript': short,
                             'company': 'No name'})
    return jobs

def rabota(base_url):
    session = requests.Session()
    # base_url = 'https://rabota.ua/jobsearch/vacancy_list?regionId=1&keyWords=python&period=2&lastdate='
    domain = 'https://rabota.ua'

    jobs = []
    urls = []
    yesterday = datetime.date.today() - datetime.timedelta(1)
    one_day_ago = yesterday.strftime('%d.%m.%Y')
    base_url += one_day_ago

    urls.append(base_url)

    req = session.get(base_url, headers=headers)
    if req.status_code == 200:
        bsObj = BS(req.content, "html.parser")
        pagination = bsObj.find('dl', attrs={'id': 'content_vacancyList_gridList_pagerInnerTable'})
        if pagination:
            pages = pagination.find_all('a', attrs={'class': 'f-always-blue'})
            for page in pages:
                urls.append(domain + page['href'])
                print(page)

    for url in urls:
        time.sleep(2)
        req = session.get(url, headers=headers)
        if req.status_code == 200:
            bsobj = BS(req.content, 'html.parser')
            table = bsObj.find('h3', attrs={'class': 'f-vacancylist-vacancytitle'})
            if table:
                tr_list = bsobj.find_all('tr', attrs={'id': True})
                for tr in tr_list:
                    h3 = tr.find('h3', attrs={'class': 'f-vacancylist-vacancytitle'})
                    title = h3.text
                    href = h3.a['href']
                    short = 'No description'
                    company = 'No name'
                    logo = tr.find('p', attrs={'class': 'f-vacancylist-companyname'})
                    if logo:
                        company = logo.a.text
                    p = tr.find('p', attrs={'class': 'f-vacancylist-shortdescr'})
                    if p:
                        short = p.text
                    jobs.append({'href': href,
                                 'title': title,
                                 'descript': short,
                                 'company': company})

    return jobs

def work(base_url):
    session = requests.Session()
    # base_url = 'https://www.work.ua/jobs-kyiv-python'
    req = session.get(base_url, headers=headers)
    domain = 'https://www.work.ua'
    jobs = []
    urls = []

    urls.append(base_url)
    if req.status_code == 200:
        bsobj = BS(req.content, 'html.parser')
        pagination = bsobj.find('ul', attrs={'class': 'pagination'})
        if pagination:
            pages = pagination.find_all('li', attrs={'class': False})
            for page in pages:
                urls.append(domain + page.a['href'])

    for url in urls:
        time.sleep(2)
        req = session.get(url, headers=headers)
        if req.status_code == 200:
            bsobj = BS(req.content, 'html.parser')
            div_list = bsobj.find_all('div', attrs={'class': 'job-link'})
            for div in div_list:
                title = div.find('h2')
                href = title.a['href']
                short = div.p.text
                company = 'No name'
                logo = div.find('img')
                if logo:
                    company = logo['alt']
                jobs.append({'href': domain + href,
                             'title': title.text,
                             'descript': short,
                             'company': company})
    return jobs

def dou(base_url):
    session = requests.Session()
    # base_url = 'https://jobs.dou.ua/vacancies/?city=%D0%9A%D0%B8%D0%B5%D0%B2&category=Python'
    jobs = []
    urls = []

    urls.append(base_url)

    for url in urls:
        time.sleep(2)
        req = session.get(url, headers=headers)
        if req.status_code == 200:
            bsobj = BS(req.content, 'html.parser')
            div = bsobj.find('div', attrs={'id': 'vacancyListId'})
            if div:
                li_list = bsobj.find_all('li', attrs={'class': 'l-vacancy'})
                for li in li_list:
                    a = li.find('a', attrs={'class': 'vt'})
                    title = a.text
                    href = a['href']
                    short = 'No description'
                    company = 'No name'
                    a_company = li.find('a', attrs={'class': 'company'})
                    if a_company:
                        company = a_company.text
                    descr = li.find('div', attrs={'class': 'sh-info'})
                    if descr:
                        short = descr.text
                    jobs.append({'href': href,
                                 'title': title,
                                 'descript': short,
                                 'company': company})
    return jobs

def hh(base_url):
    jobs = []
    pagination_urls = []
    session = requests.Session()
    # base_url = 'https://hh.ru/search/vacancy?search_period=3&clusters=true&area=1&text=python&enable_snippets=true'
    pagination_urls.append(base_url)
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        soup_pagination = BS(request.content, 'html.parser')
        pagination = soup_pagination.find('span', attrs={'class': 'bloko-button-group'})
        expected_lens = pagination.find_all('a', href = True)
        for i in expected_lens:
            pagination_urls.append('https://hh.ru' + i.get('href'))
        for url in pagination_urls:
            request = session.get(url, headers=headers)
            soup = BS(request.content, 'html.parser')
            divs = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
            for div in divs:
                title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                text_resp = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
                text_requir = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
                content = text_resp + ' ' + text_requir
                jobs.append({'href': href,
                             'title': title,
                             'descript': content,
                             'company': company})
    else:
        print('ERROR')

    return jobs
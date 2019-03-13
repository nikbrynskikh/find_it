import requests
from bs4 import BeautifulSoup as BS

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

base_url = 'https://hh.ru/search/vacancy?search_period=3&clusters=true&area=1&text=python&enable_snippets=true'

def hh(base_url, headers):
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
        print()
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

hh(base_url, headers)
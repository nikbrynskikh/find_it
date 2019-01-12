from django.shortcuts import render
from django.db import IntegrityError
from scraping.utils import *
from scraping.models import *


def home(request):
    jobs = []
    jobs.extend(djinni())
    jobs.extend(rabota())
    jobs.extend(work())
    jobs.extend(dou())
    jobs.extend(hh())
    city = City.objects.get(name='Киев')
    speciality = Speciality.objects.get(name='Python')
    # v = Vacancy.objects.filter(city=city.id, speciality=speciality.id).values('url')
    # url_list = [i['url'] for i in v]
    for job in jobs:
        vacancy = Vacancy(city=city, speciality=speciality, url=job['href'],
                          title=job['title'], descriprion=job['descript'], company=job['company'])
        try:
            vacancy.save()
        except IntegrityError:
            pass

    return render(request, 'base.html', {'jobs':jobs})


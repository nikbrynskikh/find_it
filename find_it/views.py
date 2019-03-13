from django.shortcuts import render
from django.db import IntegrityError
import datetime
from scraping.utils import *
from scraping.models import *
from scraping.forms import FindVacancyForm
from django.http import Http404

def index(request):
    return render(request, 'base.html')


# def list_vacancy(request):
#     today = datetime.date.today()
#     city_k = City.objects.get(name='Киев')
#     city_m = City.objects.get(name='Москва')
#     speciality = Speciality.objects.get(name='Python')
#     qs_k = Vacancy.objects.filter(city=city_k.id, speciality=speciality.id, timestamp = today) #QuerySet список вакансий
#     if qs_k:
#         return render(request, 'scraping/list.html', {'jobs': qs_k})
#     else:
#         return render(request, 'scraping/list.html')

def vacancy_list(request):
    today = datetime.date.today()
    form = FindVacancyForm
    if request.GET:
        try:
            city_id = int(request.GET.get('city')) #город - пока или Киев или Москва
            speciality_id = int(request.GET.get('speciality')) #специальность
        except ValueError:
            raise Http404('Страница не найдена')
        context = {}
        context['form'] = form
        qs = Vacancy.objects.filter(city=city_id, speciality=speciality_id,
                                      timestamp=today)  # QuerySet список вакансий
        if qs:
            context['jobs'] = qs
            return render(request, 'scraping/list.html', context)

    return render(request, 'scraping/list.html', {'form': form})

def home(request):
    city_k = City.objects.get(name='Киев')
    city_m = City.objects.get(name='Москва')
    speciality = Speciality.objects.get(name='Python')
    url_qs_k = Url.objects.filter(city=city_k, speciality=speciality) #QuerySet список urlов
    url_qs_m = Url.objects.filter(city=city_m, speciality=speciality) #QuerySet список urlов
    site = Site.objects.all()
    url_w = url_qs_k.get(site=site.get(name='work.ua')).url_address
    url_dj = url_qs_k.get(site=site.get(name='djinni.co')).url_address
    url_r = url_qs_k.get(site=site.get(name='rabota.ua')).url_address
    url_dou = url_qs_k.get(site=site.get(name='dou.ua')).url_address
    url_hh = url_qs_m.get(site=site.get(name='hh.ru')).url_address
    jobs_ukr = []
    jobs_ukr.extend(djinni(url_dj))
    jobs_ukr.extend(rabota(url_r))
    jobs_ukr.extend(work(url_w))
    jobs_ukr.extend(dou(url_dou))

    jobs_rus = []
    jobs_rus.extend(hh(url_hh))

    for job in jobs_ukr: #проходим по специальностям на украинских сайтах
        vacancy = Vacancy(city=city_k, speciality=speciality, url=job['href'],
                          title=job['title'], descriprion=job['descript'], company=job['company'])
        try:
            vacancy.save()
        except IntegrityError:
            pass

    for job in jobs_rus: #проходим по специальностям на российских сайтах
        vacancy = Vacancy(city=city_m, speciality=speciality, url=job['href'],
                          title=job['title'], descriprion=job['descript'], company=job['company'])
        try:
            vacancy.save()
        except IntegrityError:
            pass
    jobs = jobs_ukr + jobs_rus #работы на украинских и на российских сайтах

    return render(request, 'scraping/list.html', {'jobs':jobs})


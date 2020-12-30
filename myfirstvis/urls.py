from django.conf.urls import url
from django.urls import include
from . import views


urlpatterns = [

    url('login/', views.login),
    url('register/', views.register),
    url('logout/', views.logout),
    # url('captcha/', include('captcha.urls')),
    url('crawl/', views.crawlNews),
    url('index/', views.index),
    url('analysis/', views.analysis),
    url('region/', views.region),
    url('evaluation/', views.evaluation),
    url('sentiment/', views.sentiment),
    url('individual/', views.individual),

    # url('region/', views.region, name='region'),
    # url(r'^news$', views.news, name='news'),
    # url(r'^sentiment$', views.sentiment, name='sentiment'),
    # url(r'^demo', views.demo, name='demo'),
    # url(r'^', views.index, name='index')
    url(r'^', views.individual, name='individual')
    # url(r'^', views.default, name='default')
]


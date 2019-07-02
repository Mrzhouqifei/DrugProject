from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^region$', views.region, name='region'),
    url(r'^news$', views.news, name='news'),
    url(r'^sentiment$', views.sentiment, name='sentiment'),
    url(r'^demo', views.demo, name='demo'),
]

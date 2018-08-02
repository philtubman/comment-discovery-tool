from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^ltilaunch/$', views.ltilaunch, name='ltilaunch'),
    url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    url(r'^results/$', views.results, name='results'),
    url(r'^uploadcomments/$', views.uploadcomments, name='uploadcomments'),
    url(r'^uploadbadwords/$', views.uploadbadwords, name='uploadbadwords'),
    url(r'^data/terms/(?P<flavour>\w{1,8})/$', views.terms, name='terms'),
    url(r'^data/logclick$', views.log_click, name='log_click'),
]

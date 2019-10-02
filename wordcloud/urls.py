from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ltilaunch/$', views.ltilaunch, name='ltilaunch'),
    url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    url(r'^results/$', views.results, name='results'),
    url(r'^uploadcomments/$', views.uploadcomments, name='uploadcomments'),
    url(r'^uploadbadwords/$', views.uploadbadwords, name='uploadbadwords'),
    url(r'^data/terms$', views.terms, name='terms'),
    url(r'^data/logclick$', views.log_click, name='log_click'),
    url(r'^data/courses$', views.courses, name='courses'),
    url(r'^data/weeks$', views.weeks, name='weeks'),
    url(r'^data/comment$', views.comment, name='comment'),
]

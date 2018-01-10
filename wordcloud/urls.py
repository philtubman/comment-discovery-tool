from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ltilaunch/$', views.ltilaunch, name='ltilaunch'),
    url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
]

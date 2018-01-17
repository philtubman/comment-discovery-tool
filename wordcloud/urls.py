from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ltilaunch/$', views.ltilaunch, name='ltilaunch'),
    url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    url(r'^commenttable/$', views.commenttable, name='commenttable'),
    url(r'^twowordsresults/$', views.twowordsresults, name='twowordsresults'),
    url(r'^uploadcsv/$', views.uploadcsv, name='uploadcsv'),
    url(r'^data/terms$', views.terms, name='terms'),
]

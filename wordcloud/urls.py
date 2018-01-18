from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ltilaunch/$', views.ltilaunch, name='ltilaunch'),
    url(r'^wordcloud/$', views.wordcloud, name='wordcloud'),
    url(r'^onewordresults/$', views.onewordresults, name='onewordresults'),
    url(r'^twowordsresults/$', views.twowordsresults, name='twowordsresults'),
    url(r'^uploadcomments/$', views.uploadcomments, name='uploadcomments'),
    url(r'^uploadbadwords/$', views.uploadbadwords, name='uploadbadwords'),
    url(r'^data/terms$', views.terms, name='terms'),
]

from django.conf.urls import url

from .views import Declaration


urlpatterns = [
    url(r'^declaration/?$', Declaration.as_view(), name='form'),
]

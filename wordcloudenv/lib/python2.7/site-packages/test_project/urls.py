from django.conf.urls import include, url

urlpatterns = [
    url('', include('declaration.urls', namespace='declaration')),
]

from django.conf.urls import url
from .views import homepage
from django.urls import path

app_name='main'

urlpatterns = [
    path('',homepage,name='homepage'),
]

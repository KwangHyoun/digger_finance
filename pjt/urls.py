from django.urls import path
from . import views

app_name = 'pjt'
urlpatterns = [
    path('', views.index, name='index'),
]   
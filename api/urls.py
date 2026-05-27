from fnmatch import translate

from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('translate/', views.translate_view, name='translate'),
    path('api/translate/', views.TranslateWordAPI.as_view(), name='api_translate'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]
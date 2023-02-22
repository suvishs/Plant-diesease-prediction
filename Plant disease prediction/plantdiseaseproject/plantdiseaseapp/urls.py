from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('login_view', views.login_view, name='login_view'),
    path('register', views.register, name='register'),
    path('home', views.home, name='home'),
    path('result', views.result, name='result'),
]

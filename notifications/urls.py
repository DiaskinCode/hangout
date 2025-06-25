from django.urls import path

from . import views

urlpatterns = [
    path('', views.GetNotifications, name='post-notification'),
]
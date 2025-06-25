from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from . import views

urlpatterns = [
    path('', views.users, name = 'users'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),
    path('refresh_token/', TokenRefreshView.as_view(), name='refresh_token'),
    
    path('profile/<str:username>', views.profile, name='profile'),    
    path('profile_update/', views.UserProfileUpdate.as_view(), name="profile_update"), 
    
]
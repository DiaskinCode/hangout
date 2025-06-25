from tkinter import EW
from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import HttpResponse
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

from .models import Notification
from posts.models import Post
from users.models import UserProfile

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def GetNotifications(request):
    user = request.user
    notification = Notification.objects.get(to_user = user)
    notification.user_has_seen = True

    serializer = NotificationSerializer(notification, many=False)
    
    return Response(serializer.data)


    
    

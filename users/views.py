import uuid
import os.path

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
#email verification imports
from django.contrib.auth.tokens import default_token_generator
from django.core.files.storage import default_storage
# from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Q , Count
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from email_validator import validate_email, EmailNotValidError
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


from .models import UserProfile, TopicTag
from friend.models import FriendList,FriendRequest
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus
from .serializers import UserSerializerWithToken, UserProfileSerializer, UserSerializer




def email_validator(email):
    """vali dates & return the entered email if correct
    else returns an exception as string"""
    try:
        validated_email_data = validate_email(email)
        email_add = validated_email_data['email']
        return email_add
    except EmailNotValidError as e:
        return str(e)

# Create your views here.

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data
        username = data.get('username') 
        email = data.get('email')
        password = data.get('password')
        email_valid_check_result = email_validator(email)
        messages = {'errors':[]}
        if username == None:
            messages['errors'].append('username can\'t be empty')
        if email == None:
            messages['errors'].append('Email can\'t be empty')
        if not email_valid_check_result == email:
            messages['errors'].append(email_valid_check_result)
        if password == None:
            messages['errors'].append('Password can\'t be empty')
        if User.objects.filter(email=email).exists():
            messages['errors'].append("Account already exists with this email id.")    
        if User.objects.filter(username__iexact=username).exists():
            messages['errors'].append("Account already exists with this username.") 
        if len(messages['errors']) > 0:
            return Response({"detail":messages['errors']},status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            serializer = UserSerializerWithToken(user, many=False)
        except Exception as e:
            print(e)
            return Response({'detail':f'{e}'},status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

@api_view(['GET'])
def users(request):
    query = request.query_params.get('q') or ''
    users = User.objects.filter(
        Q(userprofile__name__icontains=query) | 
        Q(userprofile__username__icontains=query)
    ).order_by('-userprofile__followers_count')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(users,request)
    serializer = UserSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['name'] = user.userprofile.name
        token['profile_pic'] = 'static' + user.userprofile.profile_pic.url
        token['is_staff'] = user.is_staff
        token['id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs) 

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
class UserProfileUpdate(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    http_method_names = ['patch', 'head']


    def patch(self, *args, **kwargs):
        profile = self.request.user.userprofile
        serializer = self.serializer_class(
            profile, data=self.request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save().user
            new_email = self.request.data.get('email')
            user = self.request.user
            if new_email is not None:
                user.email = new_email
                profile.email_verified = False
                user.save()
                profile.save()
            return Response({'success': True, 'message': 'successfully updated your info',
                        'user': UserSerializer(user).data,'updated_email': new_email}, status=200)
        else:
            response = serializer.errors
            return Response(response, status=401)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def profile(request,username):
    context = {}
    user = request.user
    profile = UserProfile.objects.get(username=username)
    
    try:
        friend_list = FriendList.objects.get(user=profile.user)
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=profile)
        friend_list.save()
    friends = friend_list.friends.all()

    # NO_REQUEST_SENT = -1 
    # THEM_SENT_TO_YOU = 0
    # YOU_SENT_TO_THEM = 1
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value 

    is_self = True
    is_friend = False

    if user != profile.user:
        is_self = False
        if friends.filter(pk=user.id):
            is_friend = True
        else:
            is_friend = False
		    # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
            if get_friend_request_or_false(sender=profile.user, receiver=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=profile.user, receiver=user).id
			# CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
            elif get_friend_request_or_false(sender=user, receiver=profile.user) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
			# CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value


    context['is_self'] = is_self
    context['is_friend'] = is_friend
    context['request_sent'] = request_sent
        
    serializer_user = UserProfileSerializer(profile,many=False)
    
    context['friends'] = friends.count()
    context['profile_info'] = serializer_user.data
    return Response(context)

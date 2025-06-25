from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from .models import UserProfile, TopicTag

class TopicTagSerializer(serializers.Serializer):
    name = serializers.CharField()
    class Meta:
        model = TopicTag
        fields = '__all__'

class UserProfileSerializer(serializers.Serializer):
    user = serializers.StringRelatedField(many=False)
    name = serializers.CharField()
    username = serializers.CharField()
    profile_pic = serializers.ImageField()
    bio = serializers.CharField()
    vote_ratio = serializers.IntegerField( default=0)
    followers_count = serializers.IntegerField( default=0)
    interests = serializers.StringRelatedField(many = True)
    followers = serializers.StringRelatedField(many = True)
    follows = serializers.StringRelatedField(many = True)
    email_verified = serializers.BooleanField(default=False)
    id = serializers.UUIDField()
    
    profile_pic = serializers.SerializerMethodField(read_only=True)
    interests = TopicTagSerializer(many=True, read_only=True)
    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_profile_pic(self, obj):
        try:
            pic = obj.profile_pic.url
        except:
            pic = None
        return pic

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    username = serializers.CharField()
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    profile = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'profile', 'username', 'is_superuser', 'is_staff']

    def get_profile(self, obj):
        profile = obj.userprofile
        serializer = UserProfileSerializer(profile, many=False)
        return serializer.data


class UserSerializerWithToken(UserSerializer):
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        exclude = ['password']

    def get_access(self, obj):
        token = RefreshToken.for_user(obj)

        token['username'] = obj.username
        token['name'] = obj.userprofile.name
        token['profile_pic'] = obj.userprofile.profile_pic.url
        token['is_staff'] = obj.is_staff
        token['id'] = obj.id
        return str(token.access_token)
    
    def get_refresh(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token)
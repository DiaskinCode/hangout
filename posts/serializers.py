from rest_framework import serializers
from .models import Post, PostComment, User
from users.serializers import UserProfileSerializer, TopicTagSerializer

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)
    headline = serializers.CharField(max_length=500)
    description = serializers.CharField(max_length=30)
    content = serializers.CharField(max_length=10000)
    likes = serializers.StringRelatedField(many=True)
    image = serializers.ImageField()
    location = serializers.CharField(max_length=300)
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    tags = TopicTagSerializer(many=True, read_only=True)
    private = serializers.BooleanField()
    isapplyforjoin = serializers.BooleanField()
    time = serializers.DateTimeField()
    created = serializers.DateTimeField()

    def get_author(self, obj):
        author = obj.author.userprofile
        serializer = UserProfileSerializer(author, many=False)
        return serializer.data
    
    class Meta:
        model = Post
        fields = '__all__'



class PostCommentSerializer(serializers.Serializer):
    author = serializers.SerializerMethodField(read_only=True)
    parent = serializers.StringRelatedField(many = False)
    id = serializers.IntegerField(read_only = True)
    post = serializers.StringRelatedField(many = False)
    content = serializers.CharField(max_length=1000)
    created = serializers.DateTimeField()

    def get_author(self, obj):
        author = obj.author.userprofile
        serializer = UserProfileSerializer(author, many=False)
        return serializer.data
    
    class Meta:
        model = PostComment
        fields = '__all__'
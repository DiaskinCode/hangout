from email.policy import default
from pydoc import describe
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from users.models import UserProfile
from users.models import TopicTag
import uuid

# Create your models here.

class Post(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)
    author = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    headline = models.CharField(max_length=500, default="no headline")
    description = models.TextField(max_length=30)
    content = RichTextField(max_length=1200)
    likes = models.ManyToManyField(User,default=0,related_name='post_likes')
    image = models.ImageField(blank=False, null=True, default='default.png')
    location = models.CharField(max_length=300)
    isapplyforjoin = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    tags = models.ManyToManyField(TopicTag, related_name='post_tags', blank=True) 
    time = models.DateTimeField()
    private = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.headline)

class PostComment(models.Model):
    id = models.UUIDField(default=uuid.uuid4,  unique=True, primary_key=True, editable=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    likes = models.ManyToManyField(User,default=0,related_name='postcomment_likes')
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name='postcomment_post')
    author = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    
    
    def __str__(self):
        return str(self.author.username)


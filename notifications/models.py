from django.db import models

# Create your models here.
from email.policy import default
from pydoc import describe
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from posts.models import Post
from posts.models import PostComment
from users.models import TopicTag
import uuid

class Notification(models.Model):
    # 1 = like 2 = Commnet 3 follow
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User,on_delete=models.CASCADE , null=True, blank=True,related_name='notification_to') 
    from_user = models.ForeignKey(User,on_delete=models.CASCADE , null=True, blank=True,related_name='notification_from') 
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    comment = models.ForeignKey(PostComment,on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    content= models.CharField(max_length=70,null=True)
    user_has_seen = models.BooleanField(default=False)

    def __str__(self):
        return str(self)
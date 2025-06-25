from django.db import models
from posts.models import Post
from users.models import User
# Create your models here.
        
class Lobby(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='lobby_post')
    participants = models.ManyToManyField(User, related_name='meetings')

class JoinRequest(models.Model):
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name="join_sender")
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name="join_receiver")
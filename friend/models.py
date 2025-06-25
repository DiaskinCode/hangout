from os import remove
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

# Create your models here.

class FriendList(models.Model):
     # user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(User,blank=True,related_name="friends")

    def __str__(self):
        return self.user.username

    def add_friend(self,account):
        if not account in self.friends.all():
            self.friends.add(account)

    def remove_friend(self,account):
        if not account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self,removee):
        self.remove_friend(removee)
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(self.user)
    
    def is_mutual_friend(self,friend):
        if friend in self.friends.all():
            return True
        return False

class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="receiver")

    is_active = models.BooleanField(null=False, default=True)

    def accept(self,user,receiver):
        """
		Accept a friend request.
		"""
        receiver_friend_list = FriendList.objects.get(user=receiver)
        if receiver_friend_list:
            receiver_friend_list.add_friend(user)

            sender_friend_list = FriendList.objects.get(user=user)
            if sender_friend_list:

                sender_friend_list.add_friend(receiver)
                sender_friend_list.save()
                self.is_active = False
                self.save()
    

    def cancel(self):
        self.delete()
        





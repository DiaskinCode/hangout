from django.shortcuts import render
from django.http import HttpResponse
import json

from users.models import UserProfile    
from friend.models import FriendRequest, FriendList

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def send_friend_request(request,username,*args, **kwargs):
    user = request.user
    payload = {}
    receiver = UserProfile.objects.get(username=username)
    users_userprofile = UserProfile.objects.get(user=user)
    receivers_userprofile = UserProfile.objects.get(user=receiver.user)

    try:
        friendlist = FriendList.objects.get(user = receiver.user)

        if user == receiver.user:
            return HttpResponse("You can not send friend request yourself")
        try:
            friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver.user)
            try:
                for reqeust in friend_requests:
                    if reqeust.is_active:
                        raise Exception("you already sent them a friend request")
                friend_request = FriendRequest(sender=user, receiver=receiver.user)
                friend_request.save()
                users_userprofile.follows.add(receiver.user)
                receivers_userprofile.followers.add(user)
                payload['response'] = "Friend request sent. You follow " + receiver.username
                
            except Exception as e:
                payload['response'] = str(e)
        except FriendRequest.DoesNotExist:
            friend_request = FriendRequest(sender=user, receiver=receiver.user)
            friend_request.save()
            payload['response'] = "Friend request sent."

            if payload['response'] == None:
                payload['response'] = "Something went wrong"

    except FriendList.DoesNotExist:  
        friendlist = FriendList.objects.create(
            user = user
        )
        friendlist_receiver = FriendList.objects.create(
            user = receiver.user
        )

        friend_request = FriendRequest(sender=user, receiver=receiver.user)
        friend_request.save()

        friendlist.save()
        friendlist_receiver.save()
        payload['response'] = "Friend List created, Friend request sent."

    return HttpResponse(json.dumps(payload), content_type="application/json")


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def accept_friend_request(request,friend_request_user, *args, **kwargs):
    user = request.user
    payload = {} 

    accepter = UserProfile.objects.get(username=friend_request_user)

    if friend_request_user:
        friend_request = FriendRequest.objects.filter(sender=accepter.user,is_active = True).first()
        friendlist = FriendList.objects.get(user = user)
        # confirm that is the correct request
        if friend_request.receiver == user:
            if friend_request: 
                # found the request. Now accept it
                friend_request.accept(user,accepter.user)
                friendlist.add_friend(accepter.user)
                accepter.followers.add(user)
                payload['response'] = "Friend request accepted."

            else:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "That is not your request to accept."
    else:
        payload['response'] = "Unable to accept that friend request."

    # except FriendList.DoesNotExist:  
    #     friendlist = FriendList.objects.get(user = user)
    #     friendlist.friends.add(user)
    #     # ПЕРЕНЕСТИ ЭТО В АЦЕПТ 
    #     friendlist.save()
    #     payload['response'] = friendlist

    return HttpResponse(json.dumps(payload), content_type="application/json")

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def cancel_friend_request(request,receiver_username, *args, **kwargs):
    user = request.user
    users_userprofile = UserProfile.objects.get(user=user)
    receivers_userprofile = UserProfile.objects.get(username=receiver_username)
    payload = {}

    if receiver_username:
        receiver = UserProfile.objects.get(username=receiver_username)
        try:
            friendlist = FriendList.objects.get(user = user)
            friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver.user, is_active=True)
        except FriendRequest.DoesNotExist:
            payload['response'] = "Nothing to cancel. Friend request does not exist."

			# There should only ever be ONE active friend request at any given time. Cancel them all just in case.
        if len(friend_requests) > 1:
            for request in friend_requests:
                request.cancel()
            payload['response'] = "Friend request canceled."
        else:
			# found the request. Now cancel it
            friend_requests.first().delete()
            friendlist.friends.remove(receiver.user)
            users_userprofile.follows.remove(receiver.user)
            receivers_userprofile.followers.remove(user)
            payload['response'] = "Friend request canceled."
    else:
        payload['response'] = "Unable to cancel that friend request."
        # should never happen
        payload['response'] = "You must be authenticated to cancel a friend request."
    return HttpResponse(json.dumps(payload), content_type="application/json")




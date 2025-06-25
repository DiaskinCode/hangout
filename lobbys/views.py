# from datetime import date
from django.dispatch import receiver
from users.models import UserProfile
from posts.serializers import PostCommentSerializer
from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
import json

from posts.models import Post, PostComment
from .models import Lobby,JoinRequest
from notifications.models import Notification
from posts.serializers import PostSerializer, PostCommentSerializer
from users.models import TopicTag

# Create your views here.
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def CommentsList(request,pk):
    # user = request.user
    post = Post.objects.get(id=pk)
    comments = PostComment.objects.filter(post=post)
    serializer = PostCommentSerializer(comments, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def CommentCreate(request,pk):
    user = request.user
    post = Post.objects.get(id=pk)
    data = request.data
    content = data.get('content')
    
    if data.get('parent') is not None:
        parent = PostComment.objects.get(id = data.get('parent'))
        comment = PostComment.objects.create(
            author=user,
            post = post,
            parent = parent,
            content = content,
        )  

    else:
        comment = PostComment.objects.create(
            author=user,
            post = post,
            content = content,
        )   
    
    if post.author != user:
        Notification.objects.create(notification_type=2, from_user=user, to_user=post.author, post=post) 
    
    comment.save()
    serializer = PostCommentSerializer(comment, many=False)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def CommentDelete(request,pk):
    try:
        comment = PostComment.objects.get(id=pk)
        if comment.author == request.user:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'detail':f'{e}'},status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def CommentLike(request,pk):
    user = request.user
    try:
        comment_to_like = PostComment.objects.get(id=pk)
        if user == comment_to_like.author: 
            return Response('You can not like your own like')
        if user in comment_to_like.likes.all():
            comment_to_like.likes.remove(user)
            comment_to_like.save()
            return Response('Comment unlike')
        else:
            comment_to_like.likes.add(user)
            comment_to_like.save()
            return Response('Comment liked')
    except Exception as e:
        message = {'detail':f'{e}'}
        return Response(message,status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def SendRequestToJoin(request,pk):
    payload = {}

    userprofile = UserProfile.objects.get(user=request.user)
    post = Post.objects.get(id=pk)
    receiver = post.author

    if receiver == userprofile.user:
        payload['response'] = "You cant send join request to yourself." + status.HTTP_204_NO_CONTENT
    else:
        try:
            lobby = Lobby.objects.get(post=post)
            if post.isapplyforjoin == False:
                lobby.participants.add(userprofile.user)
                payload['response'] = "You joined"
            else:
                if JoinRequest.objects.get(sender=userprofile.user, receiver=receiver):
                    payload['response'] = "You already sent join request"
                join_request = JoinRequest(sender=userprofile.user, receiver=receiver)
                join_request.save()

                payload['response'] = "Join request sent to " + post.id
        except Lobby.DoesNotExist:
            lobby = Lobby.objects.create(post=post)
            join_request = JoinRequest(sender=userprofile.user, receiver=receiver)
            join_request.save()

            payload['response'] = "Join request sent."

            if payload['response'] == None:
                payload['response'] = "Something went wrong"
    return HttpResponse(json.dumps(payload), content_type="application/json")
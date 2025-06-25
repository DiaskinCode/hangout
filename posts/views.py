from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

from .models import Post, PostComment
from .serializers import PostSerializer, PostComment
from users.models import TopicTag


# Create your views here.
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_post(request):
    user = request.user
    data = request.data
    # content = data.get('content')
    tags = data.get('tags')
    headline = data.get('headline')
    description = data.get('description')
    image = data.get('image')
    price = data.get('price')
    isapplyforjoin = data.get('isapplyforjoin')
    if price !=  '00.00':
        private = True
    else:
        private = False
    location = data.get('location')
    time = data.get('time')
    post = Post.objects.create(
        author=user,
        # content=content,
        headline=headline,
        price = price,
        description=description,
        image=image,
        private = private,
        isapplyforjoin = isapplyforjoin,
        location=location,
        time=time
    )
    if tags is not None:
        for tag_name in tags:
            tag_instance = TopicTag.objects.filter(name=tag_name).first()
            if not tag_instance:
                tag_instance = TopicTag.objects.create(name=tag_name)
            post.tags.add(tag_instance)
    post.save()
    
    serializer = PostSerializer(post, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def edit_post(request,pk):
    try:
        post= Post.objects.get(id=pk)
        if post.user == request.user:
            data = request.data
            post.headline = data.get('headline')
            post.content = data.get('content')
            # tags field will be included after issue 23 is resolved
            # post.tags = data.get('tags')
            post.save()
            serializer = PostSerializer(post, many=False)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'detail':f'{e}'},status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_post(request,pk):
    try:
        post= Post.objects.get(id=pk)
        if post.user == request.user:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'detail':f'{e}'},status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def posts(request):
    query = request.query_params.get('q')
    if query == None:
        query = ''
    # Q objects is used to make complex query to search in post content and headline
    posts = Post.objects.filter(Q(content__contains=query)|Q(headline__contains=query)).order_by("-created")
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts,request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def like_post(request, post_id):
    user = request.user
    try:
        post_to_like = Post.objects.get(id=post_id)
        if user == post_to_like.author: 
            return Response('You can not like your post')
        if user in post_to_like.likes.all():
            post_to_like.likes.remove(user)
            post_to_like.save()
            return Response('Post unlike')
        else:
            post_to_like.likes.add(user)
            post_to_like.save()
            return Response('Post liked')
    except Exception as e:
        message = {'detail':f'{e}'}
        return Response(message,status=status.HTTP_204_NO_CONTENT)

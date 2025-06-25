from django.urls import path, include
from lobbys import views


urlpatterns = [
    path('<int:pk>/comments', views.CommentsList),
    # for reply you have to put id of cooment in body
    path('<int:pk>/create', views.CommentCreate),
    path('<int:pk>/delete', views.CommentDelete),
    path('comments/like/<int:pk>', views.CommentLike),
    path('send_join_request/<int:pk>', views.SendRequestToJoin),
]
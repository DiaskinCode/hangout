from django.urls import path

from friend.views import(
	send_friend_request,
	accept_friend_request,
	cancel_friend_request,
	# friend_requests,
	# remove_friend,
	# decline_friend_request,
	# friends_list_view,
)

app_name = 'friend'

urlpatterns = [
    path('send_friend_request/<str:username>', send_friend_request, name='friend-request'),
    path('friend_request_accept/<str:friend_request_user>', accept_friend_request, name='friend-request-accept'),
    path('friend_request_cancel/<str:receiver_username>', cancel_friend_request, name='friend-request-cancel'),
	# path('list/<user_id>', friends_list_view, name='list'),
	# path('friend_remove/', remove_friend, name='remove-friend'),
    # path('friend_requests/<user_id>/', friend_requests, name='friend-requests'),
    # path('friend_request_decline/<friend_request_id>/', decline_friend_request, name='friend-request-decline'),
]
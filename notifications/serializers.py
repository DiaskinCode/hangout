from rest_framework import serializers
from users.serializers import UserProfileSerializer
from .models import Notification

class NotificationSerializer(serializers.Serializer):
    
    notification_type = serializers.IntegerField(read_only=True)
    to_user = serializers.StringRelatedField(read_only=True)
    from_user = serializers.SerializerMethodField(read_only=True)
    post = serializers.StringRelatedField(many = False)
    comment = serializers.StringRelatedField(read_only=True)
    date = serializers.DateTimeField()
    content= serializers.CharField(max_length=1000)
    user_has_seen = serializers.BooleanField()
    
    def get_from_user(self, obj):
        from_user = obj.from_user.userprofile
        serializer = UserProfileSerializer(from_user, many=False)
        return serializer.data
    
    class Meta:
        model = Notification
        fields = '__all__'
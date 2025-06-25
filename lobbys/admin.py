from django.contrib import admin

# Register your models here.

from .models import Lobby,JoinRequest

class LobbyAdmin(admin.ModelAdmin):
    list_filter = ['post']
    list_display = ['post']
    search_fields = ['post']
    readonly_friends = ['post']

    class Meta:
        model = Lobby

admin.site.register(Lobby, LobbyAdmin)

class JoinRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender','receiver']
    list_display = ['sender','receiver']
    search_fields = ['sender__username','receiver__username']

    class Meta:
        model = JoinRequest

admin.site.register(JoinRequest, JoinRequestAdmin)

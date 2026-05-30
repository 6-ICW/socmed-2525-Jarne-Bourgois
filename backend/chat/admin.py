from django.contrib import admin
from .models import Server, ServerMember, Channel, Message, Invite, UserProfile, Friendship

admin.site.register(Server)
admin.site.register(ServerMember)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(Invite)
admin.site.register(UserProfile)
admin.site.register(Friendship)

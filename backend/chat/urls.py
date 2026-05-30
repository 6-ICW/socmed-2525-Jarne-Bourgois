from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'servers', views.ServerViewSet, basename='server')

urlpatterns = [
    path('', include(router.urls)),

    # Auth
    path('auth/register/', views.register),
    path('auth/login/', views.login),
    path('auth/logout/', views.logout),
    path('auth/me/', views.me),
    path('auth/heartbeat/', views.heartbeat),

    # Users
    path('users/search/', views.search_users),

    # Server members & roles
    path('servers/<int:server_id>/members/', views.server_members),
    path('servers/<int:server_id>/members/<int:user_id>/toggle-admin/', views.toggle_admin),
    path('servers/<int:server_id>/members/<int:user_id>/kick/', views.kick_member),

    # Channels
    path('servers/<int:server_id>/channels/', views.channel_list),
    path('servers/<int:server_id>/channels/<int:channel_id>/', views.channel_detail),

    # Messages
    path('channels/<int:channel_id>/messages/', views.message_list),
    path('messages/<int:message_id>/', views.message_detail),

    # Invites
    path('servers/<int:server_id>/invite/', views.create_invite),
    path('invites/', views.pending_invites),
    path('invites/<uuid:code>/accept/', views.accept_invite),

    # DMs
    path('dm/create/', views.create_dm),

    # Friends
    path('friends/', views.friends_list),
    path('friends/requests/', views.pending_friend_requests),
    path('friends/add/', views.send_friend_request),
    path('friends/<int:friendship_id>/accept/', views.accept_friend_request),
    path('friends/<int:friendship_id>/remove/', views.remove_friend),
]
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Server, ServerMember, Channel, Message, Invite, UserProfile, Friendship
from .serializers import (
    UserSerializer, RegisterSerializer, ServerSerializer, ServerMemberSerializer,
    ChannelSerializer, MessageSerializer, InviteSerializer, FriendshipSerializer
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def touch_user(user):
    profile = get_or_create_profile(user)
    profile.last_seen = timezone.now()
    profile.save(update_fields=['last_seen'])


# ── Auth ──────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    password = request.data.get('password')
    if len(password) < 8 or password.lower() == password or password.upper() == password or password.alpha() == True :
        return Response({'error': 'Ongeldige passwoord'}, status=400)
    print(password)
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        get_or_create_profile(user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        get_or_create_profile(user)
        touch_user(user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})
    return Response({'error': 'Ongeldige inloggegevens'}, status=400)


@api_view(['POST'])
def logout(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Uitgelogd'})


@api_view(['GET'])
def me(request):
    touch_user(request.user)
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
def heartbeat(request):
    """Called periodically by frontend to keep online status fresh."""
    touch_user(request.user)
    return Response({'ok': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return Response([])

    # Methode 1: naam begint met query
    starts_with = User.objects.filter(
        username__istartswith=query
    ).exclude(
        id=request.user.id
    )

    # Methode 2: naam bevat query
    contains = User.objects.filter(
        username__icontains=query
    ).exclude(
        id=request.user.id
    )

    # Combineer zonder dubbels
    users = (starts_with | contains).distinct()[:10]

    results = [
        {
            'id': user.id,
            'username': user.username
        }
        for user in users
    ]

    return Response(results)


# ── Servers ───────────────────────────────────────────────────────────────────

class ServerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ServerSerializer

    def get_queryset(self):
        return Server.objects.filter(
            servermembers__user=self.request.user
        ).prefetch_related('channels', 'servermembers__user')

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'Naam vereist'}, status=400)
        server = Server.objects.create(name=name, owner=request.user)
        ServerMember.objects.create(server=server, user=request.user, role='owner')
        Channel.objects.create(server=server, name='general', channel_type='text')
        serializer = ServerSerializer(server, context={'request': request})
        return Response(serializer.data, status=201)

    def partial_update(self, request, pk=None):
        """PATCH /servers/{id}/ — update name and/or icon. Owner or admin only."""
        try:
            server = Server.objects.get(pk=pk)
        except Server.DoesNotExist:
            return Response({'error': 'Niet gevonden'}, status=404)
        if not server.is_admin_or_owner(request.user):
            return Response({'error': 'Geen rechten'}, status=403)

        name = request.data.get('name', '').strip()
        if name:
            server.name = name

        icon = request.FILES.get('icon')
        if icon:
            # Delete old icon file
            if server.icon:
                try:
                    import os
                    os.remove(server.icon.path)
                except Exception:
                    pass
            server.icon = icon

        server.save()
        serializer = ServerSerializer(server, context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            server = Server.objects.get(pk=pk, owner=request.user)
        except Server.DoesNotExist:
            return Response({'error': 'Niet gevonden of geen eigenaar'}, status=404)
        server.delete()
        return Response(status=204)


# ── Server Members & Roles ────────────────────────────────────────────────────

@api_view(['GET'])
def server_members(request, server_id):
    try:
        server = Server.objects.get(pk=server_id)
        if not ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'error': 'Geen toegang'}, status=403)
    except Server.DoesNotExist:
        return Response({'error': 'Server niet gevonden'}, status=404)

    members = ServerMember.objects.filter(server=server).select_related('user__profile').order_by(
        # owner first, then admins, then members
        'role', 'joined_at'
    )
    # Custom ordering: owner > admin > member
    order = {'owner': 0, 'admin': 1, 'member': 2}
    members_list = sorted(list(members), key=lambda m: (order.get(m.role, 3), m.joined_at))
    return Response(ServerMemberSerializer(members_list, many=True).data)


@api_view(['PATCH'])
def toggle_admin(request, server_id, user_id):
    """Toggle admin role for a member. Only admins/owners can do this. Owner role is protected."""
    try:
        server = Server.objects.get(pk=server_id)
    except Server.DoesNotExist:
        return Response({'error': 'Server niet gevonden'}, status=404)

    if not server.is_admin_or_owner(request.user):
        return Response({'error': 'Geen rechten'}, status=403)

    try:
        target_member = ServerMember.objects.get(server=server, user_id=user_id)
    except ServerMember.DoesNotExist:
        return Response({'error': 'Lid niet gevonden'}, status=404)

    # Owner cannot be demoted
    if target_member.role == 'owner':
        return Response({'error': 'De eigenaar kan niet worden gedegradeerd'}, status=400)

    # Toggle admin/member
    if target_member.role == 'admin':
        target_member.role = 'member'
    else:
        target_member.role = 'admin'
    target_member.save()
    return Response(ServerMemberSerializer(target_member).data)


@api_view(['DELETE'])
def kick_member(request, server_id, user_id):
    """Remove a member from the server. Owner or admin only, can't kick owner."""
    try:
        server = Server.objects.get(pk=server_id)
    except Server.DoesNotExist:
        return Response({'error': 'Server niet gevonden'}, status=404)

    if not server.is_admin_or_owner(request.user):
        return Response({'error': 'Geen rechten'}, status=403)

    try:
        target_member = ServerMember.objects.get(server=server, user_id=user_id)
    except ServerMember.DoesNotExist:
        return Response({'error': 'Lid niet gevonden'}, status=404)

    if target_member.role == 'owner':
        return Response({'error': 'De eigenaar kan niet worden verwijderd'}, status=400)

    target_member.delete()
    return Response(status=204)


# ── Channels ──────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def channel_list(request, server_id):
    try:
        server = Server.objects.get(pk=server_id)
        if not ServerMember.objects.filter(server=server, user=request.user).exists():
            return Response({'error': 'Geen toegang'}, status=403)
    except Server.DoesNotExist:
        return Response({'error': 'Server niet gevonden'}, status=404)

    if request.method == 'GET':
        channels = server.channels.all().order_by('created_at')
        return Response(ChannelSerializer(channels, many=True).data)

    name = request.data.get('name', '').strip()
    channel_type = request.data.get('channel_type', 'text')
    if not name:
        return Response({'error': 'Naam vereist'}, status=400)
    if not server.is_admin_or_owner(request.user):
        return Response({'error': 'Alleen admins kunnen kanalen aanmaken'}, status=403)
    channel = Channel.objects.create(server=server, name=name, channel_type=channel_type)
    return Response(ChannelSerializer(channel).data, status=201)


@api_view(['DELETE'])
def channel_detail(request, server_id, channel_id):
    try:
        server = Server.objects.get(pk=server_id)
        channel = server.channels.get(pk=channel_id)
    except (Server.DoesNotExist, Channel.DoesNotExist):
        return Response({'error': 'Niet gevonden'}, status=404)
    if not server.is_admin_or_owner(request.user):
        return Response({'error': 'Alleen admins kunnen kanalen verwijderen'}, status=403)
    channel.delete()
    return Response(status=204)


# ── Messages ──────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def message_list(request, channel_id):
    try:
        channel = Channel.objects.get(pk=channel_id)
        if not ServerMember.objects.filter(server=channel.server, user=request.user).exists():
            return Response({'error': 'Geen toegang'}, status=403)
    except Channel.DoesNotExist:
        return Response({'error': 'Kanaal niet gevonden'}, status=404)

    if request.method == 'GET':
        messages = channel.messages.select_related('author').order_by('created_at')
        return Response(MessageSerializer(messages, many=True).data)

    content = request.data.get('content', '').strip()
    if not content:
        return Response({'error': 'Inhoud vereist'}, status=400)
    msg = Message.objects.create(channel=channel, author=request.user, content=content)
    return Response(MessageSerializer(msg).data, status=201)


@api_view(['PUT', 'DELETE'])
def message_detail(request, message_id):
    try:
        msg = Message.objects.select_related('channel__server').get(pk=message_id)
    except Message.DoesNotExist:
        return Response({'error': 'Bericht niet gevonden'}, status=404)

    server = msg.channel.server
    is_admin = server.is_admin_or_owner(request.user)
    is_author = msg.author == request.user

    if request.method == 'DELETE':
        if not is_author and not is_admin:
            return Response({'error': 'Geen rechten om dit bericht te verwijderen'}, status=403)
        msg.is_deleted = True
        msg.deleted_at = timezone.now()
        msg.save()
        return Response(status=204)

    # PUT — only author can edit
    if not is_author:
        return Response({'error': 'Je kunt alleen je eigen berichten bewerken'}, status=403)
    content = request.data.get('content', '').strip()
    if not content:
        return Response({'error': 'Inhoud vereist'}, status=400)
    msg.content = content
    msg.is_edited = True
    msg.save()
    return Response(MessageSerializer(msg).data)


@api_view(['POST'])
def restore_message(request, message_id):
    try:
        msg = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return Response(status=404)

    if msg.author != request.user:
        return Response(status=403)

    msg.is_deleted = False
    msg.deleted_at = None
    msg.save()

    return Response(MessageSerializer(msg).data)


# ── Invites ───────────────────────────────────────────────────────────────────

@api_view(['POST'])
def create_invite(request, server_id):
    try:
        server = Server.objects.get(pk=server_id)
    except Server.DoesNotExist:
        return Response({'error': 'Server niet gevonden'}, status=404)

    if not server.is_admin_or_owner(request.user):
        return Response({'error': 'Alleen admins kunnen uitnodigen'}, status=403)

    username = request.data.get('username', '').strip()
    invited_user = None
    if username:
        try:
            invited_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': f'Gebruiker "{username}" niet gevonden'}, status=404)
        if ServerMember.objects.filter(server=server, user=invited_user).exists():
            return Response({'error': 'Gebruiker is al lid'}, status=400)

    invite = Invite.objects.create(
        server=server,
        created_by=request.user,
        invited_user=invited_user,
    )
    return Response(InviteSerializer(invite).data, status=201)


@api_view(['GET'])
def pending_invites(request):
    invites = Invite.objects.filter(
        invited_user=request.user,
        is_used=False
    ).select_related('server', 'created_by')
    return Response(InviteSerializer(invites, many=True).data)


@api_view(['POST'])
def accept_invite(request, code):
    try:
        invite = Invite.objects.get(code=code, is_used=False)
    except Invite.DoesNotExist:
        return Response({'error': 'Ongeldige of al gebruikte invite'}, status=404)

    if invite.invited_user and invite.invited_user != request.user:
        return Response({'error': 'Deze invite is niet voor jou'}, status=403)

    if not ServerMember.objects.filter(server=invite.server, user=request.user).exists():
        ServerMember.objects.create(server=invite.server, user=request.user, role='member')
    invite.is_used = True
    invite.save()
    serializer = ServerSerializer(invite.server, context={'request': request})
    return Response(serializer.data)


# ── DMs ───────────────────────────────────────────────────────────────────────

@api_view(['POST'])
def create_dm(request):
    username = request.data.get('username', '').strip()
    try:
        other_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': f'Gebruiker "{username}" niet gevonden'}, status=404)

    if other_user == request.user:
        return Response({'error': 'Je kunt geen DM met jezelf starten'}, status=400)

    # Check if a private server already exists
    existing = Server.objects.filter(
        is_private=True,
        servermembers__user=request.user
    ).filter(servermembers__user=other_user)
    if existing.exists():
        return Response(ServerSerializer(existing.first(), context={'request': request}).data)

    dm_name = f'{request.user.username} & {other_user.username}'
    server = Server.objects.create(name=dm_name, owner=request.user, is_private=True)
    ServerMember.objects.create(server=server, user=request.user, role='owner')
    ServerMember.objects.create(server=server, user=other_user, role='member')
    Channel.objects.create(server=server, name='direct-message', channel_type='text')
    return Response(ServerSerializer(server, context={'request': request}).data, status=201)


# ── Friends ───────────────────────────────────────────────────────────────────

@api_view(['GET'])
def friends_list(request):
    """Return all accepted friends with online status."""
    friendships = Friendship.objects.filter(
        status='accepted'
    ).filter(
        from_user=request.user
    ) | Friendship.objects.filter(
        status='accepted'
    ).filter(
        to_user=request.user
    )

    friends = []
    for f in friendships.select_related('from_user__profile', 'to_user__profile').distinct():
        friend_user = f.to_user if f.from_user == request.user else f.from_user
        friends.append({
            'friendship_id': f.id,
            'user': UserSerializer(friend_user).data,
        })
    return Response(friends)


@api_view(['GET'])
def pending_friend_requests(request):
    """Received pending friend requests."""
    requests_qs = Friendship.objects.filter(
        to_user=request.user, status='pending'
    ).select_related('from_user__profile')
    return Response(FriendshipSerializer(requests_qs, many=True).data)


@api_view(['POST'])
def send_friend_request(request):
    username = request.data.get('username', '').strip()
    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': f'Gebruiker "{username}" niet gevonden'}, status=404)

    if target == request.user:
        return Response({'error': 'Je kunt geen vriendschap met jezelf sturen'}, status=400)

    # Check existing
    existing = Friendship.objects.filter(
        from_user=request.user, to_user=target
    ) | Friendship.objects.filter(
        from_user=target, to_user=request.user
    )
    if existing.exists():
        f = existing.first()
        if f.status == 'accepted':
            return Response({'error': 'Al vrienden'}, status=400)
        return Response({'error': 'Vriendschapsverzoek al verstuurd of ontvangen'}, status=400)

    friendship = Friendship.objects.create(from_user=request.user, to_user=target, status='pending')
    return Response(FriendshipSerializer(friendship).data, status=201)


@api_view(['POST'])
def accept_friend_request(request, friendship_id):
    try:
        friendship = Friendship.objects.get(pk=friendship_id, to_user=request.user, status='pending')
    except Friendship.DoesNotExist:
        return Response({'error': 'Verzoek niet gevonden'}, status=404)
    friendship.status = 'accepted'
    friendship.save()
    return Response(FriendshipSerializer(friendship).data)


@api_view(['DELETE'])
def remove_friend(request, friendship_id):
    try:
        friendship = Friendship.objects.get(
            pk=friendship_id
        )
        if friendship.from_user != request.user and friendship.to_user != request.user:
            return Response({'error': 'Geen rechten'}, status=403)
    except Friendship.DoesNotExist:
        return Response({'error': 'Niet gevonden'}, status=404)
    friendship.delete()
    return Response(status=204)
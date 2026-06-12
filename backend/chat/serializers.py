from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from .models import Server, ServerMember, Channel, Message, Invite, UserProfile, Friendship


class UserSerializer(serializers.ModelSerializer):
    initials = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'initials', 'is_online']

    def get_initials(self, obj):
        parts = obj.username.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return obj.username[:2].upper()

    def get_is_online(self, obj):
        try:
            return obj.profile.is_online()
        except Exception:
            return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=3)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        UserProfile.objects.get_or_create(user=user)
        return user


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'name', 'channel_type', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
    'id',
    'content',
    'author',
    'created_at',
    'updated_at',
    'is_edited',
    'is_deleted',
    'deleted_at',
]


class ServerMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ServerMember
        fields = ['id', 'user', 'role', 'joined_at']


class ServerSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    channels = ChannelSerializer(many=True, read_only=True)
    current_user_role = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ['id', 'name', 'owner', 'is_private', 'member_count', 'is_member',
                  'channels', 'current_user_role', 'icon_url', 'created_at']

    def get_member_count(self, obj):
        return ServerMember.objects.filter(server=obj).count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ServerMember.objects.filter(server=obj, user=request.user).exists()
        return False

    def get_current_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return ServerMember.objects.get(server=obj, user=request.user).role
            except ServerMember.DoesNotExist:
                return None
        return None

    def get_icon_url(self, obj):
        request = self.context.get('request')
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        elif obj.icon:
            return f"{settings.MEDIA_URL}{obj.icon}"
        return None


class InviteSerializer(serializers.ModelSerializer):
    server = ServerSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    invited_user = UserSerializer(read_only=True)

    class Meta:
        model = Invite
        fields = ['id', 'code', 'server', 'created_by', 'invited_user', 'is_used', 'created_at']


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
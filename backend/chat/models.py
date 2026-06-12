from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os


def server_icon_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'server_icons/{instance.id}.{ext}'


class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_servers')
    is_private = models.BooleanField(default=False)
    icon = models.ImageField(upload_to=server_icon_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def members(self):
        """Return queryset of users who are members."""
        return User.objects.filter(servermember__server=self)

    def get_member_role(self, user):
        try:
            return ServerMember.objects.get(server=self, user=user).role
        except ServerMember.DoesNotExist:
            return None

    def is_admin_or_owner(self, user):
        role = self.get_member_role(user)
        return role in ('owner', 'admin')


class ServerMember(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    )
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='servermembers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='servermembers')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('server', 'user')

    def __str__(self):
        return f'{self.user.username} in {self.server.name} ({self.role})'


class Channel(models.Model):
    CHANNEL_TYPES = (
        ('text', 'Text'),
        ('voice', 'Voice'),
    )
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='channels')
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=10, choices=CHANNEL_TYPES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} / {self.name}'


class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:40]}'


class Invite(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='invites')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invites')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites', null=True, blank=True)
    code = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invite to {self.server.name} by {self.created_by.username}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_seen = models.DateTimeField(default=timezone.now)

    def is_online(self):
        delta = timezone.now() - self.last_seen
        return delta.total_seconds() < 180  # 3 minutes

    def __str__(self):
        return f'Profile of {self.user.username}'


class Friendship(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    )
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friendships')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friendships')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user.username} -> {self.to_user.username} ({self.status})'
from django.db import models
from django.contrib.auth.models import User
# from post.models import Post

class BaseNotification(models.Model):
    """Abstract base class for all notifications."""
    NOTIFICATION_TYPES = ((1, 'Like'), (2, 'Comment'), (3, 'Follow'),(4,'Message'))

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_from_user"  # Unique related_name for each subclass
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_to_user"  # Unique related_name for each subclass
    )
    notification_types = models.IntegerField(choices=NOTIFICATION_TYPES, null=True, blank=True)
    text_preview = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        abstract = True

class MsgNoti(BaseNotification):
    msg = models.ForeignKey(
        "directs.Message",
        on_delete=models.CASCADE,
        related_name="direct_notifications",
        null=True,  # Allow NULL
        blank=True,  # Allow blank values in forms
        default=None)
    class Meta:
        verbose_name = "Direct Notification"
        verbose_name_plural = "Direct Notifications"

class Notification(BaseNotification):
    """Notification for posts."""
    post = models.ForeignKey(
        "post.Post",
        on_delete=models.CASCADE,
        related_name="post_notifications",
        null=True,  # Allow NULL
        blank=True,  # Allow blank values in forms
        default=None
    )
    class Meta:
        verbose_name = "Post Notification"
        verbose_name_plural = "Post Notifications"


class ReelNotification(BaseNotification):
    """Notification for reels."""
    post = models.ForeignKey(
        "reels.ReelModel",
        on_delete=models.CASCADE,
        related_name="reel_notifications",  # Unique related_name for ReelNotification
        default=None
    )

    class Meta:
        verbose_name = "Reel Notification"
        verbose_name_plural = "Reel Notifications"

from django.db.models.signals import post_save, post_delete
from notification.models import ReelNotification
from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import FileExtensionValidator
import uuid
from notification.models import Notification
from authy.models import Profile
# Create your models here.
def user_directory_path(instance, filename):
    return 'reels/user_{0}/{1}'.format(instance.user.id, filename)

def user_cover_directory_path(instance, filename):
    return 'reelCovers/user_{0}/{1}'.format(instance.user.id, filename)

class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True, default=uuid.uuid1)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

class ReelModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reel_user')
    reel_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    reel_video = models.FileField(upload_to=user_directory_path, verbose_name="Reel", validators= [FileExtensionValidator(allowed_extensions=['mp4','MOV'])])
    #reel_cover = models.FileField(upload_to=user_cover_directory_path, verbose_name="Cover", validators= [FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])
    reel_cover = models.ImageField(upload_to=user_directory_path, verbose_name="Cover")
    
    reel_description = models.TextField(blank=True, null=True)
    reel_tags = models.ManyToManyField(Tag, related_name="tags")

    reel_likes = models.IntegerField(default=0)
    reel_upload_date = models.DateField(auto_now_add=True)

    is_close = models.BooleanField(default=False, name= "is_close")
    
    def get_absolute_url(self):
        return reverse("reel-view", args=[str(self.reel_id)])



class ReelComment(models.Model):
    post = models.ForeignKey(ReelModel, on_delete=models.CASCADE, related_name="comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)

    # def __str__(self):
    #     return self.post
    
    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.body[0:90]
        sender = comment.user
        notify = ReelNotification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_types=2)
        notify.save()

    def user_del_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.user
        notify = ReelNotification.objects.filter(post=post, sender=sender, user=post.user, notification_types=2)
        notify.delete()

class ReelLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reel = models.ForeignKey(ReelModel, on_delete=models.CASCADE, related_name="post_likes")

    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        reel = like.reel
        sender = like.user
        notify = ReelNotification(post=reel, sender=sender, user=reel.user)
        notify.save()

    def user_unliked_post(sender, instance, *args, **kwargs):
        like = instance
        reel = like.reel
        sender = like.user
        notify = ReelNotification.objects.filter(post=reel, sender=sender, notification_types=1)
        notify.delete()

post_save.connect(ReelComment.user_comment_post, sender=ReelComment)
post_delete.connect(ReelComment.user_del_comment_post, sender=ReelComment)

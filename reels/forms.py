from django.contrib.auth.models import User
from .models import ReelComment, ReelModel
from django import forms
from django.core.validators import FileExtensionValidator

class NewCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Write comment'}), required=True)
    
    class Meta:
        model = ReelComment
        fields = ("body",)

class NewReelForm(forms.ModelForm):
    reel_video = forms.FileField(validators= [FileExtensionValidator(allowed_extensions=['mp4','MOV'])], required=True)
    reel_cover = forms.ImageField(required=True)
    reel_description = forms.CharField(required=False)
    is_close = forms.BooleanField(required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Seperate with comma'}), required=True)

    class Meta:
        model = ReelModel
        fields = ["reel_video", "reel_cover", "reel_description",  "is_close", "tags"]
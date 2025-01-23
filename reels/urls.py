from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from . import views

urlpatterns = [
    path('<uuid:reel_id>/', ReelDetails.as_view(), name="reel-view"),
    path('<uuid:reel_id>/delete', ReelDeleteView.as_view(), name="reel-del"),
    path('', ReelListView.as_view(), name='reel-list'),
    path('create/', ReelView.as_view(), name='reel-create'),
    path('<uuid:reel_id>/like/', like, name='like-reel'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
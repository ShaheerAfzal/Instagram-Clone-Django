from django.urls import path
from notification.views import *

urlpatterns = [
    path('', NotificationList.as_view(), name='show-notification'),
    path('<noti_id>/delete', DeleteNotification, name='delete-notification'),


]

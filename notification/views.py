import importlib
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from itertools import chain
from operator import attrgetter


# def ShowNotification(request):
#     user = request.user
#     notifications = Notification.objects.filter(user=user).order_by('-date')

#     context = {
#         'notifications': notifications,

#     }
#     return render(request, 'notifications/notification.html', context)

class NotificationList(LoginRequiredMixin, ListView):
    template_name = 'notifications/notification.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        user = self.request.user

        post_notifications = Notification.objects.filter(user=user).exclude(sender = user)

        reel_notifications = ReelNotification.objects.filter(user=user).exclude(sender = user)

        message_notifications = MsgNoti.objects.filter(user=user).exclude(sender=user)

        combined_notis = sorted(chain(post_notifications, reel_notifications, message_notifications),
                                key=attrgetter('date'),
                                reverse=True)
        return combined_notis

def DeleteNotification(request, noti_id):
    user = request.user
    # print(user)
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notification')

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from authy.views import *
from reels.views import userReels

urlpatterns = [
    # Profile Section
    path('<username>/', UserProfile, name='profile'),
    path('<username>/settings', prof_settings, name='profile-settings'),
    path('<username>/settings/password_change', password_change, name='password-change'),
    path('<username>/saved/', UserProfile, name='profilefavourite'),
    path('<username>/follow/<option>/', follow, name='follow'),
    path('<username>/followers/', followers_list, name='followers'),
    path('<username>/add-to-close/<follower_username>', add_to_close_friends, name='add-to-close'),
    path('<username>/following/', following_list, name='following'),
    path('<username>/Close-Friends/', close_friends, name='close-friends'),
    path('<username>/followers/remove/<follower_username>/', follower_remove, name='follower-remove'),
    path('<username>/following/remove/<following_username>/', following_remove, name='following-remove'),
    path('<username>/reels/', userReels.as_view(), name='profile-reels'),
    path('profile/edit', EditProfile, name="editprofile"),
    # path('profile/<str:username>/reels/', views.ReelsView.as_view(), name='profile-reels'),
    # User Authentication
    path('sign-up/', views.register, name="sign-up"),
    path('sign-in/', auth_views.LoginView.as_view(template_name="sign-in.html", redirect_authenticated_user=True), name='sign-in'),
    path('sign-out/', auth_views.LogoutView.as_view(template_name="sign-out.html"), name='sign-out'), 
]

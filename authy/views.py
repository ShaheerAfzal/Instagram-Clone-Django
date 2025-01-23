from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Follow, CloseFrens
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import *
from post.models import Post, Follow, Stream
from django.contrib.auth.models import User
from authy.models import Profile
from .forms import *
from django.urls import resolve
from comment.models import Comment
from django.contrib.auth.hashers import check_password

def UserProfile(request, username):
    Profile.objects.get_or_create(user=request.user)
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    posts = Post.objects.filter(user=user).order_by('-posted')

    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.favourite.all()
    
    # Profile Stats
    posts_count = Post.objects.filter(user=user).count()
    close= CloseFrens.objects.all()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()
    # count_comment = Comment.objects.filter(post=posts).count()
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    # pagination
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'profile':profile,
        'posts_count':posts_count,
        'following_count':following_count,
        'followers_count':followers_count,
        'posts_paginator':posts_paginator,
        'follow_status':follow_status,
        # 'count_comment':count_comment,
    }
    return render(request, 'profile.html', context)

def EditProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile', username=profile.user.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EditProfileForm(instance=request.user.profile)

    context = {
        'form':form,
    }
    return render(request, 'editprofile.html', context)


def close_friends(request, username):
    # Get the user whose profile is being viewed
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)  # Ensure the profile exists

    # Get all Follow objects where the current user is being followed
    followers = Follow.objects.filter(following=user)

    # Get CloseFrens objects where friendProf matches the followers queryset
    close = CloseFrens.objects.filter(friendProf__in=followers)

    context = {
        'profile_user': user,  # The user whose profile is being viewed
        'close_friends': close,  # List of CloseFrens related to the user's followers
        'is_owner': request.user == user,  # Check if the logged-in user owns the profile
    }

    return render(request, 'close_friends_list.html', context)



@login_required
def add_to_close_friends(request, username, follower_username):
    """
    Allows the logged-in user to add a follower to their Close Friends list.
    """
    # Get the currently logged-in user
    current_user = request.user
    profile_user = get_object_or_404(User, username=username)
    # Get the follower to be added to Close Friends
    target_user = get_object_or_404(User, username=follower_username)

    # Check if the target_user is following the current_user
    follow_instance = Follow.objects.filter(follower=target_user, following=current_user).first()
    if not follow_instance:
        messages.error(request, f"{target_user.username} must be following you to add them to Close Friends.")
        return redirect('profile', username=current_user.username)

    # Check if the follower is already in the Close Friends list
    close_friend_exists = CloseFrens.objects.filter(friendProf=follow_instance).exists()
    if close_friend_exists:
        messages.info(request, f"{target_user.username} is already in your Close Friends list.")
        return redirect('profile', username=current_user.username)

    # Add the follower to Close Friends
    CloseFrens.objects.create(friendProf=follow_instance)
    messages.success(request, f"{target_user.username} has been added to your Close Friends list.")

    # Redirect back to the profile or close friends page
    return redirect('followers', username=current_user.username)


@login_required
def prof_settings(request, username):
    user = request.user
    profile_user = get_object_or_404(User, username=username)

    if request.user != profile_user:
        return HttpResponseForbidden("You are not allowed to perform this action.")
    return render(request, "profile_settings.html")

@login_required
def password_change(request, username):
    user = request.user
    if user.username != username:
        return HttpResponseForbidden("You are not allowed to access this page.")

    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            confirm_new_password = form.cleaned_data['confirm_new_password']

            if not check_password(current_password, user.password):
                messages.error(request, "Current password is incorrect.")
                return render(request, "passChange.html", {'form': form})

            if new_password != confirm_new_password:
                messages.error(request, "New password and confirmation do not match.")
                return render(request, "passChange.html", {'form': form})

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been successfully updated.")
            return redirect('profile-settings', username=user.username)
    else:
        form = PasswordChangeForm()

    return render(request, "passChange.html", {'form': form})


@login_required
def following_remove(request, username, following_username):
    profile_user = get_object_or_404(User, username=username)

    # Ensure only the owner of the profile can remove followers
    if request.user != profile_user:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    # Get the follower by their username
    following = get_object_or_404(User, username=following_username)
    print(f"{following.username} deleted")
    
    # Remove the follow relationship
    Follow.objects.filter(follower=profile_user, following=following).delete()
    # Optional: Add a success message
    messages.success(request, f"{following.username} has been removed from your following.")
    
    # Redirect back to the followings list
    # return HttpResponseRedirect(reverse('following-list'))
    return redirect('following', username=username)


def follower_remove(request, username, follower_username):
    profile_user = get_object_or_404(User, username=username)

    # Ensure only the owner of the profile can remove followers
    if request.user != profile_user:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    # Get the follower by their username
    follower = get_object_or_404(User, username=follower_username)
    print(f"{follower.username} deleted")
    
    # Remove the follow relationship
    Follow.objects.filter(follower=follower, following=profile_user).delete()
    # Optional: Add a success message
    messages.success(request, f"{follower.username} has been removed from your followers.")
    
    # Redirect back to the followers list
    # return HttpResponseRedirect(reverse('follower-list'))
    return redirect('followers', username=username)

def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    followers = Follow.objects.filter(following=user).select_related('follower')
    close_friends = CloseFrens.objects.filter(friendProf__following=user).select_related('friendProf__follower')
    close_friend_usernames = {cf.friendProf.follower.username for cf in close_friends}

    context = {
        'profile_user': user,  # The user whose profile is being viewed
        'followers': followers,  # All users following the profile_user
        'close_friend_usernames': close_friend_usernames,  # Usernames in Close Friends
        'is_owner': request.user == user,  # Check if the logged-in user owns the profile
    }
    
    return render(request, 'followers_list.html', context)

def following_list(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    following = Follow.objects.filter(follower=user).select_related('following')

    context = {
        'profile_user': user,  # The user whose profile is being viewed
        'following': following,  # List of followers
        'is_owner': request.user == user,  # Check if the logged-in user is the profile owner
    }
    return render(request, 'following_list.html', context)

def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Validate the password
                password = form.cleaned_data.get('password1')
                validate_password(password)
                
                # Save the user
                new_user = form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Hurray! Your account was created successfully.')

                # Automatically log in the user
                new_user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                )
                if new_user:
                    login(request, new_user)
                return redirect('index')

            except ValidationError as e:
                # Capture specific password errors
                for error in e:
                    messages.error(request, error)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")


    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'sign-up.html', context)
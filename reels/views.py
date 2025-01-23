from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormMixin, DeleteView
from django.views import View
from django.core.paginator import Paginator
from django.urls import *
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from .forms import NewCommentForm, NewReelForm
from post.models import Follow  
from authy.models import Profile  
# Create your views here.

def index(request):
    return render(request, "videos/index.html")

# class ReelView(CreateView):
#     model= ReelModel
#     fields = ['reel_video', 'reel_cover', 'reel_description', 'reel_tags']
#     template_name = "reel_create_view.html"

#     def get_success_url(self):
#         return reverse("reel-details", kwargs = {"pk": self.object.pk})

class ReelView(LoginRequiredMixin, CreateView): 
    model = ReelModel
    form_class = NewReelForm  # Use the custom form
    template_name = "reel_create_view.html"

    def form_valid(self, form):
        # Set the current logged-in user to the reel instance
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the reel list page after successful form submission
        return reverse("reel-list")#, kwargs={"pk": self.object.pk})

class ReelDetails(FormMixin, DetailView):
    model = ReelModel
    template_name = "reel_view.html"
    context_object_name = "reel"
    form_class = NewCommentForm
    pk_url_kwarg = "reel_id"

    def get_success_url(self):
        """Redirect back to the reel detail view after form submission."""
        return reverse('reel-view', kwargs={'reel_id': self.object.reel_id})

    def get_context_data(self, **kwargs):
        """Add comments and the form to the context."""
        context = super().get_context_data(**kwargs)
        context['comments'] = ReelComment.objects.filter(post=self.object).order_by('-date')
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        """Handle form submission for new comments."""
        self.object = self.get_object()  # Retrieve the ReelModel instance
        form = self.get_form()

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object  # Link comment to the current reel
            comment.user = request.user  # Set the currently logged-in user as the author
            comment.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class ReelListView(ListView):
    model = ReelModel
    template_name = "reel_list.html"  # Template that will render the list
    context_object_name = "reels"  # Variable to reference in the template
    ordering = ['-reel_upload_date']  # Orders by newest reels first

class ReelDeleteView(LoginRequiredMixin, DeleteView):
    model = ReelModel
    template_name = "reel_confirm_delete.html"  # Template for the delete confirmation page
    success_url = reverse_lazy("reel-list")  # Redirect to the reel list page after deletion
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        reel_id = self.kwargs.get("reel_id")
        #obj = get_object_or_404(self.get_queryset(), id=reel_id)
        return get_object_or_404(queryset, reel_id=reel_id)

@login_required
def like(request, reel_id):
    user = request.user
    reel = ReelModel.objects.get(reel_id=reel_id)
    current_likes = reel.reel_likes
    liked = ReelLikes.objects.filter(user=user, reel=reel).count()

    if not liked:
        ReelLikes.objects.create(user=user, reel=reel)
        current_likes = current_likes + 1
    else:
        ReelLikes.objects.filter(user=user, reel=reel).delete()
        current_likes = current_likes - 1
        
    reel.reel_likes = current_likes
    reel.save()
    # return HttpResponseRedirect(reverse('post-details', args=[post_id]))
    return HttpResponseRedirect(reverse('reel-view', args=[reel_id]))


class userReels(View):


    def get(self, request, username):
        # Ensure the profile exists for the user
        Profile.objects.get_or_create(user=request.user)

        # Fetch the user whose profile is being viewed
        user = get_object_or_404(User, username=username)
        profile = Profile.objects.get(user=user)

        # Fetch the user's reels
        reels = ReelModel.objects.filter(user=user).order_by('-reel_upload_date')

        # Profile Stats
        posts_count = reels.count()  # Count reels since we are in the "Reels" view
        following_count = Follow.objects.filter(follower=user).count()
        followers_count = Follow.objects.filter(following=user).count()
        follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

        # Pagination
        paginator = Paginator(reels, 8)  # Show 8 reels per page
        page_number = request.GET.get('page')
        reels_paginator = paginator.get_page(page_number)

        # Context for the template
        context = {
            'reels': reels_paginator,
            'profile': profile,
            'posts_count': posts_count,
            'following_count': following_count,
            'followers_count': followers_count,
            'follow_status': follow_status,
        }
        return render(request, 'profile_reels.html', context)

# def share_reel(request, reel_id):
#     # Implement your sharing logic here (e.g., sharing on social media)
#     return redirect('reel-view', reel_id=reel_id)
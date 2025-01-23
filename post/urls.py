from django.urls import path
from post.views import *

urlpatterns = [
    path('', index, name='index'),
    path('create-R-or-P', create_view, name='create-new'),
    path('newpost', NewPost, name='newpost'),
    path('<uuid:post_id>', PostDetail, name='post-details'),
    path('<uuid:post_id>/delete', post_del, name='post-del'),
    path('tag/<slug:tag_slug>', Tags, name='tags'),
    path('<uuid:post_id>/like', like, name='like'),
    path('<uuid:post_id>/favourite', favourite, name='favourite'),

]

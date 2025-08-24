from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('authors/', views.authors_list_view, name='authors_list'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('author/<str:username>/', views.author_detail_view, name='author_detail'),
    path('author/<str:username>/follow/', views.toggle_follow_view, name='toggle_follow'),
    path('author/<str:username>/followers/', views.followers_view, name='followers'),
    path('author/<str:username>/following/', views.following_view, name='following'),
]


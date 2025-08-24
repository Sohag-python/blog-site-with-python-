from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.blog_create_view, name='blog_create'),
    path('my-blogs/', views.my_blogs_view, name='my_blogs'),
    path('my-favorites/', views.my_favorites_view, name='my_favorites'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('blog/<slug:slug>/edit/', views.blog_edit_view, name='blog_edit'),
    path('blog/<slug:slug>/delete/', views.blog_delete_view, name='blog_delete'),
    path('blog/<slug:slug>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('blog/<slug:slug>/rate/', views.submit_rating_view, name='submit_rating'),
    path('category/<slug:slug>/', views.category_detail_view, name='category_detail'),
    path('author/<str:username>/', views.author_blogs_view, name='author_blogs'),
]


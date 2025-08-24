from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from .models import AuthorProfile, Follow
from .forms import AuthorProfileForm
from blog.models import Blog

User = get_user_model()

def author_detail_view(request, username):
    author = get_object_or_404(User, username=username)
    
    # Get or create author profile
    profile, created = AuthorProfile.objects.get_or_create(user=author)
    
    # Get author's published blogs
    blogs = Blog.objects.filter(author=author, status='published').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if current user is following this author
    is_following = False
    if request.user.is_authenticated and request.user != author:
        is_following = Follow.objects.filter(follower=request.user, following=author).exists()
    
    # Get statistics
    total_blogs = blogs.count()
    total_views = profile.get_total_views()
    average_rating = profile.get_average_rating()
    followers_count = author.followers.count()
    following_count = author.following.count()
    
    context = {
        'author': author,
        'profile': profile,
        'page_obj': page_obj,
        'is_following': is_following,
        'total_blogs': total_blogs,
        'total_views': total_views,
        'average_rating': average_rating,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'profiles/author_detail.html', context)

@login_required
def edit_profile_view(request):
    # Get or create author profile
    profile, created = AuthorProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AuthorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profiles:author_detail', username=request.user.username)
    else:
        form = AuthorProfileForm(instance=profile)
    
    return render(request, 'profiles/edit_profile.html', {'form': form, 'profile': profile})

@login_required
def toggle_follow_view(request, username):
    author = get_object_or_404(User, username=username)
    
    if request.user == author:
        messages.error(request, "You cannot follow yourself.")
        return redirect('profiles:author_detail', username=username)
    
    follow, created = Follow.objects.get_or_create(follower=request.user, following=author)
    
    if created:
        message = f'You are now following {author.get_full_name() or author.username}!'
        is_following = True
    else:
        follow.delete()
        message = f'You have unfollowed {author.get_full_name() or author.username}.'
        is_following = False
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_following': is_following, 
            'message': message,
            'followers_count': author.followers.count()
        })
    
    messages.success(request, message)
    return redirect('profiles:author_detail', username=username)

@login_required
def followers_view(request, username):
    author = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=author).select_related('follower')
    
    paginator = Paginator(followers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'profiles/followers.html', {
        'author': author,
        'page_obj': page_obj,
        'title': 'Followers'
    })

@login_required
def following_view(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=author).select_related('following')
    
    paginator = Paginator(following, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'profiles/following.html', {
        'author': author,
        'page_obj': page_obj,
        'title': 'Following'
    })

def authors_list_view(request):
    # Get all authors (users with author or admin role)
    authors = User.objects.filter(role__in=['author', 'admin']).select_related('author_profile')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        authors = authors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(author_profile__bio__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'blogs':
        # Sort by number of published blogs
        authors = authors.annotate(
            blog_count=Count('blogs', filter=Q(blogs__status='published'))
        ).order_by('-blog_count')
    elif sort_by == 'followers':
        # Sort by number of followers
        authors = authors.annotate(
            followers_count=Count('followers')
        ).order_by('-followers_count')
    elif sort_by == 'rating':
        # Sort by average rating
        authors = authors.annotate(
            avg_rating=Avg('blogs__ratings__score')
        ).order_by('-avg_rating')
    else:  # name
        authors = authors.order_by('first_name', 'last_name')
    
    # Pagination
    paginator = Paginator(authors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'profiles/authors_list.html', context)

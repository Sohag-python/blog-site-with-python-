from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Blog, Category, Favorite, Rating
from .forms import BlogForm, CategoryForm, RatingForm, SearchForm

User = get_user_model()

def home_view(request):
    blogs = Blog.objects.filter(status='published').select_related('author', 'category')
    
    # Search functionality
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        author = search_form.cleaned_data.get('author')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if query:
            blogs = blogs.filter(
                Q(title__icontains=query) | 
                Q(body__icontains=query) | 
                Q(excerpt__icontains=query)
            )
        if category:
            blogs = blogs.filter(category=category)
        if author:
            blogs = blogs.filter(author=author)
        if date_from:
            blogs = blogs.filter(published_at__gte=date_from)
        if date_to:
            blogs = blogs.filter(published_at__lte=date_to)
    
    # Sorting
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'rating':
        blogs = blogs.annotate(avg_rating=Avg('ratings__score')).order_by('-avg_rating', '-published_at')
    elif sort_by == 'popular':
        blogs = blogs.order_by('-views_count', '-published_at')
    else:  # latest
        blogs = blogs.order_by('-published_at')
    
    # Pagination
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Featured blogs (top 3 by rating)
    featured_blogs = Blog.objects.filter(status='published').annotate(
        avg_rating=Avg('ratings__score')
    ).order_by('-avg_rating', '-views_count')[:3]
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'featured_blogs': featured_blogs,
        'sort_by': sort_by,
    }
    return render(request, 'blog/home.html', context)

def blog_detail_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    
    # Increment view count
    blog.views_count += 1
    blog.save(update_fields=['views_count'])
    
    # Check if user has favorited this blog
    is_favorited = False
    user_rating = None
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, blog=blog).exists()
        try:
            user_rating = Rating.objects.get(user=request.user, blog=blog)
        except Rating.DoesNotExist:
            pass
    
    # Get ratings and reviews
    ratings = blog.ratings.all().select_related('user')
    average_rating = blog.get_average_rating()
    rating_count = blog.get_rating_count()
    
    # Rating form
    rating_form = RatingForm()
    
    # Related blogs
    related_blogs = Blog.objects.filter(
        category=blog.category, 
        status='published'
    ).exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'is_favorited': is_favorited,
        'user_rating': user_rating,
        'ratings': ratings,
        'average_rating': average_rating,
        'rating_count': rating_count,
        'rating_form': rating_form,
        'related_blogs': related_blogs,
    }
    return render(request, 'blog/blog_detail.html', context)

@login_required
def blog_create_view(request):
    if not request.user.can_create_blog():
        messages.error(request, 'You do not have permission to create blogs.')
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Blog created successfully!')
            return redirect('blog:blog_detail', slug=blog.slug)
    else:
        form = BlogForm()
    
    return render(request, 'blog/blog_form.html', {'form': form, 'title': 'Create Blog'})

@login_required
def blog_edit_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    if blog.author != request.user and not request.user.can_moderate():
        messages.error(request, 'You do not have permission to edit this blog.')
        return redirect('blog:blog_detail', slug=blog.slug)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog updated successfully!')
            return redirect('blog:blog_detail', slug=blog.slug)
    else:
        form = BlogForm(instance=blog)
    
    return render(request, 'blog/blog_form.html', {'form': form, 'title': 'Edit Blog', 'blog': blog})

@login_required
def blog_delete_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    if blog.author != request.user and not request.user.can_moderate():
        messages.error(request, 'You do not have permission to delete this blog.')
        return redirect('blog:blog_detail', slug=blog.slug)
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully!')
        return redirect('blog:home')
    
    return render(request, 'blog/blog_confirm_delete.html', {'blog': blog})

@login_required
def toggle_favorite_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    favorite, created = Favorite.objects.get_or_create(user=request.user, blog=blog)
    
    if created:
        # Send email notification
        send_mail(
            'Blog Added to Favorites',
            f'You have added "{blog.title}" to your favorites.',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=True,
        )
        message = 'Blog added to favorites!'
        is_favorited = True
    else:
        favorite.delete()
        message = 'Blog removed from favorites!'
        is_favorited = False
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorited': is_favorited, 'message': message})
    
    messages.success(request, message)
    return redirect('blog:blog_detail', slug=blog.slug)

@login_required
def submit_rating_view(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status='published')
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                blog=blog,
                defaults={
                    'score': form.cleaned_data['score'],
                    'review': form.cleaned_data['review']
                }
            )
            if not created:
                rating.score = form.cleaned_data['score']
                rating.review = form.cleaned_data['review']
                rating.save()
                messages.success(request, 'Rating updated successfully!')
            else:
                messages.success(request, 'Rating submitted successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('blog:blog_detail', slug=blog.slug)

@login_required
def my_blogs_view(request):
    blogs = Blog.objects.filter(author=request.user).order_by('-created_at')
    
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/my_blogs.html', {'page_obj': page_obj})

@login_required
def my_favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('blog')
    
    paginator = Paginator(favorites, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/my_favorites.html', {'page_obj': page_obj})

def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    blogs = Blog.objects.filter(category=category, status='published').order_by('-published_at')
    
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'page_obj': page_obj
    })

def author_blogs_view(request, username):
    author = get_object_or_404(User, username=username)
    blogs = Blog.objects.filter(author=author, status='published').order_by('-published_at')
    
    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/author_blogs.html', {
        'author': author,
        'page_obj': page_obj
    })

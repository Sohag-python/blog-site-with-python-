from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    website = models.URLField(blank=True, help_text="Your personal website")
    twitter = models.CharField(max_length=100, blank=True, help_text="Twitter username (without @)")
    linkedin = models.URLField(blank=True, help_text="LinkedIn profile URL")
    github = models.CharField(max_length=100, blank=True, help_text="GitHub username")
    facebook = models.URLField(blank=True, help_text="Facebook profile URL")
    instagram = models.CharField(max_length=100, blank=True, help_text="Instagram username (without @)")
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Profile"
    
    def get_absolute_url(self):
        return reverse('profiles:author_detail', kwargs={'username': self.user.username})
    
    def get_social_links(self):
        """Return a list of social media links"""
        links = []
        if self.website:
            links.append(('Website', self.website, 'fas fa-globe'))
        if self.twitter:
            links.append(('Twitter', f'https://twitter.com/{self.twitter}', 'fab fa-twitter'))
        if self.linkedin:
            links.append(('LinkedIn', self.linkedin, 'fab fa-linkedin'))
        if self.github:
            links.append(('GitHub', f'https://github.com/{self.github}', 'fab fa-github'))
        if self.facebook:
            links.append(('Facebook', self.facebook, 'fab fa-facebook'))
        if self.instagram:
            links.append(('Instagram', f'https://instagram.com/{self.instagram}', 'fab fa-instagram'))
        return links
    
    def get_blog_count(self):
        return self.user.blogs.filter(status='published').count()
    
    def get_total_views(self):
        return sum(blog.views_count for blog in self.user.blogs.filter(status='published'))
    
    def get_average_rating(self):
        from blog.models import Rating
        ratings = Rating.objects.filter(blog__author=self.user)
        if ratings:
            return sum(rating.score for rating in ratings) / len(ratings)
        return 0

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

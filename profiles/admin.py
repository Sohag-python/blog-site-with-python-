from django.contrib import admin
from .models import AuthorProfile, Follow

@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'location')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'bio')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('bio', 'profile_picture', 'location', 'birth_date')
        }),
        ('Social Media', {
            'fields': ('website', 'twitter', 'linkedin', 'github', 'facebook', 'instagram'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'follower__email', 'following__username', 'following__email')
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('follower', 'following')

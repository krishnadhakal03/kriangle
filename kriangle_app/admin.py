from django.contrib import admin
from .models import (
    SEOJob, SEOResult, BlogCategory, Tag, 
    BlogPost, OldBlogPost, OffPageSEOAction, 
    Contact, SEOReport, APICredential, SEOTask
)

# Register your models here.

class SEOResultInline(admin.TabularInline):
    model = SEOResult
    extra = 0

class OffPageSEOActionInline(admin.TabularInline):
    model = OffPageSEOAction
    extra = 0

@admin.register(SEOJob)
class SEOJobAdmin(admin.ModelAdmin):
    list_display = ['url', 'created_at', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['url', 'keywords']
    inlines = [SEOResultInline, OffPageSEOActionInline]

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

class BlogPostTagsInline(admin.TabularInline):
    model = BlogPost.tags.through
    extra = 1
    verbose_name = "Tag"
    verbose_name_plural = "Tags"

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'published_at', 'created_at', 'view_count']
    list_filter = ['is_published', 'category', 'author', 'created_at']
    search_fields = ['title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'featured_image', 'summary', 'content')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Publication', {
            'fields': ('author', 'is_published', 'published_at'),
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    exclude = ('tags',)
    inlines = [BlogPostTagsInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(OldBlogPost)
class OldBlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'job', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['job', 'title', 'content', 'url', 'created_at']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'phone_number', 'address', 'message']

@admin.register(SEOReport)
class SEOReportAdmin(admin.ModelAdmin):
    list_display = ['url', 'created_at', 'is_premium']
    list_filter = ['is_premium', 'created_at']
    search_fields = ['url', 'keywords']
    readonly_fields = ['url', 'keywords', 'report_token', 'created_at', 'report_data']
    
    def has_add_permission(self, request):
        return False

# New admin classes for Off-Page SEO Automation

@admin.register(APICredential)
class APICredentialAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'is_active', 'created_at']
    list_filter = ['service', 'is_active', 'created_at']
    search_fields = ['user__username', 'service']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('API Details', {
            'fields': ('user', 'service', 'api_key', 'api_secret', 'is_active')
        }),
        ('Additional Credentials', {
            'fields': ('access_token', 'refresh_token'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(SEOTask)
class SEOTaskAdmin(admin.ModelAdmin):
    list_display = ['website_url', 'task_type', 'user', 'status', 'created_at']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['website_url', 'keywords', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    fieldsets = (
        ('Task Details', {
            'fields': ('user', 'task_type', 'website_url', 'keywords', 'status')
        }),
        ('Specific Parameters', {
            'fields': ('target_url', 'platform', 'topic', 'category'),
        }),
        ('Content', {
            'fields': ('generated_content', 'edited_content', 'submission_result'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',),
        }),
    )

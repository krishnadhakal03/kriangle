from django.db import models
from django.utils.text import slugify
from django.urls import reverse
# from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User

# Create your models here.
class SEOJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seo_jobs', null=True)
    url = models.URLField()
    website_url = models.URLField(default='', blank=True)  # Add this for compatibility
    keywords = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending', 
                             choices=[('pending', 'Pending'), 
                                     ('processing', 'Processing'), 
                                     ('completed', 'Completed'),
                                     ('failed', 'Failed'),
                                     ('PENDING', 'Pending')])
    
    def __str__(self):
        return f"{self.url} - {self.created_at.strftime('%Y-%m-%d')}"
        
    def save(self, *args, **kwargs):
        # Ensure compatibility between url and website_url fields
        if self.website_url and not self.url:
            self.url = self.website_url
        elif self.url and not self.website_url:
            self.website_url = self.url
        super().save(*args, **kwargs)

class SEOResult(models.Model):
    job = models.ForeignKey(SEOJob, on_delete=models.CASCADE, related_name='results')
    step = models.CharField(max_length=100)
    result_data = models.TextField()
    status = models.CharField(max_length=50, default='success',
                              choices=[('success', 'Success'), 
                                      ('failed', 'Failed'), 
                                      ('pending', 'Pending')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.job.url} - {self.step}"

# Blog Category Model
class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Blog Categories"

# Tag Model for Blog Posts
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# Enhanced Blog Post Model
class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name='posts', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    # Commenting out ImageField to avoid Pillow dependency
    # featured_image = models.ImageField(upload_to='blog/featured_images/', blank=True, null=True)
    featured_image = models.CharField(max_length=255, blank=True, null=True, help_text="Path to featured image")
    summary = models.TextField(help_text="Brief summary for previews and meta descriptions", blank=True, null=True)
    content = models.TextField()  # Changed from RichTextUploadingField to TextField
    
    # SEO fields
    meta_title = models.CharField(max_length=100, blank=True, help_text="Custom title for SEO (optional)")
    meta_description = models.TextField(blank=True, help_text="Custom meta description for SEO (optional)")
    
    # Date and author fields
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='blog_posts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Publication fields
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Stats
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set default meta title if not provided
        if not self.meta_title:
            self.meta_title = self.title
            
        # Set default meta description if not provided
        if not self.meta_description:
            self.meta_description = self.summary
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_post_detail', kwargs={'slug': self.slug or 'no-slug'})
    
    def __str__(self):
        return self.title

# Legacy BlogPost model for backward compatibility
class OldBlogPost(models.Model):
    job = models.ForeignKey(SEOJob, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class OffPageAction(models.Model):
    """Model for actions taken in off-page SEO campaigns"""
    job = models.ForeignKey(SEOJob, on_delete=models.CASCADE, related_name='offpage_actions')
    platform = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.platform} - {self.action_type} for {self.job.url}"

# Keep this for backwards compatibility
class OffPageSEOAction(OffPageAction):
    """Legacy model for backwards compatibility"""
    class Meta:
        proxy = True

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)  # Add phone number field
    address = models.TextField()  # Add address field
    message = models.TextField()

    def __str__(self):
        return self.name

# Model for the SEO Report feature
class SEOReport(models.Model):
    url = models.URLField()
    keywords = models.TextField(blank=True)
    report_token = models.CharField(max_length=64, unique=True)
    report_data = models.JSONField()
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"SEO Report for {self.url}"

# New models for Off-Page SEO Automation
class APICredential(models.Model):
    """Store API credentials for various services"""
    SERVICE_CHOICES = (
        ('huggingface', 'Hugging Face AI'),
        ('email', 'Email Service'),
        ('twitter', 'Twitter/X'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('directory', 'Directory Service'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.service}"
    
    class Meta:
        verbose_name = "API Credential"
        verbose_name_plural = "API Credentials"
        unique_together = ['user', 'service']

class SEOTask(models.Model):
    """Track SEO tasks and their status"""
    TYPE_CHOICES = (
        ('guest_post', 'Guest Post Outreach'),
        ('social_media', 'Social Media Post'),
        ('directory', 'Directory Submission'),
        ('forum', 'Forum Engagement'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('generating', 'Generating Content'),
        ('review', 'Ready for Review'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    website_url = models.URLField()
    keywords = models.CharField(max_length=255)
    
    # Task-specific fields
    target_url = models.URLField(blank=True, null=True)  # For guest posts, forum posts
    platform = models.CharField(max_length=50, blank=True, null=True)  # For social media
    topic = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # For directory submissions
    
    # Content and results
    generated_content = models.TextField(blank=True, null=True)
    edited_content = models.TextField(blank=True, null=True)
    submission_result = models.TextField(blank=True, null=True)
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.website_url} - {self.task_type} ({self.status})"
    
    class Meta:
        verbose_name = "SEO Task"
        verbose_name_plural = "SEO Tasks"
        ordering = ['-created_at']
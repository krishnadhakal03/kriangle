# Kriangle Site Setup Guide

## Issue Resolution

The site was not running due to missing dependencies and configuration issues. Here are the steps taken to resolve them:

### 1. Missing Dependencies

The site was using `ckeditor_uploader.fields.RichTextUploadingField` but django-ckeditor wasn't installed. Added the following to requirements.txt:

```
django-ckeditor==6.7.0
```

### 2. Static Files Configuration

The STATICFILES_DIRS setting was pointing to a directory that didn't exist. Updated settings.py to use the correct static directory:

```python
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "kriangle_app/static"),  # Use existing static files directory
]
```

### 3. Media Files Configuration

Added media files configuration for handling uploads:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 4. CKEditor Configuration

Added CKEditor settings:

```python
# CKEditor Settings
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_BROWSE_SHOW_DIRS = True
```

### 5. URL Configuration Updates

Updated the URLs to serve media files in development:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('kriangle_app.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 6. Models Update

Temporarily modified the `BlogPost` model to use `TextField` instead of `RichTextUploadingField` until the dependency issue is resolved.

## Running the Site Locally

Please follow these steps to get the site running:

1. Install all dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create a superuser (if needed):
   ```
   python manage.py createsuperuser
   ```

4. Run the development server:
   ```
   python manage.py runserver
   ```

5. Create blog categories and blog posts through the admin interface.

## Additional Notes

1. Once all dependencies are installed, you can revert the `BlogPost.content` field back to `RichTextUploadingField` for rich text editing.

2. The blog system is now fully dynamic, allowing you to:
   - Create categories and tags
   - Add blog posts with featured images
   - Edit content with a rich text editor (once CKEditor is installed)
   - View posts by category or tag
   - Track view counts on posts

3. Make sure to create directories for media if they don't exist:
   ```
   mkdir -p media/blog/featured_images
   mkdir -p media/uploads
   ``` 
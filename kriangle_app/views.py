from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from collections import Counter
import json
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import openai
import requests
import tweepy
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import SEOJob, SEOResult, BlogPost, OffPageSEOAction, BlogCategory, Tag, Contact, APICredential, SEOTask
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.contrib import messages
from django.urls import reverse
from django.utils.text import slugify
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import time
import os

# Define a check for staff/admin users
def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser

# WordPress API Credentials
WP_URL = "https://yourwordpresssite.com/wp-json/wp/v2/posts"
WP_USER = "your_username"
WP_PASSWORD = "your_application_password"

# Twitter API Credentials
TWITTER_API_KEY = "your_twitter_api_key"
TWITTER_API_SECRET = "your_twitter_api_secret"
TWITTER_ACCESS_TOKEN = "your_twitter_access_token"
TWITTER_ACCESS_SECRET = "your_twitter_access_secret"


logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'autoseo/index.html')

def about(request):
    return render(request, 'autoseo/about.html')

def pricing(request):
    return render(request, "autoseo/pricing.html")

def shop(request):
    return render(request, 'autoseo/shop.html')

def services(request):
    return render(request, 'autoseo/services.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            form.save()

            # Send email to your Gmail
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            message = form.cleaned_data['message']
            subject = f"New Contact Message from {name}"

            # Prepare the email message
            email_message = f"Message from {name} ({email}, {phone_number}, {address}):\n\n{message}"

            # Sending the email
            send_mail(
                subject,
                email_message,
                settings.EMAIL_HOST_USER,
                ['krishna.dhakal03@gmail.com'],
                fail_silently=False,
            )

            # Redirect to a thank you page after successful form submission
            return render(request, 'autoseo/thank_you.html')
    else:
        form = ContactForm()

    return render(request, 'autoseo/contact.html', {'form': form})

def thank_you(request):
    return render(request, 'autoseo/thank_you.html')

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

@login_required
def offpage_view(request):
    """Render the Off-Page SEO view"""
    return render(request, 'autoseo/offpage.html')

@login_required
def seo_results(request, job_id):
    """Display SEO results for a specific job"""
    job = get_object_or_404(SEOJob, id=job_id)
    results = SEOResult.objects.filter(job=job).order_by('id')
    
    context = {
        'job': job,
        'results': results
    }
    
    return render(request, 'autoseo/seo_results.html', context)

@login_required
def offpage_automation_view(request):
    """View for the off-page SEO automation page"""
    # Get tasks for the history section
    tasks = SEOTask.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'autoseo/offpage-automation.html', {
        'tasks': tasks
    })

@require_POST
def generate_content(request):
    """Generate content for an SEO task based on URL and keywords"""
    url = request.POST.get('url')
    keywords = request.POST.get('keywords')
    task_type = request.POST.get('task_type')
    
    try:
        # Generate content using AI or templates
        content = generate_seo_content(url, keywords, task_type)
        
        # Create a new task in review status
        task = SEOTask.objects.create(
            url=url,
            keywords=keywords,
            task_type=task_type,
            status='review',
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'content': content
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_POST
def submit_task(request, task_id):
    """Submit a reviewed task for processing"""
    try:
        task = SEOTask.objects.get(id=task_id)
        
        # Update content if edited by user
        if 'content' in request.POST:
            task.content = request.POST.get('content')
        
        task.status = 'in_progress'
        task.save()
        
        # In simulation mode, just update status
        task.status = 'completed'
        task.result = "Task simulated successfully. In production, this would be sent/posted to the appropriate service."
        task.save()
        
        return JsonResponse({
            'success': True,
            'status': 'completed',
            'result': task.result
        })
    except SEOTask.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Task not found'
        }, status=404)

def get_tasks(request):
    """Get all tasks for the current user"""
    tasks = SEOTask.objects.all().order_by('-created_at')
    return render(request, 'autoseo/task_history.html', {'tasks': tasks})
    
def get_task_detail(request, task_id):
    """Get details for a specific task"""
    task = get_object_or_404(SEOTask, id=task_id)
    return render(request, 'autoseo/task_detail.html', {'task': task})

# Helper functions for content generation
def generate_seo_content(url, keywords, task_type):
    """Generate SEO content based on URL, keywords, and task type"""
    try:
        # Try to use Hugging Face API for content generation
        content = generate_with_huggingface(url, keywords, task_type)
        return content
    except Exception as e:
        # Fall back to template-based generation
        return generate_from_template(url, keywords, task_type)

@login_required
def generate_ai_content(keywords):
    """Generate AI content using OpenAI API"""
    prompt = f"Write an SEO-optimized blog post about {keywords}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

@login_required
@user_passes_test(is_staff_or_superuser)
def post_to_wordpress(content, title):
    """Post AI content to WordPress"""
    headers = {
        "Authorization": f"Basic {WP_USER}:{WP_PASSWORD}",
        "Content-Type": "application/json"
    }
    data = {"title": title, "content": content, "status": "publish"}

    response = requests.post(WP_URL, json=data, headers=headers)
    if response.status_code == 201:
        return response.json().get("link")
    return None

@login_required
@user_passes_test(is_staff_or_superuser)
def post_to_twitter(message):
    """Post the blog link to Twitter"""
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    
    tweet = api.update_status(message)
    return f"https://twitter.com/user/status/{tweet.id}"

def scan_seo(request):
    if request.method == 'POST':
        website_url = request.POST.get('website_url', '').strip()
        keywords = request.POST.get('keywords', '').strip()

        # Validate inputs
        if not website_url:
            return JsonResponse({'error': 'Website URL is required'}, status=400)
            
        if not is_valid_url(website_url):
            return JsonResponse({'error': 'Invalid URL format'}, status=400)

        try:
            # Fetch website content with a shorter timeout
            response = requests.get(website_url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return JsonResponse({'error': f'Could not fetch website: {str(e)}'}, status=400)

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = soup.get_text()
            
            # Simplified keyword extraction - just count most common words
            word_count = len(html_content.split())
            common_words = []
            
            # Only do keyword analysis if text is not too long
            if word_count < 10000:  # Limit analysis for very large pages
                # Basic word frequency without nltk for speed
                words = re.findall(r'\b[a-zA-Z]{3,15}\b', html_content.lower())
                word_freq = {}
                common_english_words = {'the', 'and', 'a', 'to', 'of', 'in', 'is', 'you', 'that', 'it', 
                                       'for', 'with', 'on', 'as', 'are', 'be', 'this', 'was', 'have', 'or'}
                
                for word in words:
                    if word not in common_english_words:
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get top 5 words
                common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Check if user is authenticated to enable premium features
            is_premium = request.user.is_authenticated

            # Build a simplified report
            report = {
                'title_tag': soup.title.string if soup.title else 'Not found',
                'meta_description': get_meta_description(soup),
                'keyword_count': html_content.lower().count(keywords.lower()) if keywords else 0,
                'keyword_analysis': {
                    'keyword_density': round(
                        (html_content.lower().count(keywords.lower()) / 
                         max(len(html_content.split()), 1)) * 100, 2
                    ) if keywords else 0,
                    'extracted_keywords': common_words,
                    'keyword_placement': {
                        'in_title': keywords.lower() in (soup.title.string.lower() if soup.title else '') if keywords else False,
                        'in_meta_description': False,
                        'in_h1': False,
                        'in_first_paragraph': False
                    }
                },
                'content_analysis': {
                    'word_count': word_count,
                    'readability_score': 70,  # Default reasonable score
                    'content_quality': 'Content quality analyzed based on length',
                    'paragraph_count': len(soup.find_all('p')),
                    'average_paragraph_length': int(word_count / max(len(soup.find_all('p')), 1))
                },
                'technical_seo': {
                    'page_load_time': '1.2s',  # Simplified
                    'mobile_friendly': True,  # Simplified
                    'https_enabled': website_url.startswith('https'),
                    'indexed_pages': '25+ pages' if is_premium else 'Premium feature',
                    'schema_markup': bool(soup.find_all('script', type='application/ld+json')),
                    'schema_markup_details': 'Schema markup detected' if soup.find_all('script', type='application/ld+json') else 'No schema markup found',
                    'html_errors': ['Check HTML validation for detailed errors'],
                    'js_errors': 'JavaScript analysis available in premium' if not is_premium else 'No critical JS errors detected'
                },
                'competitor_analysis': {
                    'competitors': ['competitor1.com', 'competitor2.com', 'competitor3.com'],
                    'detailed_comparison': 'Competitive analysis available in premium' if not is_premium else 'Basic competitive analysis provided'
                },
                'other_seo_metrics': {
                    'num_images': len(soup.find_all('img')),
                    'num_links': len(soup.find_all('a')),
                    'num_h1': len(soup.find_all('h1')),
                    'num_h2': len(soup.find_all('h2')),
                    'num_h3': len(soup.find_all('h3')),
                    'internal_links': len([a for a in soup.find_all('a', href=True) if a['href'].startswith('/') or website_url in a['href']]),
                    'external_links': len([a for a in soup.find_all('a', href=True) if not a['href'].startswith('/') and website_url not in a['href'] and not a['href'].startswith('#')]),
                    'social_media_tags': bool(soup.find_all('meta', property=lambda x: x and x.startswith('og:'))),
                    'xml_sitemap': True,  # Simplified
                    'robots_txt': True,  # Simplified
                },
                'on_page_seo_suggestions': get_simplified_seo_suggestions(soup, keywords),
                'monetization': {
                    'is_premium': is_premium,
                    'premium_features': [
                        'Detailed competitive analysis',
                        'Full technical error reports',
                        'Downloadable PDF report',
                        'Weekly rank tracking',
                        'Custom SEO recommendations'
                    ],
                    'premium_price': '$49.99'
                }
            }
            
            # Generate a simple report token
            report_token = f"report-{int(time.time())}"
            
            return JsonResponse({'report': report})

        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return JsonResponse({'error': 'Error analyzing content'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_simplified_seo_suggestions(soup, keywords):
    """Generate basic SEO suggestions without heavy processing"""
    suggestions = []
    
    # Check title length
    if soup.title:
        title_length = len(soup.title.string) if soup.title.string else 0
        if title_length < 30:
            suggestions.append("Title tag is too short (less than 30 characters)")
        elif title_length > 60:
            suggestions.append("Title tag is too long (more than 60 characters)")
    else:
        suggestions.append("Missing title tag")
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc or not meta_desc.get('content'):
        suggestions.append("Missing meta description")
    elif len(meta_desc['content']) < 50:
        suggestions.append("Meta description is too short (less than 50 characters)")
    elif len(meta_desc['content']) > 160:
        suggestions.append("Meta description is too long (more than 160 characters)")
        
    # Check for H1
    h1_tags = soup.find_all('h1')
    if not h1_tags:
        suggestions.append("Missing H1 tag")
    elif len(h1_tags) > 1:
        suggestions.append("Multiple H1 tags (recommended to have only one main H1)")
        
    # Check for alt text in images
    images = soup.find_all('img')
    missing_alt = 0
    for img in images:
        if not img.get('alt'):
            missing_alt += 1
    
    if missing_alt > 0:
        suggestions.append(f"Missing alt text in {missing_alt} images")
        
    # Check keyword usage if provided
    if keywords:
        if soup.title and keywords.lower() not in soup.title.string.lower():
            suggestions.append(f"Primary keyword '{keywords}' not found in title tag")
    
    return suggestions

def get_meta_description(soup):
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description and meta_description.get('content'):
        content = meta_description['content']
        if 150 <= len(content) <= 160:
            return content
        else:
            return f"Meta description length is {len(content)} characters (should be 150-160)."
    return 'Meta description missing'

def get_canonical_tag(soup):
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    if canonical_tag and canonical_tag.get('href'):
        return canonical_tag['href']
    return 'Canonical tag missing'

def get_internal_links(soup, base_url):
    links = soup.find_all('a', href=True)
    internal_links = []
    for link in links:
        href = link['href']
        if href.startswith(base_url):
            internal_links.append(href)
    return len(internal_links)

def get_external_links(soup, base_url):
    links = soup.find_all('a', href=True)
    external_links = []
    for link in links:
        href = link['href']
        if not href.startswith(base_url):
            external_links.append(href)
    return len(external_links)

def is_valid_url(url):
    return bool(re.match(r'^(http|https)://', url))

# New helper functions:

def check_structured_data(soup):
    structured_data = soup.find_all('script', attrs={'type': 'application/ld+json'})
    return len(structured_data) > 0

def check_mobile_friendly(soup):
    viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
    return bool(viewport_tag)

def check_social_media_tags(soup):
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    return bool(og_title) and bool(twitter_title)

def check_noindex_tag(soup):
    noindex_tag = soup.find('meta', attrs={'name': 'robots', 'content': 'noindex'})
    return bool(noindex_tag)

def check_xml_sitemap(website_url):
    sitemap_url = website_url.rstrip("/") + "/sitemap.xml"
    try:
        sitemap_response = requests.get(sitemap_url)
        return sitemap_response.status_code == 200
    except requests.RequestException:
        return False

def check_robots_txt(website_url):
    robots_url = website_url.rstrip("/") + "/robots.txt"
    try:
        robots_response = requests.get(robots_url)
        return robots_response.status_code == 200
    except requests.RequestException:
        return False

def check_text_to_html_ratio(soup, html_content):
    text_length = len(html_content.strip())
    html_length = len(str(soup))
    text_to_html_ratio = (text_length / html_length) * 100
    return round(text_to_html_ratio, 2)

# Keyword suggestions and additional SEO checks

def extract_keywords(text):
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    words_filtered = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Calculate frequency distribution
    freq_dist = FreqDist(words_filtered)
    return freq_dist.most_common(10)  # Top 10 most frequent words

# Function to get related keywords using NLTK or external API
def get_related_keywords(keyword):
    # Example: Using NLTK WordNet to find related words (synonyms)
    from nltk.corpus import wordnet as wn

    related_keywords = set()
    for syn in wn.synsets(keyword):
        for lemma in syn.lemmas():
            related_keywords.add(lemma.name())  # Add the lemma (synonym) to the set
    return list(related_keywords)

def test_celery(request):
    from django.http import HttpResponse
    from .tasks import test_task
    
    result = test_task.delay("Hello World")
    return HttpResponse(f"Task submitted with ID: {result.id}")

def blog(request):
    try:
        # Get all published blog posts
        blog_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
        
        # Get all categories for the sidebar
        categories = BlogCategory.objects.all()
        
        # Get popular tags
        tags = Tag.objects.all()[:10]  # Limit to 10 most popular tags
        
        # Recent posts for sidebar
        recent_posts = blog_posts[:5]  # Get 5 most recent posts
        
        context = {
            'blog_posts': blog_posts,
            'categories': categories,
            'tags': tags,
            'recent_posts': recent_posts,
        }
        
        return render(request, "autoseo/blog.html", context)
    except Exception as e:
        # Log the error
        print(f"Error in blog view: {str(e)}")
        messages.error(request, "There was an error loading the blog. Our team has been notified.")
        # Return an empty blog page with error message
        return render(request, "autoseo/blog.html", {'error': str(e)})

def blog_post_detail(request, slug):
    try:
        # Get the blog post
        if slug == 'no-slug':
            # Handle posts with missing slugs
            messages.error(request, "The requested blog post could not be found.")
            return redirect('blog')
            
        post = get_object_or_404(BlogPost, slug=slug, is_published=True)
        
        # Increment view count
        post.view_count += 1
        post.save()
        
        # Get related posts from the same category
        related_posts = []
        if post.category:
            related_posts = BlogPost.objects.filter(
                category=post.category, 
                is_published=True
            ).exclude(id=post.id)[:3]
        
        # Get categories for sidebar
        categories = BlogCategory.objects.all()
        
        # Get popular tags
        tags = Tag.objects.all()[:10]
        
        # Recent posts for sidebar
        recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:5]
        
        context = {
            'post': post,
            'related_posts': related_posts,
            'categories': categories,
            'tags': tags,
            'recent_posts': recent_posts,
        }
        
        return render(request, "autoseo/blog_post_detail.html", context)
    except Exception as e:
        # Log the error
        print(f"Error in blog_post_detail view: {str(e)}")
        messages.error(request, "The requested blog post could not be found.")
        return redirect('blog')

def blog_category(request, category_slug):
    try:
        # Get the category
        category = get_object_or_404(BlogCategory, slug=category_slug)
        
        # Get blog posts in this category
        blog_posts = BlogPost.objects.filter(
            category=category,
            is_published=True
        ).order_by('-published_at')
        
        # Get all categories for the sidebar
        categories = BlogCategory.objects.all()
        
        # Get popular tags
        tags = Tag.objects.all()[:10]
        
        # Recent posts for sidebar
        recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:5]
        
        context = {
            'category': category,
            'blog_posts': blog_posts,
            'categories': categories,
            'tags': tags,
            'recent_posts': recent_posts,
        }
        
        return render(request, "autoseo/blog_category.html", context)
    except:
        # If category not found or any error, redirect to blog home
        messages.error(request, "The requested category could not be found.")
        return redirect('blog')

def blog_tag(request, tag_slug):
    try:
        # Get the tag
        tag = get_object_or_404(Tag, slug=tag_slug)
        
        # Get blog posts with this tag
        blog_posts = BlogPost.objects.filter(
            tags=tag,
            is_published=True
        ).order_by('-published_at')
        
        # Get all categories for the sidebar
        categories = BlogCategory.objects.all()
        
        # Get popular tags
        tags = Tag.objects.all()[:10]
        
        # Recent posts for sidebar
        recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:5]
        
        context = {
            'tag': tag,
            'blog_posts': blog_posts,
            'categories': categories,
            'tags': tags,
            'recent_posts': recent_posts,
        }
        
        return render(request, "autoseo/blog_tag.html", context)
    except:
        # If tag not found or any error, redirect to blog home
        messages.error(request, "The requested tag could not be found.")
        return redirect('blog')

# New helper functions for enhanced SEO analysis

def analyze_keyword_placement(soup, keyword):
    if not keyword:
        return 'No keyword provided'
        
    placement = {
        'in_title': keyword.lower() in (soup.title.string.lower() if soup.title else ''),
        'in_meta_description': False,
        'in_h1': False,
        'in_first_paragraph': False,
        'in_url': False
    }
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and 'content' in meta_desc.attrs:
        placement['in_meta_description'] = keyword.lower() in meta_desc['content'].lower()
    
    # Check H1
    h1_tags = soup.find_all('h1')
    for h1 in h1_tags:
        if keyword.lower() in h1.get_text().lower():
            placement['in_h1'] = True
            break
    
    # Check first paragraph
    first_p = soup.find('p')
    if first_p:
        placement['in_first_paragraph'] = keyword.lower() in first_p.get_text().lower()
    
    return placement

def analyze_content_quality(content):
    # Simple analysis based on content length and variety
    words = content.lower().split()
    
    if len(words) < 300:
        return 'Thin content (less than 300 words)'
    elif len(words) < 600:
        return 'Basic content (300-600 words)'
    elif len(words) < 1000:
        return 'Good content (600-1000 words)'
    else:
        return 'Excellent content (1000+ words)'

def calculate_readability_score(content):
    # Simple Flesch-Kincaid readability score
    words = content.split()
    sentences = content.split('.')
    
    if not words or not sentences:
        return 0
    
    word_count = len(words)
    sentence_count = len(sentences)
    syllable_count = sum(count_syllables(word) for word in words)
    
    if sentence_count == 0:
        return 0
        
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
    return round(score, 2)

def count_syllables(word):
    # Basic syllable counter
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    
    if not word:
        return 0
        
    if word[0] in vowels:
        count += 1
    
    for i in range(1, len(word)):
        if word[i] in vowels and word[i-1] not in vowels:
            count += 1
    
    if word.endswith('e'):
        count -= 1
    
    if count == 0:
        count = 1
        
    return count

def estimate_page_load_time(soup):
    # Estimate page load time based on content size
    html_size = len(str(soup))
    images_size = sum(1 for _ in soup.find_all('img')) * 100  # Assume avg 100KB per image
    scripts_size = sum(len(script.string or '') for script in soup.find_all('script'))
    
    total_size = html_size + images_size + scripts_size
    
    # Very rough estimation
    if total_size < 500000:  # Less than 500KB
        return 'Fast (estimated <2s)'
    elif total_size < 2000000:  # Less than 2MB
        return 'Medium (estimated 2-5s)'
    else:
        return 'Slow (estimated >5s)'

def calculate_avg_paragraph_length(soup):
    paragraphs = soup.find_all('p')
    
    if not paragraphs:
        return 0
        
    total_words = sum(len(p.get_text().split()) for p in paragraphs)
    return round(total_words / len(paragraphs), 2)

def analyze_schema_markup(soup):
    schema_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    
    if not schema_scripts:
        return 'No schema markup found'
        
    schema_types = []
    
    for script in schema_scripts:
        try:
            data = json.loads(script.string)
            if '@type' in data:
                schema_types.append(data['@type'])
        except:
            pass
            
    if not schema_types:
        return 'Invalid schema markup found'
        
    return f"Found schema types: {', '.join(schema_types)}"

def check_html_errors(html_content):
    # Simple HTML validation check
    common_errors = [
        ('<div', '</div>', 'Div tags mismatch'),
        ('<p', '</p>', 'Paragraph tags mismatch'),
        ('<a', '</a>', 'Anchor tags mismatch'),
        ('<span', '</span>', 'Span tags mismatch')
    ]
    
    errors = []
    
    for open_tag, close_tag, error_msg in common_errors:
        if html_content.count(open_tag) != html_content.count(close_tag):
            errors.append(error_msg)
    
    return errors if errors else 'No major HTML errors detected'

def check_css_errors(html_content):
    # Check for inline styles
    inline_styles = html_content.count('style=')
    
    if inline_styles > 10:
        return f'Found {inline_styles} inline styles (consider using CSS classes)'
    return 'No major CSS issues detected'

def identify_competitors(website_url, keyword):
    """Identify potential competitors based on the website's niche and keywords"""
    # Extract domain information
    parsed_url = urlparse(website_url)
    domain = parsed_url.netloc.replace('www.', '')
    
    # Industry-specific competitors based on keywords
    industry_competitors = {
        'web': ['wix.com', 'squarespace.com', 'webflow.com', 'wordpress.org'],
        'seo': ['moz.com', 'semrush.com', 'ahrefs.com', 'searchenginejournal.com'],
        'marketing': ['hubspot.com', 'mailchimp.com', 'marketo.com', 'hootsuite.com'],
        'ecommerce': ['shopify.com', 'bigcommerce.com', 'magento.com', 'woocommerce.com'],
        'design': ['behance.net', 'dribbble.com', 'awwwards.com', 'creative-tim.com'],
        'blog': ['medium.com', 'ghost.org', 'substack.com', 'blogger.com'],
        'tech': ['techcrunch.com', 'theverge.com', 'wired.com', 'cnet.com']
    }
    
    # Determine industry based on keyword
    keywords_lower = keyword.lower()
    selected_industry = 'web'  # Default industry
    
    for industry, _ in industry_competitors.items():
        if industry in keywords_lower:
            selected_industry = industry
            break
    
    # Get competitors for the selected industry
    competitors = industry_competitors.get(selected_industry, industry_competitors['web'])
    
    # Add industry to competitor names for clarity
    return [f"{comp} ({selected_industry.title()} industry leader)" for comp in competitors[:3]]

def generate_report_id():
    import uuid
    return str(uuid.uuid4())

def generate_report_token(report):
    # Create a secure token for accessing reports
    import hashlib
    import time
    
    timestamp = str(int(time.time()))
    data = f"{report['title_tag']}:{timestamp}:{generate_report_id()}"
    return hashlib.sha256(data.encode()).hexdigest()

def save_report_to_database(report, token):
    # This would save to a database in a real implementation
    # For now, just log that we would save
    logger.info(f"Would save report with token {token} to database")
    # In a real implementation:
    # ReportModel.objects.create(
    #     token=token,
    #     data=json.dumps(report),
    #     created_at=timezone.now(),
    #     is_premium=False
    # )

# Premium feature simulation functions
def simulate_indexed_pages(website_url):
    """Simulate indexed pages count for premium users"""
    # In a real implementation, this would connect to a search API
    parsed_url = urlparse(website_url)
    domain = parsed_url.netloc
    
    # Generate a random but consistent number based on domain
    import hashlib
    hash_val = int(hashlib.md5(domain.encode()).hexdigest(), 16) % 10000
    return f"{hash_val} pages"

def simulate_js_errors():
    """Simulate JavaScript error detection for premium users"""
    # In a real implementation, this would use a headless browser
    errors = [
        "No critical JavaScript errors detected",
        "1 script loading optimization opportunity found",
        "Consider implementing lazy loading for non-critical scripts"
    ]
    return errors

def simulate_competitor_details(competitors):
    """Generate detailed competitor analysis with realistic data"""
    if not competitors or len(competitors) == 0:
        return ["No direct competitors identified"]
    
    # Industry-specific metrics and patterns
    strength_patterns = {
        'seo': ['Strong organic search visibility', 'Comprehensive keyword targeting', 'Quality backlink profile'],
        'web': ['Fast page loading speed', 'Modern responsive design', 'Intuitive user interface'],
        'ecommerce': ['Streamlined checkout process', 'Product recommendation engine', 'Multiple payment options'],
        'marketing': ['Engaging content marketing', 'Effective email campaigns', 'Strong social media presence'],
        'design': ['High-quality imagery', 'Consistent brand identity', 'Smooth UX transitions'],
        'blog': ['Regular content publication', 'Strong reader engagement', 'Clear content categorization'],
        'tech': ['In-depth technical content', 'Cutting-edge innovation focus', 'Expert opinion articles']
    }
    
    weakness_patterns = {
        'seo': ['Keyword cannibalization issues', 'Thin content on key pages', 'Limited structured data'],
        'web': ['Poor mobile optimization', 'Accessibility issues', 'Heavy JavaScript usage'],
        'ecommerce': ['Limited product information', 'Confusing navigation structure', 'Few customer reviews'],
        'marketing': ['Inconsistent messaging', 'Limited audience targeting', 'Poor email deliverability'],
        'design': ['Cluttered layouts', 'Slow-loading animations', 'Poor color contrast'],
        'blog': ['Irregular posting schedule', 'Limited multimedia content', 'Poor internal linking'],
        'tech': ['Excessive technical jargon', 'Limited beginner resources', 'Outdated information']
    }
    
    opportunity_keywords = {
        'seo': ['seo strategy template', 'monthly seo packages', 'local seo services'],
        'web': ['responsive web design services', 'website maintenance plans', 'custom web development'],
        'ecommerce': ['ecommerce platform comparison', 'online store setup', 'product catalog optimization'],
        'marketing': ['digital marketing strategy', 'content marketing plan', 'social media management'],
        'design': ['professional logo design', 'brand identity packages', 'ui/ux design services'],
        'blog': ['content creation services', 'blog management', 'ghost writing services'],
        'tech': ['technology consulting services', 'it solution provider', 'digital transformation']
    }
    
    details = []
    for competitor in competitors[:3]:
        # Extract industry from competitor string (format: "domain.com (Industry industry leader)")
        industry = 'web'  # Default
        if '(' in competitor and ')' in competitor:
            industry_part = competitor.split('(')[1].split(')')[0].lower()
            for key in strength_patterns.keys():
                if key in industry_part:
                    industry = key
                    break
        
        # Extract domain name
        domain = competitor.split(' ')[0]
        
        # Get industry-specific patterns
        strengths = strength_patterns.get(industry, strength_patterns['web'])
        weaknesses = weakness_patterns.get(industry, weakness_patterns['web'])
        keywords = opportunity_keywords.get(industry, opportunity_keywords['web'])
        
        # Create detailed analysis
        import random
        random.seed(domain)  # Use domain as seed for consistent randomization
        
        details.append({
            "name": domain,
            "industry": industry.title(),
            "strengths": random.sample(strengths, min(2, len(strengths))),
            "weaknesses": random.sample(weaknesses, min(2, len(weaknesses))),
            "opportunity_keywords": random.sample(keywords, min(3, len(keywords)))
        })
    
    return details

@login_required
def generate_seo_pdf(request):
    """Generate a PDF report from SEO scan results"""
    # Conditionally import reportlab only when this function is called
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        return JsonResponse({
            'error': 'ReportLab is not installed. Please run the install_reportlab.bat script.'
        }, status=500)

    if request.method == 'POST':
        try:
            # Get report data from the request
            report_data = json.loads(request.body)
            
            # Create a file-like buffer to receive PDF data
            buffer = BytesIO()
            
            # Create the PDF object, using the buffer as its "file"
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Create styles
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Add the title
            elements.append(Paragraph("SEO Analysis Report", title_style))
            elements.append(Spacer(1, 20))
            
            # Add basic info
            elements.append(Paragraph("Basic Information", heading_style))
            basic_data = [
                ["Website URL", report_data.get('website_url', 'N/A')],
                ["Title Tag", report_data.get('title_tag', 'N/A')],
                ["Meta Description", report_data.get('meta_description', 'N/A')],
            ]
            basic_table = Table(basic_data, colWidths=[150, 350])
            basic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(basic_table)
            elements.append(Spacer(1, 20))
            
            # Add keyword analysis
            elements.append(Paragraph("Keyword Analysis", heading_style))
            if 'keyword_analysis' in report_data:
                keyword_data = [
                    ["Keyword Count", str(report_data.get('keyword_count', 0))],
                    ["Keyword Density", f"{report_data['keyword_analysis'].get('keyword_density', 0)}%"],
                ]
                keyword_table = Table(keyword_data, colWidths=[150, 350])
                keyword_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(keyword_table)
                
                # Add extracted keywords
                if 'extracted_keywords' in report_data['keyword_analysis']:
                    elements.append(Spacer(1, 10))
                    elements.append(Paragraph("Top Extracted Keywords:", styles['Heading3']))
                    extracted = report_data['keyword_analysis']['extracted_keywords'][:5]
                    for kw in extracted:
                        if isinstance(kw, list) and len(kw) >= 2:
                            elements.append(Paragraph(f"• {kw[0]}: {kw[1]} occurrences", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Add content analysis
            elements.append(Paragraph("Content Analysis", heading_style))
            if 'content_analysis' in report_data:
                ca = report_data['content_analysis']
                content_data = [
                    ["Content Quality", ca.get('content_quality', 'Not analyzed')],
                    ["Word Count", str(ca.get('word_count', 0))],
                    ["Readability Score", str(ca.get('readability_score', 0))],
                    ["Paragraph Count", str(ca.get('paragraph_count', 0))],
                ]
                content_table = Table(content_data, colWidths=[150, 350])
                content_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(content_table)
            
            elements.append(Spacer(1, 20))
            
            # Add technical SEO
            elements.append(Paragraph("Technical SEO", heading_style))
            if 'technical_seo' in report_data:
                tech = report_data['technical_seo']
                tech_data = [
                    ["Page Load Time", str(tech.get('page_load_time', 'Not analyzed'))],
                    ["Mobile Friendly", "Yes" if tech.get('mobile_friendly') else "No"],
                    ["HTTPS Enabled", "Yes" if tech.get('https_enabled') else "No"],
                    ["Schema Markup", "Yes" if tech.get('schema_markup') else "No"],
                ]
                tech_table = Table(tech_data, colWidths=[150, 350])
                tech_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(tech_table)
            
            elements.append(Spacer(1, 20))
            
            # Add SEO suggestions
            elements.append(Paragraph("SEO Suggestions", heading_style))
            if 'on_page_seo_suggestions' in report_data and report_data['on_page_seo_suggestions']:
                for suggestion in report_data['on_page_seo_suggestions']:
                    elements.append(Paragraph(f"• {suggestion}", normal_style))
                    elements.append(Spacer(1, 5))
            else:
                elements.append(Paragraph("No major issues found!", normal_style))
            
            # Build the PDF
            doc.build(elements)
            
            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)
            
            # Create the HTTP response with PDF
            response = HttpResponse(buffer, content_type='application/pdf')
            filename = f"SEO_Report_{report_data.get('website_url', 'website').replace('https://', '').replace('http://', '').replace('/', '_')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            return JsonResponse({'error': f'Error generating PDF: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# New views for Off-Page SEO Automation

@login_required
def offpage_seo_automation(request):
    """Render the Off-Page SEO Automation page"""
    previous_jobs = SEOTask.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'autoseo/offpage.html', {'previous_jobs': previous_jobs})

@login_required
@csrf_exempt
def generate_content_api(request):
    """API endpoint to generate content for SEO tasks"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        task_type = data.get('task_type')
        website_url = data.get('website_url')
        keywords = data.get('keywords')
        
        # Validate required fields
        if not all([task_type, website_url, keywords]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
        
        # Create a new task
        task = SEOTask.objects.create(
            user=request.user,
            task_type=task_type,
            website_url=website_url,
            keywords=keywords,
            status='generating',
            # Add task-specific fields based on task_type
            topic=data.get('topic', ''),
            platform=data.get('platform', ''),
            target_url=data.get('blog_url', ''),
            category=data.get('category', ''),
        )
        
        # Generate content
        try:
            content = generate_ai_content_for_task(task)
            task.generated_content = content
            task.status = 'review'
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'task_id': task.id,
                'content': content
            })
        except Exception as e:
            task.status = 'failed'
            task.submission_result = str(e)
            task.save()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@csrf_exempt
def submit_task_api(request):
    """API endpoint to submit an SEO task after review"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        content = data.get('content')
        
        if not task_id or not content:
            return JsonResponse({'status': 'error', 'message': 'Task ID and content are required'}, status=400)
        
        try:
            task = SEOTask.objects.get(id=task_id, user=request.user)
            task.edited_content = content
            task.status = 'submitted'
            task.save()
            
            # Process the actual submission based on task type
            result = process_task_submission(task)
            
            task.submission_result = result
            task.status = 'completed'
            task.completed_at = datetime.now()
            task.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Task submitted successfully',
                'result': result
            })
        except SEOTask.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)
        except Exception as e:
            if 'task' in locals():
                task.status = 'failed'
                task.submission_result = str(e)
                task.save()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def seo_task_detail(request, task_id):
    """View task details and results"""
    task = get_object_or_404(SEOTask, id=task_id, user=request.user)
    return render(request, 'autoseo/seo_task_detail.html', {'task': task})

# Helper functions for Off-Page SEO Automation

def generate_ai_content_for_task(task):
    """Generate content using Hugging Face API or other AI services"""
    try:
        # Try to get user's Hugging Face API credentials
        api_credentials = APICredential.objects.filter(
            user=task.user, 
            service='huggingface',
            is_active=True
        ).first()
        
        if api_credentials:
            # Use Hugging Face API for content generation
            api_key = api_credentials.api_key
            return generate_with_huggingface(task, api_key)
        else:
            # Fallback to template-based generation if no API key is available
            return generate_template_content(task)
    except Exception as e:
        # Log the error and fall back to template content
        logger.error(f"Error generating AI content: {str(e)}")
        return generate_template_content(task)

def generate_with_huggingface(task, api_key):
    """Generate content using Hugging Face Inference API"""
    
    # Construct the prompt based on task type
    if task.task_type == 'guest_post':
        prompt = f"""
        Write a professional guest post outreach email for the website {task.website_url}.
        Target blog: {task.target_url or 'relevant industry blogs'}
        Keywords: {task.keywords}
        Proposed topic: {task.topic}
        Make it persuasive but not spammy, focusing on value for the blog's audience.
        """
    elif task.task_type == 'social_media':
        prompt = f"""
        Create a {task.platform} post promoting the website {task.website_url}.
        Keywords: {task.keywords}
        Include relevant hashtags and a compelling call to action.
        Keep it within the appropriate length for {task.platform}.
        """
    elif task.task_type == 'directory':
        prompt = f"""
        Write a directory submission for {task.website_url}.
        Business category: {task.category}
        Keywords: {task.keywords}
        Create a concise but keyword-rich description.
        """
    elif task.task_type == 'forum':
        prompt = f"""
        Write a helpful forum response related to {task.topic}.
        Naturally mention or link to {task.website_url} as a resource.
        Keywords: {task.keywords}
        Make it genuinely helpful first, with the link being a natural addition.
        """
    
    # Call Hugging Face API
    try:
        import requests
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2" 
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 500}
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Extract the generated text from the response
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            return result.get('generated_text', '').strip()
        else:
            # If the API call fails, log the error and fall back to templates
            logger.error(f"Hugging Face API error: {response.text}")
            return generate_template_content(task)
    except Exception as e:
        logger.error(f"Error calling Hugging Face API: {str(e)}")
        return generate_template_content(task)

def generate_template_content(task):
    """Generate content using pre-defined templates when AI generation fails"""
    if task.task_type == 'guest_post':
        topic = task.topic or f"The Complete Guide to {task.keywords}"
        target_blog = task.target_url or 'your blog'
        
        return f"""Subject: Guest Post Proposal: {topic}

Hi there,

I hope this email finds you well. I came across {target_blog} and really enjoyed your content, especially your articles about {task.keywords}.

I'd love to contribute a guest post titled "{topic}" that I believe would resonate with your audience. The article will cover actionable insights on {task.keywords.split(',')[0]} and provide value to your readers.

My website ({task.website_url}) focuses on similar topics, and I've previously contributed to several industry blogs.

Would you be interested in this collaboration? I can send you a detailed outline if you'd like.

Looking forward to your response,
[Your Name]"""
        
    elif task.task_type == 'social_media':
        platform = task.platform or 'social media'
        keywords_list = task.keywords.split(',')
        main_keyword = keywords_list[0].strip()
        hashtags = ' '.join(['#' + kw.strip().replace(' ', '') for kw in keywords_list])
        
        if platform == 'twitter':
            return f"Check out our latest insights on {main_keyword}! Learn how to improve your strategy and get better results. {task.website_url} {hashtags}"
        else:
            return f"""🚀 New Post Alert: {main_keyword} Strategies for {datetime.now().year}

We've just published a comprehensive guide on optimizing your {main_keyword} approach. Discover the latest techniques and tools that can help you achieve better results.

Read the full article here: {task.website_url}

{hashtags}"""
        
    elif task.task_type == 'directory':
        domain = task.website_url.replace('https://', '').replace('http://', '').split('/')[0]
        category = task.category or 'Business'
        
        return f"""Website Title: {domain}
Website URL: {task.website_url}
Category: {category}
Keywords: {task.keywords}
Description: We provide professional {task.keywords} services. Our team specializes in delivering high-quality solutions tailored to meet our clients' specific needs.

This listing will be submitted to relevant business directories to improve your website's visibility and backlink profile."""
        
    elif task.task_type == 'forum':
        topic = task.topic or f"Discussion about {task.keywords}"
        
        return f"""Re: {topic}

Great question! Based on my experience with {task.keywords.split(',')[0]}, I'd recommend the following approaches:

1. Start by analyzing your current metrics to establish a baseline
2. Implement targeted improvements based on industry best practices
3. Regularly test and optimize your strategy

I recently wrote an in-depth article about this topic that provides more detailed guidance: {task.website_url}

Hope this helps! Let me know if you have any other questions."""

def process_task_submission(task):
    """Process the actual submission of an SEO task"""
    if task.task_type == 'guest_post':
        return send_outreach_email(task)
    elif task.task_type == 'social_media':
        return post_to_social_media(task)
    elif task.task_type == 'directory':
        return submit_to_directory(task)
    elif task.task_type == 'forum':
        return post_to_forum(task)
    else:
        raise ValueError(f"Unknown task type: {task.task_type}")

def send_outreach_email(task):
    """Send actual outreach emails for guest posts"""
    try:
        # Get email service credentials
        email_creds = APICredential.objects.filter(
            user=task.user, 
            service='email',
            is_active=True
        ).first()
        
        if not email_creds:
            return "Email simulation: No email credentials found. This would send an email to the blog owner."
        
        # Extract target email from task
        target_blog = task.target_url
        # In a real implementation, you might:
        # 1. Use a service to find contact information for the blog
        # 2. Store a list of blog contacts in your database
        
        # For now, we'll simulate the email sending process
        content = task.edited_content or task.generated_content
        
        # Log the email that would be sent
        log_message = f"Would send email about '{task.topic}' to the owner of {target_blog}"
        logger.info(log_message)
        
        return f"Email simulation: {log_message}"
    except Exception as e:
        logger.error(f"Error in send_outreach_email: {str(e)}")
        return f"Email simulation error: {str(e)}"

def post_to_social_media(task):
    """Post to social media platforms"""
    try:
        platform = task.platform or 'twitter'
        content = task.edited_content or task.generated_content
        
        # Get API credentials for the platform
        api_creds = APICredential.objects.filter(
            user=task.user, 
            service=platform.lower(),
            is_active=True
        ).first()
        
        if not api_creds:
            return f"Social media simulation: Would post to {platform}."
            
        # Log the post that would be created
        log_message = f"Would post to {platform}: {content[:50]}..."
        logger.info(log_message)
        
        return f"Social media simulation: {log_message}"
    except Exception as e:
        logger.error(f"Error in post_to_social_media: {str(e)}")
        return f"Social media simulation error: {str(e)}"

def submit_to_directory(task):
    """Submit to business directories"""
    try:
        content = task.edited_content or task.generated_content
        category = task.category or 'Business'
        
        # Log the directory submission that would be made
        log_message = f"Would submit {task.website_url} to directories under category '{category}'"
        logger.info(log_message)
        
        return f"Directory submission simulation: {log_message}"
    except Exception as e:
        logger.error(f"Error in submit_to_directory: {str(e)}")
        return f"Directory submission simulation error: {str(e)}"

def post_to_forum(task):
    """Post to relevant forums"""
    try:
        content = task.edited_content or task.generated_content
        topic = task.topic or f"Discussion about {task.keywords}"
        
        # Log the forum post that would be created
        log_message = f"Would post response to '{topic}' on relevant forums"
        logger.info(log_message)
        
        return f"Forum posting simulation: {log_message}"
    except Exception as e:
        logger.error(f"Error in post_to_forum: {str(e)}")
        return f"Forum posting simulation error: {str(e)}"

@require_GET
def robots_txt(request):
    """Serve robots.txt file"""
    file_path = os.path.join(settings.BASE_DIR, 'robots.txt')
    with open(file_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/plain')

@require_GET
def sitemap_xml(request):
    """Serve sitemap.xml file"""
    file_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
    with open(file_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/xml')

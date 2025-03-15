from django.http import JsonResponse
from django.shortcuts import render, redirect
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
from .models import SEOJob, SEOResult
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm


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
    return render(request, 'autoseo/pricing.html')

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

def offpage_seo(request):    
     if request.method == "POST":
        url = request.POST.get("website")
        keywords = request.POST.get("keywords")
        
        job = SEOJob.objects.create(url=url, keywords=keywords)
        generate_and_post_content(job.id)  # Start automation
        return redirect("seo_results", job_id=job.id)

     return render(request, "autoseo/offpage.html")

def seo_results(request, job_id):
    job = SEOJob.objects.get(id=job_id)
    results = SEOResult.objects.filter(job=job)
    return render(request, "autoseo/seo_results.html", {"results": results})

def generate_and_post_content(job_id):
    job = SEOJob.objects.get(id=job_id)

    # 1️⃣ Generate AI content
    content = generate_ai_content(job.keywords)
    SEOResult.objects.create(job=job, step="AI Content", result_data=content)

    # 2️⃣ Post to WordPress
    wp_post_url = post_to_wordpress(content, f"SEO Post for {job.keywords}")
    if wp_post_url:
        SEOResult.objects.create(job=job, step="Blog Post", result_data=wp_post_url)

    # 3️⃣ Share on Twitter
    if wp_post_url:
        tweet_link = post_to_twitter(f"Check out our new post on {job.keywords} {wp_post_url}")
        SEOResult.objects.create(job=job, step="Social Media", result_data=tweet_link)

def generate_ai_content(keywords):
    """Generate AI content using OpenAI API"""
    prompt = f"Write an SEO-optimized blog post about {keywords}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

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
            # Fetch website content
            response = requests.get(website_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return JsonResponse({'error': f'Could not fetch website: {str(e)}'}, status=400)

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            html_content = soup.get_text()

            # Extract main keywords from the page content
            extracted_keywords = extract_keywords(html_content)

            # Get related keywords for the main input keyword (if provided)
            related_keywords = get_related_keywords(keywords) if keywords else []

            # SEO analysis
            report = {
                'title_tag': soup.title.string if soup.title else 'Not found',
                'meta_description': get_meta_description(soup),
                'meta_tags': [str(tag) for tag in soup.find_all('meta')],
                'keyword_count': html_content.lower().count(keywords.lower()),
                'page_ranking': 'N/A',  # Placeholder for actual page ranking logic
                'on_page_seo_suggestions': get_seo_suggestions(soup),
                'keyword_analysis': {
                    'keyword_density': round(
                        (html_content.lower().count(keywords.lower()) / 
                         max(len(html_content.split()), 1)) * 100, 2
                    ),
                     'extracted_keywords': extracted_keywords,  # Add extracted keywords
                    'related_keywords': related_keywords  # Add related keywords
                },
                'other_seo_metrics': {
                    'num_images': len(soup.find_all('img')),
                    'num_links': len(soup.find_all('a')),
                    'num_scripts': len(soup.find_all('script')),
                    'num_h1': len(soup.find_all('h1')),
                    'num_h2': len(soup.find_all('h2')),
                    'num_h3': len(soup.find_all('h3')),
                    'canonical_tag': get_canonical_tag(soup),
                    'page_speed': 'N/A',  # Placeholder for page speed integration
                    'internal_links': get_internal_links(soup, website_url),
                    'external_links': get_external_links(soup, website_url),
                    'structured_data': check_structured_data(soup),
                    'mobile_friendly': check_mobile_friendly(soup),
                    'social_media_tags': check_social_media_tags(soup),
                    'noindex_tag': check_noindex_tag(soup),
                    'xml_sitemap': check_xml_sitemap(website_url),
                    'robots_txt': check_robots_txt(website_url),
                    'text_to_html_ratio': check_text_to_html_ratio(soup, html_content),
                },
                'broken_links': [],  # Implement broken link check if needed
                'js_errors': []  # If you plan to check JS errors, implement here
            }

            return JsonResponse({'report': report})

        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return JsonResponse({'error': 'Error analyzing content'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_seo_suggestions(soup):
    suggestions = []
    
    if not soup.find('title'):
        suggestions.append("Missing title tag")
    if not soup.find('meta', attrs={'name': 'description'}):
        suggestions.append("Missing meta description")
    if not soup.find('h1'):
        suggestions.append("Missing H1 heading")
    else:
        h1_tag = soup.find('h1').get_text().strip()
        if len(h1_tag) < 30:
            suggestions.append(f"H1 tag is too short: {h1_tag}")
    
    # Add image alt text check
    for img in soup.find_all('img'):
        if not img.get('alt') or len(img['alt']) < 5:
            suggestions.append(f"Image missing alt text or alt text is too short: {img.get('src', '')[:50]}")
    
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

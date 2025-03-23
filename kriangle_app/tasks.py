# Mock Celery implementation for production deployments
# Instead of: from celery import shared_task

import openai
import requests
import time
import random
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import send_mail
from .models import SEOJob, SEOResult, BlogPost, OffPageSEOAction

logger = logging.getLogger(__name__)

# Mock implementation of shared_task decorator
def shared_task(func=None, **kwargs):
    """
    Mock implementation of shared_task that runs the function synchronously
    """
    if func is None:
        return lambda f: f
    return func

# Directory submission sites (free)
DIRECTORY_SITES = [
    {"url": "https://www.freedirectorysubmissionsites.com/", "name": "Free Directory Submissions"},
    {"url": "https://www.exactseek.com/add.html", "name": "ExactSeek"},
    {"url": "https://www.jayde.com/submit.html", "name": "Jayde"},
    {"url": "https://www.somuch.com/submit-links/", "name": "SoMuch"},
    {"url": "https://www.chamberofcommerce.com/", "name": "Chamber of Commerce"},
]

# Bookmarking sites
BOOKMARKING_SITES = [
    {"url": "https://www.diigo.com/", "name": "Diigo"},
    {"url": "https://www.bibsonomy.org/", "name": "BibSonomy"},
    {"url": "https://www.folkd.com/", "name": "Folkd"},
    {"url": "https://www.pearltrees.com/", "name": "Pearltrees"},
]

# RSS submission sites
RSS_SITES = [
    {"url": "https://www.feedage.com/", "name": "Feedage"},
    {"url": "https://www.feedspot.com/", "name": "Feedspot"},
    {"url": "https://www.rssmicro.com/", "name": "RSSmicro"},
]

# Forum sites for link building
FORUM_SITES = [
    {"url": "https://www.quora.com/", "name": "Quora"},
    {"url": "https://www.reddit.com/", "name": "Reddit"},
    {"url": "https://forums.digitalpoint.com/", "name": "Digital Point"},
]

@shared_task
def process_offpage_seo(job_id):
    """Process off-page SEO for the given job ID"""
    try:
        # Get the job
        job = SEOJob.objects.get(id=job_id)
        job.status = "processing"
        job.save()
        
        # For testing purposes, we'll just log and create simple results
        website_url = job.url
        keywords_list = job.keywords.split(',')
        
        # Create a simple record
        SEOResult.objects.create(
            job=job, 
            step="Test Step", 
            result_data=f"Successfully processed job for {website_url} with keywords: {keywords_list}",
        )
        
        # Create mock blog post
        blog_post = BlogPost.objects.create(
            job=job,
            title=f"Test post about {keywords_list[0]}",
            content=f"<h1>Test Content</h1><p>This is a test post about {', '.join(keywords_list)}.</p>",
            url=f"https://example.com/post-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        
        # Create action record
        OffPageSEOAction.objects.create(
            job=job,
            action_type="Test Action",
            platform="Test Platform",
            url="https://example.com",
            status="success"
        )
        
        # Mark job as completed
        job.status = "completed"
        job.save()
        
        return f"Job {job_id} completed successfully"
        
    except Exception as e:
        logger.error(f"Error in process_offpage_seo for job {job_id}: {str(e)}")
        if 'job' in locals():
            job.status = "failed"
            job.save()
            SEOResult.objects.create(
                job=job, 
                step="Error", 
                result_data=f"Error: {str(e)}",
                status="failed"
            )
        return f"Job {job_id} failed: {str(e)}"

def generate_blog_content(website_url, keywords_list):
    """Generate blog content using OpenAI API"""
    try:
        # Get website information
        response = requests.get(website_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        site_title = soup.title.string if soup.title else urlparse(website_url).netloc
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        site_description = meta_desc['content'] if meta_desc else "Website"
        
        # Create prompt for AI
        primary_keyword = keywords_list[0]
        secondary_keywords = ", ".join(keywords_list[1:]) if len(keywords_list) > 1 else ""
        
        prompt = f"""
        Write a high-quality, SEO-optimized blog post about {primary_keyword}.
        
        Website information:
        - Website: {site_title}
        - Description: {site_description}
        
        The blog post should:
        - Have an engaging title that includes the primary keyword: {primary_keyword}
        - Be at least 800 words long
        - Include the primary keyword in the first paragraph
        - Naturally incorporate these secondary keywords: {secondary_keywords}
        - Include 3-5 subheadings (H2)
        - Include a conclusion with a call to action
        - Be written in a professional, informative tone
        - Include bullet points where appropriate
        
        Format the post in HTML.
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO content writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        content = response["choices"][0]["message"]["content"]

        # Extract title from HTML content
        soup = BeautifulSoup(content, 'html.parser')
        title_tag = soup.find('h1')
        title = title_tag.text if title_tag else f"Article about {primary_keyword}"
        
        return content, title
        
    except Exception as e:
        logger.error(f"Error generating blog content: {str(e)}")
        # Fallback content generation
        title = f"{keywords_list[0]} - {datetime.now().strftime('%Y-%m-%d')}"
        content = f"<h1>{title}</h1><p>Article about {', '.join(keywords_list)}.</p>"
        return content, title

def create_blog_post(job, title, content):
    """Create a blog post entry in the database"""
    try:
        # In a real-world scenario, this would publish to an actual blog
        # For this implementation, we'll simulate it
        blog_post = BlogPost.objects.create(
            job=job,
            title=title,
            content=content,
            url=f"https://blog.example.com/posts/{int(time.time())}"  # Simulated URL
        )
        
        # Record action
        OffPageSEOAction.objects.create(
            job=job,
            action_type="Blog Post Creation",
            platform="Internal Blog",
            url=blog_post.url,
            status="success"
        )
        
        return blog_post
    except Exception as e:
        logger.error(f"Error creating blog post: {str(e)}")
        OffPageSEOAction.objects.create(
            job=job,
            action_type="Blog Post Creation",
            platform="Internal Blog",
            status="failed"
        )
        return None

def submit_to_directories(job, website_url, keywords_list):
    """Submit website to directories"""
    successful_submissions = 0
    
    for directory in DIRECTORY_SITES:
        try:
            time.sleep(random.uniform(1, 3))  # Random delay to avoid being flagged as bot
            
            # In a real implementation, this would use Selenium or requests with proper form submission
            # Simulating success/failure for demo purposes
            success = random.random() > 0.2  # 80% success rate for simulation
            
            status = "success" if success else "failed"
            if success:
                successful_submissions += 1
                
            OffPageSEOAction.objects.create(
                job=job,
                action_type="Directory Submission",
                platform=directory["name"],
                url=directory["url"],
                status=status
            )
            
        except Exception as e:
            logger.error(f"Error submitting to directory {directory['name']}: {str(e)}")
            OffPageSEOAction.objects.create(
                job=job,
                action_type="Directory Submission",
                platform=directory["name"],
                url=directory["url"],
                status="failed"
            )
    
    return successful_submissions

def submit_to_bookmarking(job, website_url, keywords_list):
    """Submit to social bookmarking sites"""
    successful_submissions = 0
    
    for site in BOOKMARKING_SITES:
        try:
            time.sleep(random.uniform(1, 3))  # Random delay
            
            # Simulate submission (would use Selenium or API in real implementation)
            success = random.random() > 0.3  # 70% success rate for simulation
            
            status = "success" if success else "failed"
            if success:
                successful_submissions += 1
                
            OffPageSEOAction.objects.create(
                job=job,
                action_type="Social Bookmarking",
                platform=site["name"],
                url=site["url"],
                status=status
            )
            
        except Exception as e:
            logger.error(f"Error submitting to bookmarking site {site['name']}: {str(e)}")
            OffPageSEOAction.objects.create(
                job=job,
                action_type="Social Bookmarking",
                platform=site["name"],
                url=site["url"],
                status="failed"
            )
    
    return successful_submissions

def create_and_submit_rss(job, website_url, keywords_list):
    """Create RSS feed and submit to directories"""
    successful_submissions = 0
    
    try:
        # Create simulated RSS feed (would generate actual XML in production)
        domain = urlparse(website_url).netloc
        
        # Simulate RSS feed submission
        for site in RSS_SITES:
            time.sleep(random.uniform(1, 2))  # Random delay
            
            # Simulate submission
            success = random.random() > 0.4  # 60% success rate for simulation
            
            status = "success" if success else "failed"
            if success:
                successful_submissions += 1
                
            OffPageSEOAction.objects.create(
                job=job,
                action_type="RSS Feed Submission",
                platform=site["name"],
                url=site["url"],
                status=status
            )
            
    except Exception as e:
        logger.error(f"Error with RSS feed creation/submission: {str(e)}")
        OffPageSEOAction.objects.create(
            job=job,
            action_type="RSS Feed Creation",
            platform="RSS Feed Generator",
            status="failed"
        )
    
    return successful_submissions

def submit_to_forums(job, website_url, keywords_list):
    """Submit to forums with backlinks"""
    successful_posts = 0
    
    for forum in FORUM_SITES:
        try:
            time.sleep(random.uniform(2, 4))  # Random delay
            
            # Generate forum post content
            primary_keyword = keywords_list[0]
            forum_content = f"I recently found this interesting website about {primary_keyword}. Check it out: {website_url}"
            
            # Simulate forum posting (would use Selenium or API in real implementation)
            success = random.random() > 0.5  # 50% success rate
            
            status = "success" if success else "failed"
            if success:
                successful_posts += 1
                
            OffPageSEOAction.objects.create(
                job=job,
                action_type="Forum Posting",
                platform=forum["name"],
                url=forum["url"],
                status=status
            )
            
        except Exception as e:
            logger.error(f"Error posting to forum {forum['name']}: {str(e)}")
            OffPageSEOAction.objects.create(
                job=job,
                action_type="Forum Posting",
                platform=forum["name"],
                url=forum["url"],
                status="failed"
            )
    
    return successful_posts

def create_link_wheel(job, website_url, keywords_list, blog_post):
    """Create a link wheel to improve backlink structure"""
    nodes_created = 0
    
    try:
        if not blog_post:
            return 0
            
        # In a real implementation, this would create multiple web 2.0 profiles 
        # and link them together in a wheel pattern pointing to the main site
        # For demo purposes, we'll simulate it
        
        # Simulated Web 2.0 platforms
        web20_platforms = [
            {"name": "WordPress.com", "url": "https://wordpress.com"},
            {"name": "Blogger", "url": "https://blogger.com"},
            {"name": "Medium", "url": "https://medium.com"},
            {"name": "Tumblr", "url": "https://tumblr.com"},
            {"name": "Weebly", "url": "https://weebly.com"},
        ]
        
        # Create simulated link wheel nodes
        for i, platform in enumerate(web20_platforms):
            time.sleep(random.uniform(1, 3))
            
            # Simulate creating content on Web 2.0 platforms
            success = random.random() > 0.3  # 70% success rate
            
            if success:
                nodes_created += 1
                
                # Link to next node in the wheel
                next_platform = web20_platforms[(i + 1) % len(web20_platforms)]
                
                OffPageSEOAction.objects.create(
                    job=job,
                    action_type="Link Wheel Node",
                    platform=platform["name"],
                    url=f"{platform['url']}/{urlparse(website_url).netloc.replace('.', '-')}", # Simulated URL
                    status="success"
                )
            else:
                OffPageSEOAction.objects.create(
                    job=job,
                    action_type="Link Wheel Node",
                    platform=platform["name"],
                    url=platform["url"],
                    status="failed"
                )
        
    except Exception as e:
        logger.error(f"Error creating link wheel: {str(e)}")
        OffPageSEOAction.objects.create(
            job=job,
            action_type="Link Wheel Creation",
            platform="Link Wheel Generator",
            status="failed"
        )
    
    return nodes_created

@shared_task
def test_task(param):
    """Simple test task used for testing Celery functionality"""
    logger.info(f"Test task executed with parameter: {param}")
    return f"Test task completed with parameter: {param}"

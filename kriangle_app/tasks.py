from celery import shared_task
import openai
import requests
from .models import SEORequest

@shared_task
def process_seo_automation(seo_request_id):
    seo_request = SEORequest.objects.get(id=seo_request_id)
    seo_request.status = "processing"
    seo_request.save()

    website = seo_request.website
    keywords = seo_request.keywords

    # 1️⃣ Generate AI Content
    prompt = f"Write an SEO-optimized blog post about {keywords}."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response["choices"][0]["message"]["content"]

    # 2️⃣ Submit to Directories (Backlink Building)
    directories = ["https://directory1.com/submit", "https://directory2.com/submit"]
    for directory in directories:
        try:
            requests.post(directory, data={"url": website})
        except:
            pass  # Handle submission failure

    # 3️⃣ Social Media Posting (Twitter)
    twitter_api = "https://api.twitter.com/2/tweets"
    twitter_headers = {"Authorization": "Bearer YOUR_TWITTER_TOKEN"}
    tweet_data = {"text": f"Check out this awesome site! {website}"}
    requests.post(twitter_api, json=tweet_data, headers=twitter_headers)

    # 4️⃣ Track SEO Performance
    moz_api = f"https://moz.com/api/v1/domain-authority?url={website}"
    seo_report = requests.get(moz_api).json()

    # Mark as completed
    seo_request.status = "completed"
    seo_request.save()

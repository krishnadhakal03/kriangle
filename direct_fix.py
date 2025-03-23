import os
import django
import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')
django.setup()

from kriangle_app.models import SEOJob, SEOResult, OffPageSEOAction

print("===== Direct Fix for Off-page SEO =====")

# Create a test SEO job
url = "https://example.com"
keywords = "test, keywords"

print(f"Creating test job for URL: {url}, Keywords: {keywords}")
job = SEOJob.objects.create(url=url, keywords=keywords, status="processing")
print(f"Created job with ID: {job.id}")

# Create results
print("Creating results...")
steps = ["Initialization", "Analysis", "Directory Submission", "Social Bookmarking", "Completion"]
for step in steps:
    SEOResult.objects.create(
        job=job,
        step=step,
        result_data=f"Performed {step} for {url} targeting {keywords}",
        status="success"
    )
    print(f"Created result for step: {step}")

# Create actions
print("Creating actions...")
platforms = ["Google Business", "Facebook", "Twitter", "Directory Site"]
for i, platform in enumerate(platforms):
    OffPageSEOAction.objects.create(
        job=job,
        action_type="Submission" if i < 2 else "Post",
        platform=platform,
        url=f"https://example.com/{platform.lower().replace(' ', '-')}",
        status="success"
    )
    print(f"Created action for platform: {platform}")

# Mark job as completed
job.status = "completed"
job.save()
print("Job marked as completed")

print("\n===== Fix Complete =====")
print(f"Now access the results directly at: http://127.0.0.1:8000/seo-results/{job.id}/")
print("\nIf accessing the URL above works but the form submission doesn't,")
print("there's likely an issue with the form processing or redirect.") 
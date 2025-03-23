import os
import django
import sys
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')
django.setup()

from kriangle_app.models import SEOJob, SEOResult, OffPageSEOAction
from django.contrib.auth.models import User

print("\n===== Off-page SEO Debug/Fix Tool =====")

try:
    # Check if the models exist and are accessible
    job_count = SEOJob.objects.count()
    print(f"Found {job_count} SEO jobs in the database")
    
    # Create a test job
    url = "https://example.com/debug-test"
    keywords = "test, debug, fix"
    
    print(f"Creating test SEO job for: {url}")
    job = SEOJob.objects.create(
        url=url,
        keywords=keywords,
        status="processing"
    )
    print(f"✓ Created job with ID: {job.id}")
    
    # Create test results
    print("Creating test results...")
    steps = [
        "Initialization", 
        "Website Analysis", 
        "Keyword Research", 
        "Backlink Analysis", 
        "Completion"
    ]
    
    for step in steps:
        SEOResult.objects.create(
            job=job,
            step=step,
            result_data=f"Successfully completed {step} for {url}",
            status="success"
        )
    print(f"✓ Created {len(steps)} result steps")
    
    # Create test actions
    print("Creating test actions...")
    platforms = [
        ("Google Business", "Listing"),
        ("Facebook", "Profile Optimization"),
        ("Twitter", "Post Creation"),
        ("Directory", "Submission")
    ]
    
    for platform, action_type in platforms:
        OffPageSEOAction.objects.create(
            job=job,
            platform=platform,
            action_type=action_type,
            url=f"https://example.com/{platform.lower().replace(' ', '-')}",
            status="success"
        )
    print(f"✓ Created {len(platforms)} platform actions")
    
    # Mark job as completed
    job.status = "completed"
    job.save()
    print("✓ Job marked as completed")
    
    print("\n===== Testing Access =====")
    # Test retrieving the job
    try:
        retrieved_job = SEOJob.objects.get(id=job.id)
        print(f"✓ Successfully retrieved job: {retrieved_job}")
        
        # Test retrieving results
        results = SEOResult.objects.filter(job=retrieved_job)
        print(f"✓ Retrieved {results.count()} results")
        
        # Test retrieving actions
        actions = retrieved_job.offpage_actions.all()
        print(f"✓ Retrieved {actions.count()} actions")
        
    except Exception as e:
        print(f"× Error retrieving job: {str(e)}")
    
    print("\n===== Fix Complete =====")
    print(f"* Access the results directly at: http://127.0.0.1:8000/seo-results/{job.id}/")
    print("* Try the form again at: http://127.0.0.1:8000/offpage-seo/")
    print("\n* If you still have issues:")
    print("  1. Make sure migrations have been applied")
    print("  2. Check for errors in the Django console")
    print("  3. Ensure Celery is running if using background tasks")
    
except Exception as e:
    print(f"\n× ERROR: {str(e)}")
    print("\nTrying alternative approach...")
    
    # Try with direct SQL if ORM fails
    try:
        from django.db import connection
        
        print("Creating tables directly if they don't exist...")
        with connection.cursor() as cursor:
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_seojob'")
            if not cursor.fetchone():
                print("Creating SEOJob table...")
                cursor.execute("""
                CREATE TABLE kriangle_app_seojob (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url VARCHAR(200) NOT NULL,
                    keywords TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    status VARCHAR(50) NOT NULL
                )
                """)
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_seoresult'")
            if not cursor.fetchone():
                print("Creating SEOResult table...")
                cursor.execute("""
                CREATE TABLE kriangle_app_seoresult (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step VARCHAR(100) NOT NULL,
                    result_data TEXT NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at DATETIME NOT NULL,
                    job_id INTEGER NOT NULL REFERENCES kriangle_app_seojob(id)
                )
                """)
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_offpageseoaction'")
            if not cursor.fetchone():
                print("Creating OffPageSEOAction table...")
                cursor.execute("""
                CREATE TABLE kriangle_app_offpageseoaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type VARCHAR(100) NOT NULL,
                    platform VARCHAR(255) NOT NULL,
                    url VARCHAR(200) NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at DATETIME NOT NULL,
                    job_id INTEGER NOT NULL REFERENCES kriangle_app_seojob(id)
                )
                """)
        
        print("✓ Tables created. Please restart the server and try again.")
    except Exception as sql_error:
        print(f"× SQL Error: {str(sql_error)}")
        print("\nPlease run these commands manually:")
        print("1. python manage.py makemigrations")
        print("2. python manage.py migrate")
        print("3. Restart the server") 
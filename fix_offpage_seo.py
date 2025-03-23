import os
import sys
import sqlite3
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.contrib.auth.models import User

def create_tables():
    """Create required tables for offpage SEO functionality"""
    print("Checking and fixing database tables...")
    
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check and create SEOJob table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_seojob'")
        if not cursor.fetchone():
            print("Creating SEOJob table...")
            cursor.execute("""
            CREATE TABLE kriangle_app_seojob (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url VARCHAR(200) NOT NULL,
                website_url VARCHAR(200) DEFAULT '' NOT NULL,
                keywords TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                status VARCHAR(50) DEFAULT 'pending' NOT NULL,
                user_id INTEGER REFERENCES auth_user(id)
            )
            """)
            print("✓ SEOJob table created")
        else:
            # Make sure user_id column exists
            cursor.execute("PRAGMA table_info(kriangle_app_seojob)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'user_id' not in column_names:
                print("Adding user_id column to SEOJob table...")
                cursor.execute("ALTER TABLE kriangle_app_seojob ADD COLUMN user_id INTEGER REFERENCES auth_user(id)")
                print("✓ user_id column added to SEOJob table")
        
        # Check and create SEOResult table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_seoresult'")
        if not cursor.fetchone():
            print("Creating SEOResult table...")
            cursor.execute("""
            CREATE TABLE kriangle_app_seoresult (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                step VARCHAR(100) NOT NULL,
                result_data TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'success' NOT NULL,
                created_at DATETIME NOT NULL,
                job_id INTEGER NOT NULL REFERENCES kriangle_app_seojob(id)
            )
            """)
            print("✓ SEOResult table created")
        
        # Check and create OffPageAction table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_offpageaction'")
        if not cursor.fetchone():
            print("Creating OffPageAction table...")
            cursor.execute("""
            CREATE TABLE kriangle_app_offpageaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform VARCHAR(100) NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                url VARCHAR(200) NULL,
                status VARCHAR(20) DEFAULT 'pending' NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                job_id INTEGER NOT NULL REFERENCES kriangle_app_seojob(id)
            )
            """)
            print("✓ OffPageAction table created")
        
        # Check and create BlogCategory table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_blogcategory'")
        if not cursor.fetchone():
            print("Creating BlogCategory table...")
            cursor.execute("""
            CREATE TABLE kriangle_app_blogcategory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(50) UNIQUE NOT NULL,
                description TEXT NOT NULL
            )
            """)
            print("✓ BlogCategory table created")
            
            # Insert a default category
            cursor.execute("""
            INSERT INTO kriangle_app_blogcategory (name, slug, description)
            VALUES ('General', 'general', 'General blog posts')
            """)
            print("✓ Default blog category added")
        
        # Commit all changes
        conn.commit()
        
        print("✓ All database tables verified and fixed")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"× Database error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def create_test_data():
    """Create test data for demoing the offpage SEO functionality"""
    
    try:
        from kriangle_app.models import SEOJob, SEOResult, OffPageAction, BlogCategory
        
        # Make sure we have at least one user
        if not User.objects.exists():
            print("Creating a default admin user...")
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            print("✓ Default admin user created (username: admin, password: admin)")
        
        user = User.objects.first()
        
        # Create a test SEO job if none exists
        if not SEOJob.objects.filter(user=user).exists():
            print("Creating a test SEO job...")
            job = SEOJob.objects.create(
                user=user,
                url='https://example.com',
                website_url='https://example.com',
                keywords='seo, marketing, web development',
                status='completed'
            )
            
            # Create some results for this job
            SEOResult.objects.create(
                job=job,
                step='Analysis',
                result_data='Website analysis completed successfully',
                status='success'
            )
            
            # Create some offpage actions for this job
            OffPageAction.objects.create(
                job=job,
                platform='Directory',
                action_type='Submission',
                url='https://directory.example.com',
                status='completed'
            )
            
            print("✓ Test data created successfully")
        else:
            print("✓ Test data already exists")
        
        return True
    except Exception as e:
        print(f"× Error creating test data: {str(e)}")
        return False

if __name__ == "__main__":
    print("Off-Page SEO Fix Script - Kriangle")
    print("="*40)
    
    try:
        # First run migrations
        print("Running migrations...")
        call_command('makemigrations', 'kriangle_app', '--noinput')
        call_command('migrate', '--noinput')
        print("✓ Migrations completed")
        
        # Then create/fix tables
        if create_tables():
            # Finally create test data
            create_test_data()
            print("\n✓ Off-Page SEO functionality fixed!")
        else:
            print("\n× Database tables could not be fully fixed.")
    except Exception as e:
        print(f"\n× Error: {str(e)}")
    
    print("\nYou can now restart your Django server and try the Off-Page SEO feature.")
    print("\nPress Enter to continue...")
    input() 
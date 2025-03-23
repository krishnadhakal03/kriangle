import os
import sys
import sqlite3
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from kriangle_app.models import SEOJob, SEOResult, BlogCategory, Tag, BlogPost, OldBlogPost, OffPageSEOAction, Contact, SEOReport

def run_migrations():
    """Run migrations to create missing tables"""
    print("Running migrations to fix database structure...")
    try:
        call_command('makemigrations', 'kriangle_app', '--noinput')
        call_command('migrate', '--noinput')
        print("✓ Migrations applied successfully")
    except Exception as e:
        print(f"× Error applying migrations: {str(e)}")
        return False
    return True

def fix_database_tables():
    """Check and fix critical database tables manually if needed"""
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
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
        
        # Check and create Tag table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_tag'")
        if not cursor.fetchone():
            print("Creating Tag table...")
            cursor.execute("""
            CREATE TABLE kriangle_app_tag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                slug VARCHAR(50) UNIQUE NOT NULL
            )
            """)
        
        # Check and create BlogPost_tags table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kriangle_app_blogpost_tags'")
        if not cursor.fetchone():
            print("Creating BlogPost_tags table...")
            cursor.execute("""
            CREATE TABLE kriangle_app_blogpost_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blogpost_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (blogpost_id) REFERENCES kriangle_app_blogpost (id),
                FOREIGN KEY (tag_id) REFERENCES kriangle_app_tag (id),
                UNIQUE (blogpost_id, tag_id)
            )
            """)
        
        # Check if the user_id column exists in SEOJob table
        cursor.execute("PRAGMA table_info(kriangle_app_seojob)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Adding user_id column to SEOJob table...")
            cursor.execute("ALTER TABLE kriangle_app_seojob ADD COLUMN user_id INTEGER REFERENCES auth_user(id)")
        
        # Check if the summary column exists in BlogPost table
        cursor.execute("PRAGMA table_info(kriangle_app_blogpost)")
        blog_columns = [column[1] for column in cursor.fetchall()]
        
        if 'summary' not in blog_columns and 'id' in blog_columns:
            print("Adding summary column to BlogPost table...")
            cursor.execute("ALTER TABLE kriangle_app_blogpost ADD COLUMN summary TEXT NOT NULL DEFAULT 'Blog post summary'")
        
        conn.commit()
        
        # Add sample data for testing
        try:
            # Create a default blog category if none exists
            if not BlogCategory.objects.exists():
                print("Creating default blog category...")
                BlogCategory.objects.create(name="General", slug="general", description="General blog posts")
            
            print("✓ Database tables fixed successfully")
            return True
        except Exception as e:
            print(f"× Error adding sample data: {str(e)}")
            # Continue anyways as tables are created
            return True
            
    except Exception as e:
        print(f"× Database error: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Database Fix Script - Kriangle")
    print("="*40)
    
    if run_migrations():
        if fix_database_tables():
            print("\n✓ Database repair complete!")
            print("\nYou can now restart your Django server.")
        else:
            print("\n× Some manual fixes failed, but migrations completed.")
            print("\nRestart your Django server and report any continuing issues.")
    else:
        print("\n× Failed to apply migrations.")
        print("\nTry running these commands manually:")
        print("1. python manage.py makemigrations kriangle_app")
        print("2. python manage.py migrate")
    
    print("\nPress Enter to continue...")
    input() 
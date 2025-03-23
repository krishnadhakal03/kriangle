import os
import django
from django.conf import settings
from django.db import migrations
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')
django.setup()

# Create a new migration file for kriangle_app
migrations_dir = 'kriangle_app/migrations'
os.makedirs(migrations_dir, exist_ok=True)

# Create a new migration file
migration_number = 1
while os.path.exists(f"{migrations_dir}/{migration_number:04d}_add_slug_field.py"):
    migration_number += 1

migration_content = f'''# Generated manually to fix missing slug field
from django.db import migrations, models
from django.utils.text import slugify

def create_slugs(apps, schema_editor):
    """Create slugs for existing posts"""
    BlogPost = apps.get_model('kriangle_app', 'BlogPost')
    for post in BlogPost.objects.all():
        if not post.slug:
            post.slug = slugify(post.title)
            post.save()

class Migration(migrations.Migration):

    dependencies = [
        ('kriangle_app', '{migration_number-1:04d}_auto'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.RunPython(create_slugs),
    ]
'''

# Check if there are existing migrations to determine dependencies
migrations_files = os.listdir(migrations_dir)
migration_files = [f for f in migrations_files if f.endswith('.py') and f != '__init__.py']

if not migration_files:
    # If no migrations exist, create an initial migration
    migration_content = migration_content.replace(
        f"('kriangle_app', '{migration_number-1:04d}_auto')",
        "('kriangle_app', '__first__')"
    )

# Write the migration file
with open(f"{migrations_dir}/{migration_number:04d}_add_slug_field.py", 'w') as f:
    f.write(migration_content)

print(f"Created migration file: {migrations_dir}/{migration_number:04d}_add_slug_field.py")
print("Now run: python manage.py migrate kriangle_app") 
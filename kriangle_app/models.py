from django.db import models

# Create your models here.
class SEOJob(models.Model):
    url = models.URLField()
    keywords = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class SEOResult(models.Model):
    job = models.ForeignKey(SEOJob, on_delete=models.CASCADE)
    step = models.CharField(max_length=100)
    result_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)  # Add phone number field
    address = models.TextField()  # Add address field
    message = models.TextField()

    def __str__(self):
        return self.name
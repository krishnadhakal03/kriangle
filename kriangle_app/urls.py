from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('shop/', views.shop, name='shop'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact, name='contact'),
    path('scan_seo/', views.scan_seo, name='scan_seo'),
    path('offpageseo/', views.offpage_seo, name='offpageseo'),
    path("seo-results/<int:job_id>/", views.seo_results, name="seo_results"),
    path('thank_you/', views.thank_you, name='thank_you'),
]
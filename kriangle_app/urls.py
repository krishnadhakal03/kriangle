from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('shop/', views.shop, name='shop'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('blog/category/<slug:category_slug>/', views.blog_category, name='blog_category'),
    path('blog/tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),
    path('scan_seo/', views.scan_seo, name='scan_seo'),
    path('offpageseo/', views.offpage_view, name='offpageseo'),
    path("seo-results/<int:job_id>/", views.seo_results, name="seo_results"),
    path('generate-seo-pdf/', views.generate_seo_pdf, name='generate_seo_pdf'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('test-celery/', views.test_celery, name='test_celery'),
    
    # SEO files
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    
    # Off-Page SEO Automation URLs
    path('offpage/', views.offpage_view, name='offpage'),
    path('offpage-automation/', views.offpage_automation_view, name='offpage_automation'),
    path('offpage/generate-content/', views.generate_content, name='generate_content'),
    path('offpage/tasks/<int:task_id>/submit/', views.submit_task, name='submit_task'),
    path('offpage/tasks/', views.get_tasks, name='get_tasks'),
    path('offpage/tasks/<int:task_id>/', views.get_task_detail, name='get_task_detail'),
    
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='autoseo/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='autoseo/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='autoseo/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='autoseo/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='autoseo/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='autoseo/password_reset_complete.html'), name='password_reset_complete'),
]
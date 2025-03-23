import os
import sys
import django
import requests
import datetime
import time
import json
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init()

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from kriangle_app.models import SEOJob, SEOResult, OffPageSEOAction, BlogPost, BlogCategory

class KriangleRegressionTest:
    """
    Comprehensive regression testing module for Kriangle application.
    Tests all major features to ensure they are working correctly.
    """
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {
            "success": 0,
            "failure": 0,
            "total": 0,
            "features": {}
        }
        self.session = requests.Session()
        
        # Set up test data
        self.test_username = "test_admin"
        self.test_password = "test_password123"
        self.test_email = "test@kriangle.com"
        self.test_site = "https://example.com"
        self.test_keywords = "seo, testing, django"
        
        # Test user for login tests
        try:
            # Check if test user exists, create if not
            if not User.objects.filter(username=self.test_username).exists():
                User.objects.create_superuser(
                    username=self.test_username,
                    email=self.test_email,
                    password=self.test_password
                )
                print(f"{Fore.GREEN}Created test user: {self.test_username}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Test user already exists: {self.test_username}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to create test user: {str(e)}{Style.RESET_ALL}")
    
    def log_success(self, feature, message):
        """Log a successful test"""
        self.test_results["success"] += 1
        self.test_results["total"] += 1
        
        if feature not in self.test_results["features"]:
            self.test_results["features"][feature] = {"success": 0, "failure": 0}
            
        self.test_results["features"][feature]["success"] += 1
        print(f"{Fore.GREEN}✓ {feature}: {message}{Style.RESET_ALL}")
    
    def log_failure(self, feature, message, error=None):
        """Log a failed test"""
        self.test_results["failure"] += 1
        self.test_results["total"] += 1
        
        if feature not in self.test_results["features"]:
            self.test_results["features"][feature] = {"success": 0, "failure": 0}
            
        self.test_results["features"][feature]["failure"] += 1
        
        error_msg = f" - Error: {str(error)}" if error else ""
        print(f"{Fore.RED}✗ {feature}: {message}{error_msg}{Style.RESET_ALL}")
    
    def test_server_status(self):
        """Test if the server is running"""
        feature = "Server Status"
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_success(feature, "Server is running")
                return True
            else:
                self.log_failure(feature, f"Server returned status code {response.status_code}")
                return False
        except Exception as e:
            self.log_failure(feature, "Failed to connect to server", e)
            return False
    
    def test_login_functionality(self):
        """Test user login functionality"""
        feature = "User Authentication"
        
        try:
            # First, get the CSRF token
            response = self.session.get(f"{self.base_url}/admin/login/")
            
            if response.status_code != 200:
                self.log_failure(feature, "Failed to load admin login page")
                return False
                
            # Extract CSRF token
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrftoken' in line and 'value' in line:
                    # Basic extraction, a proper implementation would use BeautifulSoup
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    csrf_token = line[start:end]
                    break
            
            if not csrf_token:
                self.log_failure(feature, "Failed to extract CSRF token")
                return False
            
            # Attempt login
            login_data = {
                'username': self.test_username,
                'password': self.test_password,
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/login/", 
                data=login_data,
                headers={'Referer': f"{self.base_url}/admin/login/"}
            )
            
            if response.status_code == 200 and "Log in | Django site admin" not in response.text:
                self.log_success(feature, "Admin login successful")
                return True
            else:
                self.log_failure(feature, "Admin login failed")
                return False
                
        except Exception as e:
            self.log_failure(feature, "Login test failed with exception", e)
            return False
    
    def test_on_page_seo(self):
        """Test on-page SEO scan functionality"""
        feature = "On-page SEO Scan"
        
        try:
            # Get CSRF token
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code != 200:
                self.log_failure(feature, "Failed to load home page")
                return False
            
            # Extract CSRF token (basic method)
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value' in line:
                    # Basic extraction
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    csrf_token = line[start:end]
                    break
            
            if not csrf_token:
                # If not found in HTML, try from cookies
                csrf_token = self.session.cookies.get('csrftoken')
            
            if not csrf_token:
                self.log_failure(feature, "Failed to extract CSRF token")
                return False
                
            # Submit SEO scan
            scan_data = {
                'website_url': self.test_site,
                'keywords': self.test_keywords,
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = self.session.post(
                f"{self.base_url}/scan-seo/", 
                data=scan_data,
                headers={'Referer': f"{self.base_url}/"}
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if 'report' in result:
                        self.log_success(feature, "On-page SEO scan successful")
                        return True
                    else:
                        self.log_failure(feature, "On-page SEO scan returned invalid data")
                        return False
                except json.JSONDecodeError:
                    self.log_failure(feature, "On-page SEO scan did not return valid JSON")
                    return False
            else:
                self.log_failure(feature, f"On-page SEO scan failed with status code {response.status_code}")
                return False
                
        except Exception as e:
            self.log_failure(feature, "On-page SEO scan test failed with exception", e)
            return False
    
    def test_off_page_seo(self):
        """Test off-page SEO functionality"""
        feature = "Off-page SEO"
        
        try:
            # Get CSRF token from off-page SEO page
            response = self.session.get(f"{self.base_url}/offpage-seo/")
            
            if response.status_code != 200:
                self.log_failure(feature, "Failed to load off-page SEO page")
                return False
            
            # Extract CSRF token
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value' in line:
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    csrf_token = line[start:end]
                    break
            
            if not csrf_token:
                # If not found in HTML, try from cookies
                csrf_token = self.session.cookies.get('csrftoken')
            
            if not csrf_token:
                self.log_failure(feature, "Failed to extract CSRF token")
                return False
                
            # Submit off-page SEO job
            data = {
                'website': self.test_site,
                'keywords': self.test_keywords,
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = self.session.post(
                f"{self.base_url}/offpageseo/", 
                data=data,
                headers={'Referer': f"{self.base_url}/offpage-seo/"},
                allow_redirects=True
            )
            
            # Check database directly
            try:
                # Look for a job with our test site
                job = SEOJob.objects.filter(url=self.test_site).order_by('-created_at').first()
                
                if job:
                    # Check if results were created
                    results = SEOResult.objects.filter(job=job).count()
                    actions = OffPageSEOAction.objects.filter(job=job).count()
                    
                    if results > 0 and actions > 0:
                        self.log_success(feature, f"Off-page SEO job created with {results} results and {actions} actions")
                        return True
                    else:
                        self.log_failure(feature, f"Off-page SEO job created but missing results or actions")
                        return False
                else:
                    self.log_failure(feature, "Off-page SEO job not found in database")
                    return False
            except Exception as db_error:
                self.log_failure(feature, "Failed to check database for off-page SEO job", db_error)
                return False
                
        except Exception as e:
            self.log_failure(feature, "Off-page SEO test failed with exception", e)
            return False
    
    def test_blog_functionality(self):
        """Test blog functionality"""
        feature = "Blog System"
        
        try:
            # Test accessing blog page
            response = self.session.get(f"{self.base_url}/blog/")
            
            if response.status_code != 200:
                self.log_failure(feature, f"Failed to load blog page: status {response.status_code}")
                return False
                
            # Check if blog posts are being displayed
            if "No blog posts found" in response.text:
                # Create a test blog post if none exist
                try:
                    # Create category if needed
                    category, created = BlogCategory.objects.get_or_create(
                        name="Test Category",
                        defaults={
                            'slug': 'test-category',
                            'description': 'Category for regression testing'
                        }
                    )
                    
                    # Create a test post
                    test_post = BlogPost.objects.create(
                        title="Test Blog Post",
                        slug="test-blog-post",
                        content="This is a test blog post created by the regression testing system.",
                        summary="Test post summary",
                        category=category,
                        is_published=True,
                        view_count=0
                    )
                    
                    self.log_success(feature, "Created test blog post")
                    
                    # Test viewing the post
                    response = self.session.get(f"{self.base_url}/blog/post/{test_post.slug}/")
                    
                    if response.status_code == 200 and "Test Blog Post" in response.text:
                        self.log_success(feature, "Test blog post is viewable")
                        return True
                    else:
                        self.log_failure(feature, "Created test blog post but unable to view it")
                        return False
                        
                except Exception as post_error:
                    self.log_failure(feature, "Failed to create test blog post", post_error)
                    return False
            else:
                # Check if we can view an existing post
                try:
                    # Get an existing post
                    post = BlogPost.objects.filter(is_published=True).first()
                    
                    if post:
                        response = self.session.get(f"{self.base_url}/blog/post/{post.slug}/")
                        
                        if response.status_code == 200 and post.title in response.text:
                            self.log_success(feature, "Existing blog post is viewable")
                            return True
                        else:
                            self.log_failure(feature, "Failed to view existing blog post")
                            return False
                    else:
                        self.log_failure(feature, "No published blog posts found despite blog page not showing 'No posts' message")
                        return False
                        
                except Exception as view_error:
                    self.log_failure(feature, "Failed to view existing blog post", view_error)
                    return False
                    
        except Exception as e:
            self.log_failure(feature, "Blog functionality test failed with exception", e)
            return False
    
    def test_contact_form(self):
        """Test contact form functionality"""
        feature = "Contact Form"
        
        try:
            # Get contact page
            response = self.session.get(f"{self.base_url}/contact/")
            
            if response.status_code != 200:
                self.log_failure(feature, f"Failed to load contact page: status {response.status_code}")
                return False
                
            # Extract CSRF token
            csrf_token = None
            for line in response.text.split('\n'):
                if 'csrfmiddlewaretoken' in line and 'value' in line:
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    csrf_token = line[start:end]
                    break
            
            if not csrf_token:
                # If not found in HTML, try from cookies
                csrf_token = self.session.cookies.get('csrftoken')
            
            if not csrf_token:
                self.log_failure(feature, "Failed to extract CSRF token")
                return False
                
            # Submit contact form
            contact_data = {
                'name': 'Regression Test User',
                'email': 'regression@test.com',
                'phone_number': '1234567890',
                'address': 'Test Address',
                'message': 'This is a test message from the regression testing system.',
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = self.session.post(
                f"{self.base_url}/contact/", 
                data=contact_data,
                headers={'Referer': f"{self.base_url}/contact/"},
                allow_redirects=True
            )
            
            # Check if redirected to thank you page
            if response.status_code == 200 and "thank you" in response.text.lower():
                self.log_success(feature, "Contact form submitted successfully")
                return True
            else:
                self.log_failure(feature, f"Contact form submission failed: status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_failure(feature, "Contact form test failed with exception", e)
            return False
    
    def run_all_tests(self):
        """Run all regression tests"""
        print(f"\n{Fore.CYAN}========== KRIANGLE REGRESSION TEST SUITE =========={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")
        
        # Run tests only if server is running
        if self.test_server_status():
            self.test_login_functionality()
            self.test_on_page_seo()
            self.test_off_page_seo()
            self.test_blog_functionality()
            self.test_contact_form()
        else:
            print(f"{Fore.RED}Server is not running, skipping remaining tests{Style.RESET_ALL}")
        
        self.generate_report()
    
    def generate_report(self):
        """Generate and display test report"""
        total = self.test_results["total"]
        success = self.test_results["success"]
        failure = self.test_results["failure"]
        
        success_rate = (success / total * 100) if total > 0 else 0
        
        print(f"\n{Fore.CYAN}========== TEST REPORT =========={Style.RESET_ALL}")
        print(f"Total Tests: {total}")
        print(f"Successful: {Fore.GREEN}{success}{Style.RESET_ALL}")
        print(f"Failed: {Fore.RED}{failure}{Style.RESET_ALL}")
        print(f"Success Rate: {Fore.YELLOW}{success_rate:.2f}%{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Feature Summary:{Style.RESET_ALL}")
        for feature, results in self.test_results["features"].items():
            feature_success = results["success"]
            feature_failure = results["failure"]
            
            if feature_failure > 0:
                status = f"{Fore.RED}FAILING{Style.RESET_ALL}"
            elif feature_success > 0:
                status = f"{Fore.GREEN}PASSING{Style.RESET_ALL}"
            else:
                status = f"{Fore.YELLOW}NO TESTS{Style.RESET_ALL}"
                
            print(f"- {feature}: {status} ({feature_success} passed, {feature_failure} failed)")
        
        # Save report to file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"regression_report_{timestamp}.txt"
        
        with open(report_file, "w") as f:
            f.write("KRIANGLE REGRESSION TEST REPORT\n")
            f.write(f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Tests: {total}\n")
            f.write(f"Successful: {success}\n")
            f.write(f"Failed: {failure}\n")
            f.write(f"Success Rate: {success_rate:.2f}%\n\n")
            
            f.write("Feature Summary:\n")
            for feature, results in self.test_results["features"].items():
                feature_success = results["success"]
                feature_failure = results["failure"]
                
                status = "FAILING" if feature_failure > 0 else "PASSING" if feature_success > 0 else "NO TESTS"
                f.write(f"- {feature}: {status} ({feature_success} passed, {feature_failure} failed)\n")
        
        print(f"\n{Fore.CYAN}Report saved to: {report_file}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}========== END OF REPORT =========={Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        tester = KriangleRegressionTest()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test suite interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Test suite encountered an error: {str(e)}{Style.RESET_ALL}") 
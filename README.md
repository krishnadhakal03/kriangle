# Kriangle - Website Development & SEO Services

A Django-based web application that offers website development, SEO optimization services, and digital marketing solutions for small businesses.

## Project Overview

Kriangle is a web platform designed to help small businesses improve their online presence through:

1. SEO Analysis & Optimization
2. Automated SEO Improvements
3. Website Development Services
4. Digital Marketing Solutions

The application includes a modern, responsive frontend interface built with HTML, CSS, and JavaScript, powered by a Django backend.

## Features

- **SEO Analysis**: Scans websites for SEO issues and provides detailed reports
- **Off-Page SEO Automation**: Generates AI content, posts to WordPress, and shares on social media
- **Contact Form**: Integrated contact form with email notifications
- **Modern Web Interface**: Responsive Bootstrap-based frontend

## Technology Stack

- **Backend**: Python Django 5.1.7
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI Integration**: OpenAI API for content generation
- **Background Jobs**: Celery with Redis for asynchronous tasks
- **APIs Integration**: 
  - WordPress API for content publishing
  - Twitter API for social sharing
  - NLTK for natural language processing

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/kriangle-master.git
cd kriangle-master
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set up environment variables (for production):
```
# Create a .env file with the following variables
SECRET_KEY=your_secret_key
DEBUG=False
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
OPENAI_API_KEY=your_openai_api_key
```

5. Run migrations:
```
python manage.py migrate
```

6. Create a superuser:
```
python manage.py createsuperuser
```

7. Run the development server:
```
python manage.py runserver
```

## Project Structure

- `kriangle/` - Main Django project configuration
- `kriangle_app/` - Main application with all functionality
  - `models.py` - Database models (SEOJob, SEOResult, Contact)
  - `views.py` - View functions for all pages and functionality
  - `tasks.py` - Background tasks for SEO automation
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and image files

## Usage

1. Access the admin panel at `/admin/` to manage site content
2. Navigate to the SEO analysis tool at `/scan_seo/`
3. Use the Off-page SEO automation at `/offpageseo/`
4. Contact form available at `/contact/`

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact krishna.dhakal03@gmail.com. 

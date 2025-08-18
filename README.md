# WiseCart - Smart Shopping Comparison Platform

WiseCart is a comprehensive e-commerce comparison platform that helps users find the best prices and deals across multiple online stores. The platform features product comparison, shop reviews, user authentication, and automated web scraping to keep product information up-to-date.

## 🚀 Features

- **Product Comparison**: Compare products across multiple stores
- **Shop Reviews & Ratings**: User-generated reviews and ratings for online stores
- **Smart Search**: Advanced search functionality with filters
- **User Authentication**: Secure user registration, login, and profile management
- **Bookmarking**: Save favorite products for later
- **Web Scraping**: Automated data collection from various e-commerce sites
- **Responsive Design**: Mobile-friendly interface
- **Admin Panel**: Comprehensive Django admin interface

## 🏗️ Project Structure

```
wisecart/
├── comparison/          # Product comparison functionality
├── products/           # Product management and display
├── search/            # Search functionality and results
├── shops/             # Shop management and reviews
├── users/             # User authentication and profiles
├── scraper/           # Web scraping with Scrapy
├── static/            # CSS, JavaScript, and images
├── templates/         # HTML templates
├── media/             # User-uploaded files
└── wisecart/          # Main Django project settings
```

## 🛠️ Prerequisites

Before setting up WiseCart, ensure you have the following installed:

- **Python 3.8+**
- **PostgreSQL 12+**
- **pip** (Python package installer)
- **Git** (for cloning the repository)

## 📋 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/lazy-sharaf/WiseCart.git
cd WiseCart
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql postgresql-server postgresql-contrib
```

**macOS (using Homebrew):**
```bash
brew install postgresql
```

#### Create Database and User

```bash
# Access PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE DATABASE wisecart_db;
CREATE USER wisecart_team WITH PASSWORD 'wise_people';
GRANT ALL PRIVILEGES ON DATABASE wisecart_db TO wisecart_team;
ALTER USER wisecart_team CREATEDB;
\q
```

### 5. Environment Configuration

The project comes with pre-configured settings, but you may want to customize:

- **Database credentials** in `wisecart/settings.py`
- **Email settings** for password reset functionality
- **Secret key** for production deployment

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

## 🚀 Running the Application

### Development Server

```bash
# Start Django development server
python manage.py runserver

# The application will be available at:
# http://127.0.0.1:8000/
```

### Web Scraping

The project includes Scrapy spiders for automated data collection:

```bash
# Navigate to scraper directory
cd scraper

# Run a specific spider
scrapy crawl startech
scrapy crawl techland
scrapy crawl riointernational
scrapy crawl potakait
scrapy crawl sumashtech
scrapy crawl ucc

# Run all spiders
scrapy list | xargs -n 1 scrapy crawl
```

**Available Spiders:**
- `startech` - Scrapes Startech.com.bd
- `techland` - Scrapes Techland.com.bd
- `riointernational` - Scrapes Rio International
- `potakait` - Scrapes Potaka IT
- `sumashtech` - Scrapes Sumash Tech
- `ucc` - Scrapes UCC

## 🔧 Configuration

### Database Settings

The default database configuration is in `wisecart/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "wisecart_db",
        "USER": "wisecart_team",
        "PASSWORD": "wise_people",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### Email Configuration

The project supports multiple email backends. Configure your preferred option in `wisecart/settings.py`:

- Gmail SMTP
- Outlook/Hotmail SMTP
- Yahoo SMTP
- Custom SMTP Server
- SendGrid
- Mailgun

### Static and Media Files

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

## 📱 Usage

### For Users

1. **Browse Products**: View featured products and search for specific items
2. **Compare Prices**: Use the comparison tool to compare products across stores
3. **Read Reviews**: Check shop reviews and ratings before making purchases
4. **Bookmark Items**: Save interesting products for later
5. **User Account**: Register, login, and manage your profile

### For Administrators

1. **Admin Panel**: Access `/admin/` with superuser credentials
2. **Manage Content**: Add/edit products, shops, and user accounts
3. **Monitor Scraping**: Check scraped data and manage spiders
4. **User Management**: Handle user registrations and issues

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test products
python manage.py test search
python manage.py test shops
python manage.py test users
python manage.py test comparison
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Move sensitive settings to environment variables
2. **Static Files**: Use a CDN or web server for static file serving
3. **Database**: Use production-grade PostgreSQL with proper backups
4. **Email**: Configure production email backend (SendGrid, Mailgun, etc.)
5. **Security**: Set `DEBUG = False` and configure `ALLOWED_HOSTS`
6. **HTTPS**: Enable SSL/TLS certificates

### Using Gunicorn

```bash
pip install gunicorn
gunicorn wisecart.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker (Optional)

Create a `Dockerfile` and `docker-compose.yml` for containerized deployment.

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in settings.py
   - Ensure database and user exist

2. **Migration Errors**
   - Delete migration files and recreate them
   - Check for conflicting model changes

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATIC_URL` settings

4. **Scraping Issues**
   - Verify target websites are accessible
   - Check for changes in website structure
   - Review spider logs for errors

### Logs

Check Django logs and Scrapy logs for detailed error information:

```bash
# Django logs (if configured)
tail -f /var/log/django/wisecart.log

# Scrapy logs
tail -f scraper/logs/scrapy.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Updates

Keep the project updated:

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Django
pip install --upgrade django

# Check for security updates
pip list --outdated
```

---

**Happy Shopping with WiseCart! 🛒✨** 

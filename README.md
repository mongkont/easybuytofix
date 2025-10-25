# EasyBuyToFix

A Django-based e-commerce platform built with Django LTS 5.2.6, PostgreSQL, and Cloudflare R2 for media storage.

## 🚀 Features

- **Django LTS 5.2.6** - Latest Long Term Support version
- **PostgreSQL Database** - Robust and scalable database
- **Cloudflare R2 Storage** - Fast and cost-effective media storage
- **Thai Language Support** - Localized for Thai users
- **Environment-based Configuration** - Secure configuration management
- **Admin Panel** - Full Django admin interface

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6 (LTS)
- **Database**: PostgreSQL
- **Storage**: Cloudflare R2
- **Language**: Python 3.13
- **Environment**: Virtual Environment

## 📋 Prerequisites

- Python 3.13+
- PostgreSQL
- Cloudflare Account (for R2 storage)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mongkont/easybuytofix.git
cd easybuytofix
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=easybuytfix_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Timezone
TIME_ZONE=Asia/Bangkok
LANGUAGE_CODE=th

# Cloudflare R2 Settings
R2_ENABLED=True
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=your-bucket-name
R2_CUSTOM_DOMAIN=https://your-custom-domain.r2.dev
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Or use the provided script:

```bash
./run_server.sh
```

## 🌐 Access Points

- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
easybuytofix/
├── easybuytofix/          # Django project settings
│   ├── __init__.py
│   ├── settings.py        # Main settings file
│   ├── urls.py           # URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── R2_SETUP.md           # Cloudflare R2 setup guide
├── run_server.sh         # Server startup script
├── r2_test.py            # R2 connection test script
├── manage_r2.py          # R2 file management script
├── media/                # Local media files (when R2 disabled)
├── staticfiles/          # Static files
└── venv/                 # Virtual environment
```

## 🔧 Configuration

### Database Configuration

The project uses PostgreSQL by default. Make sure PostgreSQL is running and create a database:

```sql
CREATE DATABASE easybuytfix_db;
```

### Cloudflare R2 Setup

1. Create a Cloudflare account and R2 bucket
2. Generate API tokens with Object Read & Write permissions
3. Configure the R2 settings in `.env` file
4. Test the connection:

```bash
python r2_test.py
```

For detailed R2 setup instructions, see [R2_SETUP.md](R2_SETUP.md).

## 🛠️ Development Tools

### R2 Management

```bash
# Test R2 connection
python r2_test.py

# Show R2 configuration
python manage_r2.py info

# List files in R2
python manage_r2.py list

# Upload file to R2
python manage_r2.py upload local_file.txt remote_file.txt

# Delete file from R2
python manage_r2.py delete remote_file.txt

# Get file URL
python manage_r2.py url remote_file.txt
```

### Django Management

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Check system
python manage.py check
```

## 🌍 Localization

The project is configured for Thai users:

- **Language**: Thai (`th`)
- **Timezone**: Asia/Bangkok
- **Date Format**: Thai Buddhist Era (พ.ศ.)

## 🔒 Security

- Environment variables are used for sensitive configuration
- `.env` file is excluded from version control
- Django security settings are configured for development
- For production, update security settings in `settings.py`

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `DB_NAME` | Database name | `easybuytfix_db` |
| `DB_USER` | Database user | Required |
| `DB_PASSWORD` | Database password | Required |
| `R2_ENABLED` | Enable R2 storage | `False` |
| `R2_ACCESS_KEY_ID` | R2 access key | Required for R2 |
| `R2_SECRET_ACCESS_KEY` | R2 secret key | Required for R2 |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**มงคล ตั้งใจพิทักษ์ (Mongkont Tangjaipitak)**
- Email: mongkonjoe@gmail.com
- GitHub: [@mongkont](https://github.com/mongkont)

## 🙏 Acknowledgments

- Django team for the excellent framework
- Cloudflare for R2 storage service
- PostgreSQL community for the robust database
- Thai developer community for support and inspiration

## 📞 Support

If you have any questions or need help, please:

1. Check the [Issues](https://github.com/mongkont/easybuytofix/issues) page
2. Create a new issue if your problem isn't already reported
3. Contact the author at mongkonjoe@gmail.com

---

**Happy Coding! 🚀**

# SwiftDrop — Production Deployment Guide

> **Tagline:** Your Essentials. Delivered Smarter.  
> **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)  
> **Author & Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)  
> **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)

---

## 1. Prerequisites
* Python 3.10+ (Python 3.13 recommended)
* Git installed
* Production PostgreSQL or SQLite database
* A web hosting provider (Render, Railway, Linux VPS, or PythonAnywhere)

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` on your production host and configure the required settings:

```ini
DJANGO_SECRET_KEY=generate-a-strong-random-50-character-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,127.0.0.1
DATABASE_URL=postgres://user:password@host:5432/swiftdrop_db
EMAIL_HOST_USER=rifat5566123@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

---

## 3. Deployment on Cloud Platforms

### Option A: Render (Recommended PaaS)
1. Link your GitHub repository to Render as a **Web Service**.
2. Set Environment to **Python 3**.
3. **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput --settings=Nagaribashi_express.settings_production && python manage.py migrate --settings=Nagaribashi_express.settings_production
   ```
4. **Start Command:**
   ```bash
   gunicorn Nagaribashi_express.wsgi:application --bind 0.0.0.0:$PORT
   ```
5. Add the environment variables defined in Section 2.

### Option B: Linux VPS (Ubuntu 22.04 / 24.04 with Nginx + Gunicorn)
1. **Clone repository and setup virtual environment:**
   ```bash
   git clone https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp.git /var/www/swiftdrop
   cd /var/www/swiftdrop
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

2. **Run migrations and collect static assets:**
   ```bash
   python manage.py migrate --settings=Nagaribashi_express.settings_production
   python manage.py collectstatic --noinput --settings=Nagaribashi_express.settings_production
   python manage.py setup_data
   ```

3. **Configure Systemd Service (`/etc/systemd/system/swiftdrop.service`):**
   ```ini
   [Unit]
   Description=SwiftDrop Gunicorn Daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/swiftdrop
   ExecStart=/var/www/swiftdrop/.venv/bin/gunicorn \
       --access-logfile - \
       --workers 3 \
       --bind unix:/run/swiftdrop.sock \
       Nagaribashi_express.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

4. **Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/swiftdrop`):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           alias /var/www/swiftdrop/staticfiles/;
       }
       location /media/ {
           alias /var/www/swiftdrop/media/;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/run/swiftdrop.sock;
       }
   }
   ```

5. **Enable HTTPS with Let's Encrypt:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## 4. Post-Deployment Verification

1. Verify system status via `https://yourdomain.com/health/` or homepage.
2. Sign in using the admin account to confirm database migrations and operational dashboard.
3. Perform a test order checkout and verify invoice generation.

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*

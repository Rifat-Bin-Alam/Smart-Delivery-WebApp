# নাগরীবাসী এক্সপ্রেস (Nagaribashi Express)

একটি আধুনিক, বাংলা-প্রথম Django ওয়েবসাইট যা শহরের সবচেয়ে নির্ভরযোগ্য ডেলিভারি সেবা প্রদান করে। খাবার, ঔষধ, গ্যাস এবং আরও অনেক কিছু দ্রুত এবং নিরাপদে পৌঁছে দেওয়া।

## বৈশিষ্ট্য (Features)

### 🏠 গ্রাহক সেবা (Customer Services)
- **হোম পেজ**: স্বাগতম পেজ এবং সেবা পরিচিতি
- **লগইন/সাইনআপ**: নিরাপদ ব্যবহারকারী অ্যাকাউন্ট ব্যবস্থাপনা
- **অর্ডার প্লেসমেন্ট**: সহজ অর্ডার দেওয়ার সিস্টেম
- **পেমেন্ট**: নানান পেমেন্ট পদ্ধতি (ক্যাশ অন ডেলিভারি, bKash, Nagad, Rocket)
- **রিভিউ সিস্টেম**: ৫-তারকা রেটিং এবং মন্তব্য
- **অর্ডার ট্র্যাকিং**: রিয়েল-টাইম অর্ডার অবস্থা

### 👨‍💼 অ্যাডমিন প্যানেল (Admin Panel)
- **ড্যাশবোর্ড**: বিক্রয়, রাজস্ব, এবং ডেলিভারি পরিসংখ্যান
- **গ্রাহক ব্যবস্থাপনা**: গ্রাহক এবং ডেলিভারি এজেন্ট পরিচালনা
- **অর্ডার ব্যবস্থাপনা**: অর্ডার প্রক্রিয়াকরণ এবং অবস্থা আপডেট
- **পণ্য/সেবা ব্যবস্থাপনা**: পণ্য ক্যাটালগ পরিচালনা
- **ডেলিভারি ব্যবস্থাপনা**: ডেলিভারি এজেন্ট নির্ধারণ এবং ট্র্যাকিং
- **পেমেন্ট ব্যবস্থাপনা**: পেমেন্ট এবং রিফান্ড প্রক্রিয়াকরণ
- **রিভিউ মডারেশন**: রিভিউ অনুমোদন এবং রিপোর্ট ব্যবস্থাপনা

### 🚚 ডেলিভারি সিস্টেম (Delivery System)
- **ডেলিভারি এজেন্ট অ্যাপ**: এজেন্টদের জন্য বিশেষ ইন্টারফেস
- **লোকেশন ট্র্যাকিং**: রিয়েল-টাইম অবস্থান আপডেট
- **অর্ডার অ্যাসাইনমেন্ট**: স্বয়ংক্রিয় এজেন্ট নির্ধারণ
- **ডেলিভারি এলাকা**: বিভিন্ন এলাকার জন্য ফি এবং সময় নির্ধারণ

## প্রযুক্তি স্ট্যাক (Technology Stack)

- **Backend**: Django 5.2.6
- **Database**: SQLite (Development), PostgreSQL/MySQL (Production)
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Fonts**: Noto Sans Bengali (বাংলা ফন্ট)
- **Icons**: Font Awesome 6.4
- **Payment**: bKash, Nagad, Rocket integration ready
- **Maps**: Google Maps API ready
- **SMS/Email**: Twilio, Django Email ready

## ইনস্টলেশন (Installation)

### ১. প্রজেক্ট ক্লোন করুন
```bash
git clone <repository-url>
cd Nagaribashi_express
```

### ২. ভার্চুয়াল এনভায়রনমেন্ট তৈরি করুন
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### ৩. প্রয়োজনীয় প্যাকেজ ইনস্টল করুন
```bash
pip install -r requirements.txt
```

### ৪. ডেটাবেস মাইগ্রেশন চালান
```bash
python manage.py makemigrations
python manage.py migrate
```

### ৫. সুপারইউজার তৈরি করুন
```bash
python manage.py createsuperuser
```

### ৬. স্ট্যাটিক ফাইল সংগ্রহ করুন
```bash
python manage.py collectstatic
```

### ৭. সার্ভার চালু করুন
```bash
python manage.py runserver
```

## কনফিগারেশন (Configuration)

### পরিবেশ পরিবর্তনশীল (Environment Variables)
`.env` ফাইল তৈরি করুন:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### ডেটাবেস কনফিগারেশন
`settings.py` এ ডেটাবেস সেটিংস:
```python
# SQLite (Development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL (Production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nagaribashi_express',
        'USER': 'your-username',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## ব্যবহারকারী ধরন (User Types)

### ১. গ্রাহক (Customer)
- অর্ডার দেওয়া
- পেমেন্ট করা
- রিভিউ দেওয়া
- অর্ডার ট্র্যাক করা

### ২. ডেলিভারি এজেন্ট (Delivery Agent)
- অর্ডার গ্রহণ
- অবস্থান আপডেট
- ডেলিভারি সম্পন্ন
- রেটিং পাওয়া

### ৩. অ্যাডমিন (Admin)
- সব ব্যবস্থাপনা
- রিপোর্ট দেখা
- সিস্টেম কনফিগার

## API এন্ডপয়েন্ট (API Endpoints)

### গ্রাহক API
- `GET /` - হোম পেজ
- `GET /orders/` - অর্ডার তালিকা
- `POST /orders/create/` - নতুন অর্ডার
- `GET /orders/{id}/track/` - অর্ডার ট্র্যাক
- `POST /payments/create/` - পেমেন্ট
- `GET /reviews/` - রিভিউ তালিকা
- `POST /reviews/create/` - রিভিউ তৈরি

### অ্যাডমিন API
- `GET /admin-dashboard/` - অ্যাডমিন ড্যাশবোর্ড
- `GET /orders/admin/` - অ্যাডমিন অর্ডার তালিকা
- `POST /delivery/assign/` - ডেলিভারি এজেন্ট নির্ধারণ
- `GET /analytics/` - বিশ্লেষণ রিপোর্ট

## ডেটাবেস মডেল (Database Models)

### Users App
- `User` - কাস্টম ইউজার মডেল
- `CustomerProfile` - গ্রাহক প্রোফাইল
- `DeliveryAgentProfile` - ডেলিভারি এজেন্ট প্রোফাইল

### Orders App
- `ProductService` - পণ্য/সেবা
- `Order` - অর্ডার
- `OrderItem` - অর্ডার আইটেম
- `OrderStatusHistory` - অর্ডার অবস্থা ইতিহাস

### Delivery App
- `DeliveryAssignment` - ডেলিভারি নির্ধারণ
- `DeliveryStatus` - ডেলিভারি অবস্থা
- `DeliveryArea` - ডেলিভারি এলাকা
- `DeliveryAgentLocation` - এজেন্ট অবস্থান
- `DeliveryRating` - ডেলিভারি রেটিং

### Payments App
- `Payment` - পেমেন্ট
- `PaymentMethod` - পেমেন্ট পদ্ধতি
- `PaymentTransaction` - পেমেন্ট লেনদেন
- `Refund` - রিফান্ড

### Reviews App
- `Review` - রিভিউ
- `ReviewImage` - রিভিউ ছবি
- `ReviewHelpful` - সহায়ক ভোট
- `ReviewResponse` - রিভিউ উত্তর
- `ReviewReport` - রিভিউ রিপোর্ট

### Dashboard App
- `DashboardWidget` - ড্যাশবোর্ড উইজেট
- `AnalyticsData` - বিশ্লেষণ ডেটা
- `Notification` - নোটিফিকেশন
- `SystemLog` - সিস্টেম লগ
- `FAQ` - প্রায়শই জিজ্ঞাসিত প্রশ্ন

## সিকিউরিটি (Security)

- CSRF Protection
- XSS Protection
- SQL Injection Protection
- Password Validation
- User Authentication
- Permission-based Access Control

## ডেপ্লয়মেন্ট (Deployment)

### Heroku
```bash
# Procfile
web: gunicorn Nagaribashi_express.wsgi --log-file -

# Runtime
python-3.11.0
```

### DigitalOcean
```bash
# Nginx configuration
# Gunicorn service
# SSL certificate
```

### AWS
```bash
# EC2 instance
# RDS database
# S3 storage
# CloudFront CDN
```

## টেস্টিং (Testing)

```bash
# Unit tests
python manage.py test

# Coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

## কন্ট্রিবিউশন (Contribution)

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## লাইসেন্স (License)

This project is licensed under the MIT License.

## যোগাযোগ (Contact)

- **Email**: info@nagaribashiexpress.com
- **Phone**: +৮৮০ ১৭১১-২৩৪৫৬৭
- **Address**: ধানমন্ডি, ঢাকা-১২০৫

## সমর্থন (Support)

যদি আপনার কোন সমস্যা থাকে বা সাহায্যের প্রয়োজন হয়, দয়া করে আমাদের সাথে যোগাযোগ করুন।

---

**Made with ❤️ in Bangladesh**
#   S m a r t - D e l i v e r y - W e b A p p  
 #   S m a r t - D e l i v e r y - W e b A p p  
 
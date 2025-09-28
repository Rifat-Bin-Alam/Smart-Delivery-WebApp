# নগরবাসী এক্সপ্রেস - সমস্যা সমাধান গাইড

## সার্ভার চালু করার সমস্যা

### ১. PowerShell Execution Policy সমস্যা
যদি আপনি এই ত্রুটি পান:
```
File cannot be loaded because running scripts is disabled on this system
```

**সমাধান:**
```powershell
# PowerShell এ Administrator হিসেবে চালান
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ২. ভার্চুয়াল এনভায়রনমেন্ট সক্রিয় করা
```powershell
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### ৩. সার্ভার চালু করা
```bash
python manage.py runserver
```

## সাধারণ সমস্যা ও সমাধান

### সমস্যা ১: "no such table" ত্রুটি
**সমাধান:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### সমস্যা ২: "ModuleNotFoundError" ত্রুটি
**সমাধান:**
```bash
pip install -r requirements.txt
```

### সমস্যা ৩: স্ট্যাটিক ফাইল লোড হচ্ছে না
**সমাধান:**
```bash
python manage.py collectstatic
```

### সমস্যা ৪: টেমপ্লেট খুঁজে পাওয়া যাচ্ছে না
**সমাধান:**
- `templates` ফোল্ডার `manage.py` এর সাথে একই লেভেলে আছে কিনা চেক করুন
- `settings.py` এ `TEMPLATES` সেটিং সঠিক আছে কিনা চেক করুন

## সার্ভার টেস্ট করা

### ১. টেস্ট পেজ
```
http://127.0.0.1:8000/test/
```

### ২. হোম পেজ
```
http://127.0.0.1:8000/
```

### ৩. অ্যাডমিন প্যানেল
```
http://127.0.0.1:8000/admin/
```

## লগইন তথ্য

### অ্যাডমিন
- **ইউজারনেম:** admin
- **পাসওয়ার্ড:** admin123

### স্যাম্পল গ্রাহক
- **ইউজারনেম:** customer1
- **পাসওয়ার্ড:** customer123

## ডেটাবেস রিসেট করা

যদি ডেটাবেসে সমস্যা হয়:
```bash
# ডেটাবেস ফাইল মুছে দিন
del db.sqlite3

# নতুন মাইগ্রেশন করুন
python manage.py makemigrations
python manage.py migrate

# স্যাম্পল ডেটা তৈরি করুন
python manage.py setup_data
```

## পোর্ট পরিবর্তন করা

যদি 8000 পোর্ট ব্যবহৃত হয়:
```bash
python manage.py runserver 8080
```

## ব্রাউজার ক্যাশ ক্লিয়ার করা

যদি সাইট আপডেট না হয়:
- **Chrome:** Ctrl + Shift + R
- **Firefox:** Ctrl + F5
- **Edge:** Ctrl + Shift + R

## যোগাযোগ

যদি সমস্যা সমাধান না হয়:
1. Error message টি কপি করুন
2. `python manage.py check` চালান
3. `python manage.py runserver --verbosity=2` চালান

## সফল সেটআপের লক্ষণ

✅ সার্ভার চালু হয়েছে
✅ টেস্ট পেজ লোড হচ্ছে
✅ অ্যাডমিন প্যানেলে লগইন হচ্ছে
✅ হোম পেজ বাংলা ফন্টে দেখাচ্ছে
✅ স্যাম্পল পণ্য দেখা যাচ্ছে

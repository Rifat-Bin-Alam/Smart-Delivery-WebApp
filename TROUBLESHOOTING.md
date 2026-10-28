# SwiftDrop — Technical Troubleshooting & Diagnostics Guide

> **Tagline:** Your Essentials. Delivered Smarter.  
> **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)  
> **Author & Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)  
> **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)

---

## 1. Environment & Setup Issues

### Issue 1.1: PowerShell Execution Policy Restriction
* **Symptom:**  
  `File ...\Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
* **Solution:**  
  Open PowerShell and permit script execution for your user account:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Issue 1.2: Pillow Installation Failure on Python 3.13
* **Symptom:**  
  `KeyError: '__version__'` or C-extension compilation errors when running `pip install -r requirements.txt`.
* **Root Cause:**  
  Older versions of Pillow (< 10.4.0) lack pre-built wheels for Python 3.13.
* **Solution:**  
  Upgrade Pillow in `requirements.txt` to `Pillow>=10.4.0`:
  ```bash
  pip install --upgrade "Pillow>=10.4.0"
  ```

### Issue 1.3: Port 8000 Already in Use
* **Symptom:**  
  `Error: That port is already in use.`
* **Solution:**  
  Specify an alternate port when launching the development server:
  ```bash
  python manage.py runserver 8080
  ```
  Or identify and terminate the process holding the port on Windows:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  ```

---

## 2. Database & Data Integrity Issues

### Issue 2.1: SQLite Database Is Locked (`OperationalError: database is locked`)
* **Symptom:**  
  `sqlite3.OperationalError: database is locked` during migrations, seeding, or checkout.
* **Root Cause:**  
  An external database viewer (such as DB Browser for SQLite or VS Code SQLite extension) is holding an open write lock or uncommitted transaction on `db.sqlite3`.
* **Solution:**  
  1. Close DB Browser for SQLite or any external SQL tool.
  2. If a dangling `.sqlite3-journal` or `.sqlite3-wal` file remains, stop the Django server and restart it to release the lock cleanly.

### Issue 2.2: Missing Table Errors (`no such table: orders_productservice`)
* **Symptom:**  
  Database queries fail on uninitialized tables.
* **Solution:**  
  Run all pending migrations and re-seed required data:
  ```bash
  python manage.py migrate
  python manage.py setup_data
  ```

---

## 3. Authentication & Account Inquiries

### Issue 3.1: Unable to Sign In with Demo Accounts
* **Symptom:**  
  `Please enter a correct email and password.`
* **Solution:**  
  Re-seed the verified default accounts:
  ```bash
  python manage.py setup_data
  ```
  Verify that you are using:
  * **Customer:** `rifat@gmail.com` / `123456`
  * **Admin:** `rifatadmin@gmail.com` / `123456`

---

## 4. Static Files & Image Rendering

### Issue 4.1: Missing Styles or Broken Graphics in Production
* **Symptom:**  
  The application loads unstyled HTML or broken image placeholders.
* **Solution:**  
  1. Run Django's static collection command:
     ```bash
     python manage.py collectstatic --noinput --settings=Nagaribashi_express.settings_production
     ```
  2. Ensure your web server (Nginx / WhiteNoise) is configured with aliases pointing to `staticfiles/` and `media/`.
  3. SwiftDrop includes automatic vector SVG category fallbacks (`/static/images/fallbacks/`) that render automatically if uploaded photography is not present.

---

## 5. Automated Testing Verification

If tests fail when executed from an arbitrary directory:
* Ensure your current working directory is the repository root:
  ```powershell
  cd "F:\IUBAT\8th Semester\CSE 3391\Smart Delivery Webapp\Smart-Delivery-WebApp"
  python manage.py test users orders delivery payments reviews dashboard
  ```

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*

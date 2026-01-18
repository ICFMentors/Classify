# Critical Security Fixes Required

## 🚨 IMMEDIATE ACTION REQUIRED

Your application currently has **CRITICAL SECURITY VULNERABILITIES** that expose:
- Database credentials
- Authentication secrets
- API keys
- User data

---

## Quick Fix Guide (5 Minutes)

### 1. Generate a Secret Key (30 seconds)

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Create `.env` File (2 minutes)

Create `/home/user/Classify/.env`:

```bash
# REQUIRED - Use the secret key you just generated
SECRET_KEY=paste-your-generated-key-here

# REQUIRED - Set to production
FLASK_ENV=production

# REQUIRED - Update with your production database
DATABASE_URL=mysql+pymysql://NEW_USER:NEW_STRONG_PASSWORD@34.106.105.100/school

# REQUIRED - Get these from Firebase Console (https://console.firebase.google.com)
FIREBASE_API_KEY=AIzaSyBWQXbSBC6oKNZk96jMP53qvHJqekG0T1Q
FIREBASE_AUTH_DOMAIN=summer-2023-396400.firebaseapp.com
FIREBASE_PROJECT_ID=summer-2023-396400
FIREBASE_STORAGE_BUCKET=summer-2023-396400.appspot.com
FIREBASE_MESSAGING_SENDER_ID=900862315561
FIREBASE_APP_ID=1:900862315561:web:fa9f9ccf3f5f2b4f6b6038
FIREBASE_MEASUREMENT_ID=G-XYTJ9FBMVG
FIREBASE_DATABASE_URL=

# OPTIONAL
PORT=8080
```

### 3. Update `app.py` (2 minutes)

**Add at line 10 (after imports):**
```python
from dotenv import load_dotenv
load_dotenv()
```

**Replace line 13:**
```python
# OLD:
app.secret_key = 'summer2023project'

# NEW:
app.secret_key = os.getenv('SECRET_KEY')
```

**Replace line 15:**
```python
# OLD:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://classifydbuser:WeakPass@23@34.106.105.100/school'

# NEW:
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
```

**Replace lines 19-28 (Firebase config):**
```python
# OLD:
config = {
    'apiKey': "AIzaSyBWQXbSBC6oKNZk96jMP53qvHJqekG0T1Q",
    'authDomain': "summer-2023-396400.firebaseapp.com",
    # ... etc
}

# NEW:
config = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('FIREBASE_APP_ID'),
    'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID'),
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL', ' ')
}
```

**Replace line 668 (app.run):**
```python
# OLD:
app.run(debug=True, port=8080)

# NEW:
debug_mode = os.getenv('FLASK_ENV') == 'development'
port = int(os.getenv('PORT', 8080))
app.run(debug=debug_mode, port=port, host='0.0.0.0')
```

### 4. Test Locally (30 seconds)

```bash
source env/bin/activate  # or .\env\Scripts\activate on Windows
python app.py
```

Verify you see:
- ✅ Application starts without errors
- ✅ No "summer2023project" or "WeakPass@23" in logs
- ✅ "Running in production mode" or similar message

### 5. NEVER Commit .env (Already Done)

✅ `.gitignore` has been created and includes `.env`

---

## What Was Exposed?

### Before Fixes:
```python
# ❌ EXPOSED IN PUBLIC REPOSITORY:
app.secret_key = 'summer2023project'
'mysql+pymysql://classifydbuser:WeakPass@23@34.106.105.100/school'
'apiKey': "AIzaSyBWQXbSBC6oKNZk96jMP53qvHJqekG0T1Q"
```

### After Fixes:
```python
# ✅ SECURE - Values loaded from environment:
app.secret_key = os.getenv('SECRET_KEY')
os.getenv('DATABASE_URL')
os.getenv('FIREBASE_API_KEY')
```

---

## Additional Hardening (Recommended)

### Change Database Password

```sql
-- Connect to MySQL
mysql -u root -p

-- Change the password
ALTER USER 'classifydbuser'@'%' IDENTIFIED BY 'NewStr0ngP@ssw0rd!2024';
FLUSH PRIVILEGES;
```

Update your `.env`:
```bash
DATABASE_URL=mysql+pymysql://classifydbuser:NewStr0ngP@ssw0rd!2024@34.106.105.100/school
```

### Rotate Firebase Keys

1. Go to Firebase Console: https://console.firebase.google.com
2. Select your project: `summer-2023-396400`
3. Settings → General → Your apps
4. Delete old web app and create new one (generates new API keys)
5. Update `.env` with new credentials

---

## Deployment Platform Config

### Heroku

```bash
heroku config:set SECRET_KEY=your-generated-key
heroku config:set FLASK_ENV=production
heroku config:set DATABASE_URL=mysql+pymysql://user:pass@host/db
heroku config:set FIREBASE_API_KEY=your-key
# ... set all other variables
```

### AWS, DigitalOcean, etc.

Set environment variables in your platform's dashboard or use:

```bash
export SECRET_KEY=your-generated-key
export FLASK_ENV=production
# ... etc
```

---

## Verification Checklist

After making changes, verify:

- [ ] `.env` file exists and contains all required variables
- [ ] `.env` is listed in `.gitignore`
- [ ] `app.py` uses `os.getenv()` instead of hardcoded values
- [ ] Application starts successfully
- [ ] Login/signup still works
- [ ] Database connection works
- [ ] No secrets visible in `git log` output
- [ ] Debug mode is disabled in production

---

## Test Commands

```bash
# Check if .env is ignored
git status  # Should NOT show .env

# Verify no secrets in code
grep -n "summer2023project" app.py  # Should return nothing
grep -n "WeakPass" app.py  # Should return nothing
grep -n "AIzaSyB" app.py  # Should return nothing

# Test environment loading
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('SECRET_KEY loaded:', bool(os.getenv('SECRET_KEY')))"
```

Expected output:
```
SECRET_KEY loaded: True
```

---

## Next Steps

1. ✅ Complete the 5-minute quick fix above
2. 📖 Read `DEPLOYMENT.md` for full deployment guide
3. 🔄 Set up regular secret rotation (every 90 days)
4. 🔒 Enable additional security features (CSRF, security headers)
5. 📊 Set up monitoring and logging

---

## Need Help?

- Full deployment guide: `DEPLOYMENT.md`
- Code examples: `app_production.py`
- Environment template: `.env.example`

**REMEMBER:** Never commit `.env` file to git!

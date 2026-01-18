# Production Deployment Guide for Classify LMS

This guide outlines the steps needed to deploy Classify to a production environment securely.

## 🚨 Critical Issues to Fix

### 1. Security Vulnerabilities

**Current Issues:**
- ❌ Hardcoded Flask secret key (`'summer2023project'`)
- ❌ Hardcoded database password (`WeakPass@23`)
- ❌ Hardcoded Firebase API keys
- ❌ Debug mode enabled in production
- ❌ No `.gitignore` file (risks committing secrets)

**Impact:** Attackers could compromise your application, database, and user data.

---

## 📝 Step-by-Step Deployment Checklist

### Step 1: Generate a Secure Secret Key

```bash
# In Python shell or terminal:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Save this key - you'll need it for the `.env` file.

### Step 2: Create Environment Variables File

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
nano .env  # or vim, code, etc.
```

Fill in your `.env` file with real values:

```bash
# Generate a new secret key (use command from Step 1)
SECRET_KEY=abc123def456...your-generated-key

# Set environment
FLASK_ENV=production

# Production database (MySQL)
DATABASE_URL=mysql+pymysql://your_user:your_secure_password@your_host:3306/your_database

# Firebase credentials (from Firebase Console)
FIREBASE_API_KEY=your-actual-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abcdef
FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com

# Server configuration
PORT=8080
```

**⚠️ IMPORTANT:** Never commit the `.env` file to git!

### Step 3: Update app.py

You have two options:

**Option A: Quick Update (Minimal Changes)**

Add these lines at the top of `app.py` after the imports:

```python
from dotenv import load_dotenv
load_dotenv()
```

Then replace:

```python
# OLD (lines 13-28):
app.secret_key = 'summer2023project'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://classifydbuser:WeakPass@23@34.106.105.100/school'

config = {
    'apiKey': "AIzaSyBWQXbSBC6oKNZk96jMP53qvHJqekG0T1Q",
    # ... rest of hardcoded config
}

# NEW:
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

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

And update the run configuration (line 668):

```python
# OLD:
if __name__ == '__main__':
    if not os.path.exists('data.db'):
        db.create_all()
    app.run(debug=True, port=8080)

# NEW:
if __name__ == '__main__':
    flask_env = os.getenv('FLASK_ENV', 'development')
    database_url = os.getenv('DATABASE_URL', 'sqlite:///data.db')

    # Only create SQLite tables in development
    if 'sqlite' in database_url and not os.path.exists('data.db'):
        with app.app_context():
            db.create_all()

    # Disable debug in production
    debug_mode = flask_env == 'development'
    port = int(os.getenv('PORT', 8080))

    app.run(debug=debug_mode, port=port, host='0.0.0.0')
```

**Option B: Use the Production Template**

Reference the `app_production.py` file I created for you as a guide.

### Step 4: Update .gitignore

The `.gitignore` file has been created. **Verify it includes:**

```
.env
.env.local
.env.production
*.db
__pycache__/
env/
```

### Step 5: Database Setup for Production

**For MySQL Production Database:**

1. Create the database:
```sql
CREATE DATABASE school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Create a secure user:
```sql
CREATE USER 'classify_prod'@'%' IDENTIFIED BY 'StrongP@ssw0rd!2024';
GRANT ALL PRIVILEGES ON school.* TO 'classify_prod'@'%';
FLUSH PRIVILEGES;
```

3. Initialize tables (run once):
```bash
python3 -c "from app import db; db.create_all()"
```

4. Import sample data if needed:
```bash
mysql -u classify_prod -p school < data.sql
```

### Step 6: Verify Environment Variables Are Loaded

Test locally before deploying:

```bash
# Activate virtual environment
source env/bin/activate  # or .\env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Test the application
python app.py
```

Check the logs to ensure:
- ✅ No hardcoded values appear
- ✅ Debug mode is OFF
- ✅ Database connection succeeds
- ✅ Firebase initializes correctly

### Step 7: Security Hardening

**Add Flask Security Headers** (recommended):

```bash
pip install flask-talisman
```

In `app.py`, add:

```python
from flask_talisman import Talisman

# After app = Flask(__name__)
if os.getenv('FLASK_ENV') == 'production':
    Talisman(app,
             force_https=True,
             strict_transport_security=True,
             content_security_policy={
                 'default-src': "'self'",
                 'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
                 'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"]
             })
```

**Additional Security Recommendations:**

1. Enable CSRF protection:
```bash
pip install flask-wtf
```

2. Set session cookie security:
```python
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

3. Update MySQL password from `WeakPass@23` to a strong password

### Step 8: Platform-Specific Deployment

#### Heroku Deployment

1. **Set environment variables:**
```bash
heroku config:set SECRET_KEY=your-generated-secret-key
heroku config:set FLASK_ENV=production
heroku config:set DATABASE_URL=mysql+pymysql://user:pass@host/db
heroku config:set FIREBASE_API_KEY=your-key
# ... set all other Firebase variables
```

2. **Update Procfile** (already exists):
```
web: gunicorn app:app
```

3. **Deploy:**
```bash
git add .
git commit -m "Configure for production deployment"
git push heroku main
```

4. **Initialize database:**
```bash
heroku run python -c "from app import db; db.create_all()"
```

#### Other Platforms (AWS, DigitalOcean, etc.)

1. **Set environment variables** in your hosting platform's dashboard
2. **Use a process manager** like systemd or supervisor
3. **Set up nginx** as a reverse proxy
4. **Enable SSL/TLS** with Let's Encrypt

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 9: Post-Deployment Verification

**Test these critical functions:**

- [ ] User registration
- [ ] User login/logout
- [ ] Course creation (teacher)
- [ ] Course enrollment (student)
- [ ] Announcements
- [ ] Profile updates
- [ ] Database persistence
- [ ] Session management
- [ ] Error pages (404, 500)
- [ ] HTTPS redirect (if configured)

**Monitor logs for:**
- ❌ No secret keys or passwords in logs
- ❌ No debug mode warnings
- ✅ Successful database connections
- ✅ Proper error handling

### Step 10: Ongoing Maintenance

**Regular tasks:**

1. **Update dependencies:**
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

2. **Rotate secrets** periodically (every 90 days):
   - Generate new SECRET_KEY
   - Update database passwords
   - Regenerate Firebase credentials if compromised

3. **Monitor security advisories:**
   - Check GitHub Dependabot alerts
   - Subscribe to Flask security announcements

4. **Backup database regularly:**
```bash
# MySQL backup
mysqldump -u user -p school > backup_$(date +%Y%m%d).sql
```

---

## 🔥 URGENT: Before First Deployment

**DO THIS IMMEDIATELY:**

1. ✅ Create `.env` file with secure values
2. ✅ Update `app.py` to use environment variables
3. ✅ Verify `.gitignore` includes `.env`
4. ✅ **REMOVE HARDCODED SECRETS FROM GIT HISTORY**

### Removing Secrets from Git History

Since you've already committed hardcoded secrets:

```bash
# Option 1: Use BFG Repo-Cleaner (recommended)
# Download from: https://reclaimtheweb.org/bfg-repo-cleaner/
java -jar bfg.jar --replace-text passwords.txt

# Option 2: Use git-filter-repo
git filter-repo --replace-text passwords.txt

# Option 3: Treat repository as compromised
# - Rotate ALL secrets immediately
# - Consider starting a new repository
```

**After removing secrets:**
```bash
git push --force  # ⚠️ Coordinate with team first!
```

**Then immediately:**
- Regenerate new Firebase API keys
- Change all database passwords
- Generate new Flask secret key

---

## 📊 Production Checklist Summary

- [ ] `.env` file created with secure values
- [ ] `.gitignore` includes `.env` and `*.db`
- [ ] `app.py` updated to use `os.getenv()`
- [ ] Debug mode disabled (`FLASK_ENV=production`)
- [ ] Strong secret key generated
- [ ] Database password changed from `WeakPass@23`
- [ ] Firebase credentials moved to environment
- [ ] SSL/HTTPS enabled
- [ ] Database backups configured
- [ ] Error logging set up
- [ ] Security headers added (optional)
- [ ] CSRF protection enabled (optional)
- [ ] All secrets removed from git history
- [ ] Application tested in staging environment
- [ ] Monitoring and alerting configured

---

## 🆘 Troubleshooting

### "KeyError: SECRET_KEY"
- Ensure `.env` file exists in project root
- Verify `load_dotenv()` is called before accessing variables
- Check environment variables are set on hosting platform

### Database Connection Fails
- Verify `DATABASE_URL` format: `mysql+pymysql://user:pass@host:port/db`
- Check database server allows remote connections
- Verify firewall rules allow connection from your server

### Firebase Authentication Fails
- Confirm all Firebase environment variables are set
- Check API key is valid in Firebase Console
- Verify `authDomain` matches your Firebase project

### Application Won't Start
- Check logs: `heroku logs --tail` (Heroku) or server logs
- Verify all dependencies installed: `pip install -r requirements.txt`
- Test locally with production settings first

---

## 📚 Additional Resources

- [Flask Production Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [12-Factor App Methodology](https://12factor.net/)
- [Heroku Python Documentation](https://devcenter.heroku.com/categories/python-support)

---

**Last Updated:** 2026-01-18
**Version:** 1.0

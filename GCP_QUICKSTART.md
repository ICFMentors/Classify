# GCP Cloud SQL Quick Start (5 Steps)

## TL;DR: Get MySQL Running on GCP in 15 Minutes

### Prerequisites
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

## Step 1: Enable APIs (2 minutes)

```bash
gcloud services enable sqladmin.googleapis.com \
    sql-component.googleapis.com \
    compute.googleapis.com
```

---

## Step 2: Create Database Instance (3 minutes)

**Via Console:** [Click Here](https://console.cloud.google.com/sql/choose-instance-engine)

OR via command line:

```bash
# Generate secure root password
ROOT_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Save this password: $ROOT_PASSWORD"

# Create instance (takes 5-10 minutes)
gcloud sql instances create classify-db \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password="$ROOT_PASSWORD" \
    --backup \
    --storage-auto-increase

# Get connection info
gcloud sql instances describe classify-db \
    --format="value(connectionName,ipAddresses[0].ipAddress)"
```

**Save these values:**
- Connection Name: `PROJECT_ID:REGION:classify-db`
- Public IP: `XX.XX.XX.XX`

---

## Step 3: Create Database & User (2 minutes)

```bash
# Connect to instance
gcloud sql connect classify-db --user=root

# In MySQL shell, run:
```

```sql
CREATE DATABASE school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'classify_app'@'%' IDENTIFIED BY 'YOUR_STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON school.* TO 'classify_app'@'%';
FLUSH PRIVILEGES;
EXIT;
```

**Generate password:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 4: Configure Access (3 minutes)

### Option A: Allow Your Server IP (Recommended)

```bash
# Add your deployment server IP
gcloud sql instances patch classify-db \
    --authorized-networks=YOUR_SERVER_IP/32
```

### Option B: Use Cloud SQL Proxy (Development)

```bash
# Download proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# Start proxy
./cloud_sql_proxy -instances=PROJECT:REGION:classify-db=tcp:3306 &
```

### Option C: Allow All (Less Secure - Use SSL!)

```bash
gcloud sql instances patch classify-db \
    --authorized-networks=0.0.0.0/0
```

---

## Step 5: Update Your Application (5 minutes)

### Update `.env`:

```bash
# For direct connection (Option A)
DATABASE_URL=mysql+pymysql://classify_app:YOUR_PASSWORD@PUBLIC_IP:3306/school

# For Cloud SQL Proxy (Option B)
DATABASE_URL=mysql+pymysql://classify_app:YOUR_PASSWORD@127.0.0.1:3306/school

# With SSL (recommended)
DATABASE_URL=mysql+pymysql://classify_app:YOUR_PASSWORD@PUBLIC_IP:3306/school?ssl_mode=REQUIRED
```

### Install dependencies:

```bash
pip install PyMySQL cryptography
```

### Test connection:

```bash
python3 -c "
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✅ Connection successful!')
"
```

---

## Migration: Copy Existing Data

```bash
# Export from old database
mysqldump -h 34.106.105.100 \
    -u classifydbuser \
    -p'WeakPass@23' \
    school > backup.sql

# Import to Cloud SQL
mysql -h PUBLIC_IP -u classify_app -p school < backup.sql

# Or via Cloud SQL Proxy
mysql -h 127.0.0.1 -u classify_app -p school < backup.sql
```

---

## Cost Estimate

**db-f1-micro (Development):**
- Instance: $9.37/month
- Storage (10GB): $1.70/month
- **Total: ~$11/month**

**db-n1-standard-1 (Production):**
- Instance: $44.77/month
- Storage (10GB): $1.70/month
- **Total: ~$47/month**

---

## Platform-Specific Setup

### Heroku

```bash
# Set environment variable
heroku config:set DATABASE_URL="mysql+pymysql://classify_app:PASSWORD@PUBLIC_IP:3306/school"

# Deploy
git push heroku main

# Initialize tables
heroku run python -c "from app import db; db.create_all()"
```

### Google Cloud Run

```bash
# Deploy with Cloud SQL connection
gcloud run deploy classify-app \
    --image gcr.io/PROJECT_ID/classify-app \
    --add-cloudsql-instances=PROJECT:REGION:classify-db \
    --set-env-vars DATABASE_URL="mysql+pymysql://classify_app:PASSWORD@/school?unix_socket=/cloudsql/PROJECT:REGION:classify-db" \
    --region us-central1 \
    --allow-unauthenticated
```

### Compute Engine / VPS

```bash
# Install Cloud SQL Proxy as systemd service
sudo nano /etc/systemd/system/cloud-sql-proxy.service
```

```ini
[Unit]
Description=Cloud SQL Proxy
After=network.target

[Service]
Type=simple
User=www-data
ExecStart=/usr/local/bin/cloud_sql_proxy -instances=PROJECT:REGION:classify-db=tcp:3306
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cloud-sql-proxy
sudo systemctl start cloud-sql-proxy

# Update .env to use 127.0.0.1:3306
```

---

## Verification Checklist

- [ ] Cloud SQL instance created and running
- [ ] Database `school` created
- [ ] User `classify_app` created with strong password
- [ ] Authorized networks configured OR Cloud SQL Proxy running
- [ ] `.env` updated with correct DATABASE_URL
- [ ] Application connects successfully
- [ ] Data migrated from old database (if applicable)
- [ ] Backups enabled and tested

---

## Troubleshooting

### "Can't connect to MySQL server"

1. Check instance is running:
```bash
gcloud sql instances describe classify-db --format="value(state)"
```

2. Verify authorized networks:
```bash
gcloud sql instances describe classify-db \
    --format="value(settings.ipConfiguration.authorizedNetworks)"
```

3. Test with mysql client:
```bash
mysql -h PUBLIC_IP -u classify_app -p
```

### "Access denied for user"

- Verify username and password
- Check user was created: `SELECT User,Host FROM mysql.user WHERE User='classify_app';`
- Verify grants: `SHOW GRANTS FOR 'classify_app'@'%';`

### "SSL connection error"

```bash
# Download server certificate
gcloud sql ssl-certs describe server-ca \
    --instance=classify-db \
    --format="get(cert)" > server-ca.pem

# Update DATABASE_URL
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@PUBLIC_IP:3306/school?ssl_ca=/path/to/server-ca.pem
```

---

## Useful Commands

```bash
# Connect to database
gcloud sql connect classify-db --user=classify_app --database=school

# View instance details
gcloud sql instances describe classify-db

# Create manual backup
gcloud sql backups create --instance=classify-db

# List backups
gcloud sql backups list --instance=classify-db

# Stop instance (to save costs in dev)
gcloud sql instances patch classify-db --activation-policy=NEVER

# Start instance
gcloud sql instances patch classify-db --activation-policy=ALWAYS

# Delete instance (careful!)
gcloud sql instances delete classify-db
```

---

## Security Best Practices

1. ✅ Use strong passwords (32+ characters)
2. ✅ Enable automated backups
3. ✅ Use SSL for public IP connections
4. ✅ Whitelist specific IPs (not 0.0.0.0/0)
5. ✅ Store credentials in Secret Manager (not .env in production)
6. ✅ Enable point-in-time recovery
7. ✅ Set up monitoring alerts

---

## Next Steps

After basic setup:

1. 📊 Set up monitoring: [GCP_DATABASE_SETUP.md](GCP_DATABASE_SETUP.md#monitoring-and-maintenance)
2. 🔒 Configure SSL: [GCP_DATABASE_SETUP.md](GCP_DATABASE_SETUP.md#security-configuration)
3. 💰 Optimize costs: [GCP_DATABASE_SETUP.md](GCP_DATABASE_SETUP.md#cost-estimation)
4. 🚀 Read full guide: [GCP_DATABASE_SETUP.md](GCP_DATABASE_SETUP.md)

---

**Quick Links:**
- [Cloud SQL Console](https://console.cloud.google.com/sql)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs/mysql)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

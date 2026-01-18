# GCP Cloud Database Setup Guide for Classify LMS

This guide covers setting up a production MySQL database on Google Cloud Platform (GCP) for the Classify application.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Option 1: Cloud SQL for MySQL (Recommended)](#option-1-cloud-sql-for-mysql-recommended)
- [Option 2: Cloud SQL with Cloud Run](#option-2-cloud-sql-with-cloud-run)
- [Security Configuration](#security-configuration)
- [Connection Methods](#connection-methods)
- [Migration from Current Database](#migration-from-current-database)
- [Cost Estimation](#cost-estimation)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Current Setup:**
- MySQL at `34.106.105.100:3306`
- Database: `school`
- User: `classifydbuser`
- Password: `WeakPass@23` (insecure)

**Recommended GCP Setup:**
- **Cloud SQL for MySQL** - Fully managed MySQL database
- **Automatic backups** and point-in-time recovery
- **High availability** with automatic failover
- **Automatic storage scaling**
- **Built-in security** with VPC, SSL, and IAM

---

## Prerequisites

### 1. GCP Account Setup

```bash
# Install Google Cloud SDK
# For Linux/Mac:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# For Windows: Download from
# https://cloud.google.com/sdk/docs/install

# Initialize gcloud
gcloud init

# Login to your account
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
# Enable Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com

# Enable Cloud SQL API
gcloud services enable sql-component.googleapis.com

# Enable Compute Engine API (for networking)
gcloud services enable compute.googleapis.com

# Enable Secret Manager (for credentials)
gcloud services enable secretmanager.googleapis.com
```

### 3. Install Cloud SQL Proxy (for local development)

```bash
# Linux
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# Mac
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
chmod +x cloud_sql_proxy

# Windows
# Download from: https://dl.google.com/cloudsql/cloud_sql_proxy.x64.exe
```

---

## Option 1: Cloud SQL for MySQL (Recommended)

### Step 1: Create Cloud SQL Instance

#### Via Console (Easy)

1. Go to [Cloud SQL Console](https://console.cloud.google.com/sql)
2. Click **"Create Instance"**
3. Choose **"MySQL"**
4. Select **MySQL 8.0** (or latest stable version)

**Configuration:**
- **Instance ID**: `classify-production-db`
- **Password**: Generate a strong password (save it securely!)
- **Region**: Choose closest to your users (e.g., `us-central1`)
- **Zone**: Single zone (or Multi-zone for HA)
- **Database version**: MySQL 8.0
- **Preset**:
  - Development: db-f1-micro (1 vCPU, 0.6 GB RAM) - ~$10/month
  - Production: db-n1-standard-1 (1 vCPU, 3.75 GB RAM) - ~$45/month
  - High Load: db-n1-standard-2 (2 vCPU, 7.5 GB RAM) - ~$90/month

**Storage:**
- Type: SSD
- Capacity: 10 GB (auto-scales up to 1000 GB)
- Enable automatic storage increase: ✅

**Backups:**
- Enable automated backups: ✅
- Backup window: Choose low-traffic time (e.g., 3:00 AM)
- Point-in-time recovery: ✅ (recommended)

**Maintenance:**
- Maintenance window: Choose low-traffic time
- Order: Any available

Click **"Create Instance"** (takes 5-10 minutes)

#### Via Command Line (Advanced)

```bash
# Set variables
PROJECT_ID="your-project-id"
INSTANCE_NAME="classify-production-db"
REGION="us-central1"
ROOT_PASSWORD="$(openssl rand -base64 32)"

# Save the password securely!
echo "Root Password: $ROOT_PASSWORD" > ~/classify-db-password.txt
chmod 600 ~/classify-db-password.txt

# Create the instance
gcloud sql instances create $INSTANCE_NAME \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=$REGION \
    --root-password="$ROOT_PASSWORD" \
    --backup \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=3 \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --storage-auto-increase-limit=100

# For production with high availability:
gcloud sql instances create $INSTANCE_NAME \
    --database-version=MYSQL_8_0 \
    --tier=db-n1-standard-1 \
    --region=$REGION \
    --root-password="$ROOT_PASSWORD" \
    --availability-type=REGIONAL \
    --backup \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=3 \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase
```

### Step 2: Create Database and User

```bash
# Connect to instance (uses Cloud SQL Proxy)
gcloud sql connect $INSTANCE_NAME --user=root

# Or get connection name and use mysql client
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format='value(connectionName)')
echo "Connection Name: $INSTANCE_CONNECTION_NAME"
```

In MySQL shell:

```sql
-- Create the database
CREATE DATABASE school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user with strong password
CREATE USER 'classify_app'@'%' IDENTIFIED BY 'GENERATE_STRONG_PASSWORD_HERE';

-- Grant privileges
GRANT ALL PRIVILEGES ON school.* TO 'classify_app'@'%';

-- Create read-only user for backups/reports (optional)
CREATE USER 'classify_readonly'@'%' IDENTIFIED BY 'ANOTHER_STRONG_PASSWORD';
GRANT SELECT ON school.* TO 'classify_readonly'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User LIKE 'classify%';

-- Exit
EXIT;
```

**Generate Strong Passwords:**
```bash
# Generate password for classify_app
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate password for classify_readonly
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Configure Connection Security

#### Option A: Public IP with Authorized Networks (Simplest)

```bash
# Add your deployment server IP
gcloud sql instances patch $INSTANCE_NAME \
    --authorized-networks=YOUR_SERVER_IP/32

# For multiple IPs
gcloud sql instances patch $INSTANCE_NAME \
    --authorized-networks=IP1/32,IP2/32,IP3/32

# For Heroku or other platforms with dynamic IPs, you might need:
# WARNING: Less secure, use with SSL
gcloud sql instances patch $INSTANCE_NAME \
    --authorized-networks=0.0.0.0/0
```

**Important:** If using `0.0.0.0/0`, MUST enable SSL (see Security Configuration below)

#### Option B: Private IP with VPC (Most Secure)

```bash
# Enable Private IP
gcloud sql instances patch $INSTANCE_NAME \
    --network=projects/$PROJECT_ID/global/networks/default \
    --no-assign-ip

# Or create dedicated VPC
gcloud compute networks create classify-vpc \
    --subnet-mode=auto

gcloud sql instances patch $INSTANCE_NAME \
    --network=projects/$PROJECT_ID/global/networks/classify-vpc
```

#### Option C: Cloud SQL Proxy (Recommended for Development)

No IP whitelisting needed - uses IAM for authentication.

### Step 4: Get Connection Details

```bash
# Get instance connection name
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME \
    --format='value(connectionName)')

echo "Instance Connection Name: $INSTANCE_CONNECTION_NAME"

# Get public IP (if using public IP)
PUBLIC_IP=$(gcloud sql instances describe $INSTANCE_NAME \
    --format='value(ipAddresses[0].ipAddress)')

echo "Public IP: $PUBLIC_IP"

# Get private IP (if configured)
PRIVATE_IP=$(gcloud sql instances describe $INSTANCE_NAME \
    --format='value(ipAddresses[1].ipAddress)')

echo "Private IP: $PRIVATE_IP"
```

### Step 5: Update Application Configuration

#### Update `.env` file:

```bash
# For Public IP connection
DATABASE_URL=mysql+pymysql://classify_app:YOUR_STRONG_PASSWORD@PUBLIC_IP:3306/school?charset=utf8mb4

# For Private IP connection
DATABASE_URL=mysql+pymysql://classify_app:YOUR_STRONG_PASSWORD@PRIVATE_IP:3306/school?charset=utf8mb4

# For Cloud SQL Proxy (local development)
DATABASE_URL=mysql+pymysql://classify_app:YOUR_STRONG_PASSWORD@127.0.0.1:3306/school?charset=utf8mb4

# With SSL (recommended)
DATABASE_URL=mysql+pymysql://classify_app:YOUR_STRONG_PASSWORD@PUBLIC_IP:3306/school?charset=utf8mb4&ssl_mode=REQUIRED
```

#### Update `requirements.txt`:

Add if not already present:
```
PyMySQL>=1.0.2
cryptography>=3.4.8  # Required for SSL connections
```

Install:
```bash
pip install PyMySQL cryptography
```

---

## Option 2: Cloud SQL with Cloud Run

If deploying the entire app to GCP Cloud Run:

### Step 1: Create Cloud SQL Instance

Same as Option 1 above, but use Private IP.

### Step 2: Deploy to Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/classify-app

# Deploy with Cloud SQL connection
gcloud run deploy classify-app \
    --image gcr.io/$PROJECT_ID/classify-app \
    --add-cloudsql-instances=$INSTANCE_CONNECTION_NAME \
    --set-env-vars DATABASE_URL="mysql+pymysql://classify_app:PASSWORD@/school?unix_socket=/cloudsql/$INSTANCE_CONNECTION_NAME" \
    --set-env-vars SECRET_KEY="YOUR_SECRET_KEY" \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

**Note:** When using Cloud Run with Cloud SQL, the connection uses Unix sockets, not TCP.

---

## Security Configuration

### 1. Enable SSL/TLS Connections

#### Download Server Certificates:

```bash
# Get server CA certificate
gcloud sql ssl-certs list --instance=$INSTANCE_NAME

# Create client certificate (optional, for mutual TLS)
gcloud sql ssl-certs create classify-client-cert \
    client-key.pem \
    --instance=$INSTANCE_NAME

# Download server CA cert
gcloud sql ssl-certs describe server-ca \
    --instance=$INSTANCE_NAME \
    --format="get(cert)" > server-ca.pem
```

#### Update Connection String:

```python
# In app.py, add SSL configuration
import pymysql

# Configure SQLAlchemy with SSL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'ssl': {
            'ca': '/path/to/server-ca.pem',
            # Optional: for mutual TLS
            # 'cert': '/path/to/client-cert.pem',
            # 'key': '/path/to/client-key.pem',
        }
    }
}
```

### 2. Use Secret Manager for Credentials

```bash
# Store database password in Secret Manager
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-

# Grant access to your service account
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

In Python:
```python
from google.cloud import secretmanager

def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Use in DATABASE_URL
db_password = get_secret('db-password', 'your-project-id')
```

### 3. Enable Cloud SQL IAM Authentication (Advanced)

```bash
# Create IAM database user
gcloud sql users create classify-app-sa@your-project-id.iam \
    --instance=$INSTANCE_NAME \
    --type=CLOUD_IAM_USER

# Grant database permissions
gcloud sql connect $INSTANCE_NAME --user=root
```

```sql
GRANT ALL PRIVILEGES ON school.* TO 'classify-app-sa@your-project-id.iam';
FLUSH PRIVILEGES;
```

**Connection with IAM:**
```python
# No password needed!
DATABASE_URL=mysql+pymysql://classify-app-sa@your-project-id.iam@/school?unix_socket=/cloudsql/CONNECTION_NAME&charset=utf8mb4
```

---

## Connection Methods

### Method 1: Direct TCP Connection (Public IP)

**Pros:** Simple, works from anywhere
**Cons:** Requires IP whitelisting, less secure

```bash
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@PUBLIC_IP:3306/school
```

### Method 2: Cloud SQL Proxy (Recommended for Development)

**Pros:** Secure, no IP whitelisting, automatic SSL
**Cons:** Requires running proxy process

**Local Development:**
```bash
# Start proxy
./cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:3306

# In another terminal
export DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@127.0.0.1:3306/school
python app.py
```

**Production (background process):**
```bash
# Start proxy in background
./cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:3306 &

# Add to systemd service
sudo nano /etc/systemd/system/cloud-sql-proxy.service
```

```ini
[Unit]
Description=Cloud SQL Proxy
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/classify
ExecStart=/usr/local/bin/cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:3306
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cloud-sql-proxy
sudo systemctl start cloud-sql-proxy
```

### Method 3: Unix Socket (Cloud Run / Compute Engine)

**Pros:** Most secure, best performance
**Cons:** Only works on GCP compute resources

```bash
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@/school?unix_socket=/cloudsql/$INSTANCE_CONNECTION_NAME
```

### Method 4: Private IP via VPC (Production)

**Pros:** Secure, no proxy needed, good performance
**Cons:** Requires VPC setup, only works within GCP network

```bash
DATABASE_URL=mysql+pymysql://classify_app:PASSWORD@PRIVATE_IP:3306/school
```

---

## Migration from Current Database

### Option 1: Export and Import (Simple)

```bash
# Export from current database
mysqldump -h 34.106.105.100 \
    -u classifydbuser \
    -p'WeakPass@23' \
    --databases school \
    --single-transaction \
    --quick \
    --lock-tables=false > classify_backup.sql

# Import to Cloud SQL
gcloud sql import sql $INSTANCE_NAME \
    gs://YOUR_BUCKET/classify_backup.sql \
    --database=school

# Or import via proxy
mysql -h 127.0.0.1 -u classify_app -p school < classify_backup.sql
```

### Option 2: Cloud SQL Database Migration Service

```bash
# Create migration job (for minimal downtime)
gcloud sql operations list --instance=$INSTANCE_NAME

# Follow wizard in console:
# https://console.cloud.google.com/sql/migration
```

### Step-by-Step Migration:

1. **Backup current database:**
```bash
mysqldump -h 34.106.105.100 -u classifydbuser -p'WeakPass@23' \
    --single-transaction school > backup_$(date +%Y%m%d).sql
```

2. **Upload to Cloud Storage:**
```bash
# Create bucket
gsutil mb gs://classify-db-backups

# Upload backup
gsutil cp backup_*.sql gs://classify-db-backups/
```

3. **Import to Cloud SQL:**
```bash
gcloud sql import sql $INSTANCE_NAME \
    gs://classify-db-backups/backup_$(date +%Y%m%d).sql \
    --database=school
```

4. **Verify data:**
```bash
gcloud sql connect $INSTANCE_NAME --user=classify_app --database=school
```

```sql
-- Check tables
SHOW TABLES;

-- Check row counts
SELECT 'user' as table_name, COUNT(*) as count FROM user
UNION ALL
SELECT 'course', COUNT(*) FROM course
UNION ALL
SELECT 'teacher', COUNT(*) FROM teacher;
```

5. **Update application:**
```bash
# Update .env
DATABASE_URL=mysql+pymysql://classify_app:NEW_PASSWORD@PUBLIC_IP:3306/school

# Restart application
sudo systemctl restart classify-app
```

6. **Monitor and test:**
- Test login/signup
- Test course enrollment
- Test announcements
- Check error logs

---

## Cost Estimation

### Cloud SQL Pricing (as of 2024)

**db-f1-micro (Development):**
- 1 shared vCPU, 0.6 GB RAM
- ~$9.37/month (24/7)
- 10 GB SSD: $1.70/month
- **Total: ~$11/month**

**db-n1-standard-1 (Production):**
- 1 vCPU, 3.75 GB RAM
- ~$44.77/month (24/7)
- 10 GB SSD: $1.70/month
- Backups (10 GB): $0.80/month
- **Total: ~$47/month**

**db-n1-standard-2 (High Load):**
- 2 vCPU, 7.5 GB RAM
- ~$89.54/month (24/7)
- **Total: ~$91/month**

**Additional Costs:**
- Network egress: $0.12/GB (first 1 GB free)
- Backups: $0.08/GB/month
- High Availability: +100% instance cost

**Cost Optimization:**

1. **Use development tier for testing:**
```bash
gcloud sql instances patch $INSTANCE_NAME --tier=db-f1-micro
```

2. **Enable auto-scaling:**
```bash
gcloud sql instances patch $INSTANCE_NAME \
    --storage-auto-increase \
    --storage-auto-increase-limit=50
```

3. **Schedule downtime for dev environments:**
```bash
# Stop instance (development only)
gcloud sql instances patch $INSTANCE_NAME --activation-policy=NEVER

# Start instance
gcloud sql instances patch $INSTANCE_NAME --activation-policy=ALWAYS
```

---

## Monitoring and Maintenance

### Enable Monitoring

```bash
# Install Cloud SQL Insights
gcloud sql instances patch $INSTANCE_NAME \
    --insights-config-query-insights-enabled \
    --insights-config-query-string-length=1024 \
    --insights-config-record-application-tags \
    --insights-config-record-client-address
```

### View Metrics

```bash
# In Cloud Console:
# https://console.cloud.google.com/sql/instances/INSTANCE_NAME/monitoring

# Or via gcloud
gcloud sql operations list --instance=$INSTANCE_NAME --limit=10
```

### Set Up Alerts

1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Create alert policies for:
   - CPU utilization > 80%
   - Memory utilization > 80%
   - Disk utilization > 80%
   - Connection count > 80% of max
   - Replication lag > 5 seconds

### Backup Verification

```bash
# List backups
gcloud sql backups list --instance=$INSTANCE_NAME

# Create on-demand backup
gcloud sql backups create --instance=$INSTANCE_NAME

# Restore from backup
gcloud sql backups restore BACKUP_ID \
    --backup-instance=$INSTANCE_NAME \
    --backup-id=BACKUP_ID
```

---

## Troubleshooting

### Connection Issues

**Problem:** "Can't connect to MySQL server"

**Solutions:**
```bash
# 1. Check instance is running
gcloud sql instances describe $INSTANCE_NAME --format="value(state)"

# 2. Verify authorized networks
gcloud sql instances describe $INSTANCE_NAME \
    --format="value(settings.ipConfiguration.authorizedNetworks)"

# 3. Test connection
mysql -h PUBLIC_IP -u classify_app -p

# 4. Check Cloud SQL Proxy
ps aux | grep cloud_sql_proxy
```

### SSL Issues

**Problem:** "SSL connection error"

**Solutions:**
```bash
# Download fresh certificates
gcloud sql ssl-certs list --instance=$INSTANCE_NAME

# Verify SSL is required
gcloud sql instances describe $INSTANCE_NAME \
    --format="value(settings.ipConfiguration.requireSsl)"

# Test without SSL first
mysql -h PUBLIC_IP -u classify_app -p --ssl-mode=DISABLED
```

### Performance Issues

**Problem:** Slow queries

**Solutions:**
```bash
# Enable slow query log
gcloud sql instances patch $INSTANCE_NAME \
    --database-flags=slow_query_log=on,long_query_time=2

# View query insights
# https://console.cloud.google.com/sql/instances/INSTANCE_NAME/query-insights

# Check current connections
gcloud sql operations list --instance=$INSTANCE_NAME
```

### Out of Connections

**Problem:** "Too many connections"

**Solutions:**
```bash
# Increase max connections
gcloud sql instances patch $INSTANCE_NAME \
    --database-flags=max_connections=100

# Check current connections
mysql -h PUBLIC_IP -u classify_app -p -e "SHOW PROCESSLIST;"
```

---

## Production Checklist

- [ ] Cloud SQL instance created with appropriate tier
- [ ] Strong passwords generated and stored securely
- [ ] Database and application user created
- [ ] SSL/TLS enabled
- [ ] Authorized networks configured (or VPC setup)
- [ ] Automated backups enabled
- [ ] Point-in-time recovery enabled
- [ ] Monitoring and alerts configured
- [ ] Data migrated from old database
- [ ] Application tested with new database
- [ ] Connection pooling configured in application
- [ ] Backup restoration tested
- [ ] Secrets stored in Secret Manager (not .env in production)
- [ ] Cost alerts set up

---

## Quick Reference Commands

```bash
# Connect to instance
gcloud sql connect $INSTANCE_NAME --user=classify_app --database=school

# Start Cloud SQL Proxy
./cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:3306

# Check instance status
gcloud sql instances describe $INSTANCE_NAME

# Create backup
gcloud sql backups create --instance=$INSTANCE_NAME

# View logs
gcloud sql operations list --instance=$INSTANCE_NAME --limit=50

# Restart instance
gcloud sql instances restart $INSTANCE_NAME
```

---

## Next Steps

1. ✅ Create Cloud SQL instance
2. ✅ Configure security (SSL, authorized networks)
3. ✅ Migrate data from current database
4. ✅ Update application configuration
5. ✅ Test thoroughly
6. ✅ Set up monitoring and alerts
7. ✅ Document connection details in Secret Manager
8. 🚀 Deploy to production!

---

**Last Updated:** 2026-01-18
**GCP Documentation:** https://cloud.google.com/sql/docs/mysql

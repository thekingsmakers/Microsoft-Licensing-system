# Service Renewal Hub

A comprehensive web application for internal service management with automated expiry notifications, multi-provider email support, and full customization capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-green.svg)
![Python](https://img.shields.io/badge/python-%3E%3D3.9-blue.svg)

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone Repository](#1-clone-repository)
  - [Backend Setup](#2-backend-setup)
  - [Frontend Setup](#3-frontend-setup)
  - [Database Setup](#4-database-setup)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Email Configuration](#email-configuration)
  - [Theme & Branding](#theme--branding)
- [Running the Application](#running-the-application)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [First-Time Setup](#first-time-setup)
- [API Documentation](#api-documentation)
- [User Roles & Permissions](#user-roles--permissions)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

### Core Features
- **Service Dashboard**: Searchable, filterable table for all organizational services
- **Service Management**: Full CRUD operations with categories, costs, and contact information
- **Expiry Tracking**: Visual status indicators (Safe, Warning, Critical, Expired)
- **Automated Notifications**: Daily checks with configurable thresholds (default: 30, 7, 1 days)

### Email Integration
- **8 Email Providers Supported**:
  - Resend API
  - Custom SMTP
  - Gmail (with App Password)
  - Microsoft Outlook / Office 365
  - Microsoft Exchange Online
  - SendGrid
  - Mailgun
  - Yahoo Mail

### Administration
- **Role-Based Access Control (RBAC)**:
  - Admin: Full access to settings, users, and all features
  - User: Limited access (view/edit services, no settings)
- **User Management**: Create, edit roles, delete users
- **Settings Panel**: Configure all options via UI (no .env editing required)

### Customization
- **Branding**: Company name, tagline, logo URL
- **Theme**: Dark/Light/System mode
- **Accent Colors**: 8 presets + custom color picker
- **Email Templates**: Professional HTML templates with company branding

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TailwindCSS, Shadcn/UI |
| Backend | FastAPI (Python 3.9+) |
| Database | MongoDB |
| Email | Resend API / SMTP (aiosmtplib) |
| Scheduler | APScheduler |
| Authentication | JWT (PyJWT, bcrypt) |

---

## Prerequisites

Before installation, ensure you have:

- **Node.js** >= 18.0.0
- **Python** >= 3.9
- **MongoDB** >= 5.0 (local or cloud instance)
- **Yarn** (recommended) or npm
- **Git**

### Verify Prerequisites

```bash
node --version    # Should be >= 18.0.0
python3 --version # Should be >= 3.9
mongod --version  # Should be >= 5.0
yarn --version    # Any recent version
```

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd service-renewal-hub
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `.env` with your configuration (see [Environment Variables](#environment-variables)).

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
yarn install
# OR: npm install

# Create environment file
cp .env.example .env
```

Edit `.env` with your backend URL:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 4. Database Setup

#### Option A: Local MongoDB

```bash
# Start MongoDB service
sudo systemctl start mongod
# OR on macOS:
brew services start mongodb-community
```

#### Option B: MongoDB Atlas (Cloud)

1. Create account at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create a cluster
3. Get connection string
4. Update `MONGO_URL` in backend `.env`

---

## Configuration

### Environment Variables

#### Backend (`/backend/.env`)

```env
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="service_renewal_hub"

# CORS (comma-separated origins)
CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"

# JWT Secret (generate a secure random string)
JWT_SECRET="your-super-secret-key-change-in-production"

# Optional: Default email settings (can be configured via UI)
RESEND_API_KEY=""
SENDER_EMAIL="notifications@yourdomain.com"
COMPANY_NAME="Your Organization"
```

#### Frontend (`/frontend/.env`)

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Generate Secure JWT Secret

```bash
# Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

---

## Email Configuration

Email can be configured via the Settings UI (Admin > Settings > Email) or environment variables.

### Option 1: Resend (Recommended)

1. Sign up at [resend.com](https://resend.com)
2. Create API key at [resend.com/api-keys](https://resend.com/api-keys)
3. Verify your domain (or use `onboarding@resend.dev` for testing)
4. Enter API key in Settings > Email

### Option 2: Gmail SMTP

1. Enable 2-Factor Authentication on your Google account
2. Generate App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Configure in Settings > Email:
   - Provider: Gmail
   - SMTP Host: `smtp.gmail.com` (auto-filled)
   - Port: `587` (auto-filled)
   - Username: Your Gmail address
   - Password: App Password (16 characters)
   - Use TLS: Enabled

### Option 3: Microsoft Outlook / Office 365

1. Configure in Settings > Email:
   - Provider: Outlook
   - SMTP Host: `smtp.office365.com` (auto-filled)
   - Port: `587` (auto-filled)
   - Username: Your Outlook email
   - Password: Your password or App Password
   - Use TLS: Enabled

### Option 4: Custom SMTP

For any SMTP server:

| Setting | Description |
|---------|-------------|
| SMTP Host | e.g., `mail.yourdomain.com` |
| Port | Usually `587` (TLS) or `465` (SSL) |
| Username | Your email or account username |
| Password | Email account password |
| Use TLS | Enable for port 587, disable for 465 |

---

## Theme & Branding

All customization is done via Settings > Branding (Admin only).

### Company Branding
- **Company Name**: Displayed in header and emails
- **Tagline**: Displayed below company name
- **Logo URL**: Direct URL to logo image (PNG, SVG recommended)

### Theme Settings
- **Theme Mode**: Dark / Light / System
- **Accent Color**: Choose from presets or use custom hex color

### Color Presets
| Color | Hex Code |
|-------|----------|
| Cyan | `#06b6d4` |
| Violet | `#8b5cf6` |
| Emerald | `#10b981` |
| Amber | `#f59e0b` |
| Red | `#ef4444` |
| Pink | `#ec4899` |
| Blue | `#3b82f6` |
| Lime | `#84cc16` |

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
# OR: npm start
```

Access the application at: `http://localhost:3000`

### Production Mode

#### Backend (using Gunicorn)

```bash
cd backend
pip install gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

#### Frontend (build static files)

```bash
cd frontend
yarn build
# OR: npm run build

# Serve with nginx, Apache, or any static file server
# Build output is in /frontend/build
```

### Using Docker (Optional)

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine as build
WORKDIR /app
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend/ .
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  mongodb:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=service_renewal_hub
      - JWT_SECRET=${JWT_SECRET}
      - CORS_ORIGINS=http://localhost:3000
    depends_on:
      - mongodb
    ports:
      - "8001:8001"

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  mongo_data:
```

Run with: `docker-compose up -d`

---

## First-Time Setup

### 1. Create Admin Account

The **first user to register** automatically becomes an Admin.

1. Open `http://localhost:3000`
2. Click "Sign Up" tab
3. Enter your name, email, and password
4. You are now logged in as Admin

### 2. Configure Email

1. Navigate to Settings > Email
2. Select your email provider
3. Enter credentials/API keys
4. Click "Send Test Email" to verify

### 3. Customize Branding

1. Navigate to Settings > Branding
2. Set company name and tagline
3. Add logo URL (optional)
4. Choose theme mode and accent color
5. Click "Save Branding & Theme"

### 4. Add Your First Service

1. Go to Dashboard
2. Click "Add Service"
3. Fill in service details:
   - Service Name
   - Provider
   - Category
   - Expiry Date
   - Contact Name & Email
   - Annual Cost (optional)
4. Click "Add Service"

---

## API Documentation

### Authentication

All protected endpoints require Bearer token in header:
```
Authorization: Bearer <jwt_token>
```

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get token |
| GET | `/api/settings/public` | Get public branding settings |
| GET | `/api/categories` | Get service categories |

### Protected Endpoints (Requires Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user |
| GET | `/api/services` | List all services |
| POST | `/api/services` | Create service |
| GET | `/api/services/{id}` | Get service by ID |
| PUT | `/api/services/{id}` | Update service |
| DELETE | `/api/services/{id}` | Delete service |
| POST | `/api/services/{id}/send-reminder` | Send manual reminder |
| GET | `/api/dashboard/stats` | Get dashboard statistics |
| GET | `/api/email-logs` | Get email notification logs |
| POST | `/api/check-expiring` | Trigger expiry check |

### Admin Only Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings` | Get all settings |
| PUT | `/api/settings/update` | Update settings |
| POST | `/api/settings/test-email` | Send test email |
| GET | `/api/users` | List all users |
| PUT | `/api/users/{id}` | Update user (role) |
| DELETE | `/api/users/{id}` | Delete user |

### Example: Login and Create Service

```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"yourpassword"}' \
  | jq -r '.token')

# Create Service
curl -X POST "http://localhost:8001/api/services" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Adobe Creative Cloud",
    "provider": "Adobe Inc.",
    "category": "Software License",
    "expiry_date": "2025-12-31T00:00:00Z",
    "contact_email": "it@company.com",
    "contact_name": "IT Department",
    "cost": 599.99
  }'
```

---

## User Roles & Permissions

| Feature | Admin | User |
|---------|-------|------|
| View Dashboard | ✅ | ✅ |
| View Services | ✅ | ✅ |
| Add Services | ✅ | ✅ |
| Edit Services | ✅ | ✅ |
| Delete Services | ✅ | ✅ |
| Send Manual Reminders | ✅ | ❌ |
| View Notifications | ✅ | ✅ |
| Access Settings | ✅ | ❌ |
| Manage Users | ✅ | ❌ |
| Configure Email | ✅ | ❌ |
| Customize Branding | ✅ | ❌ |

---

## Troubleshooting

### Backend won't start

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Check for port conflicts
lsof -i :8001

# View backend logs
tail -f /var/log/backend.log
```

### Frontend build errors

```bash
# Clear cache and reinstall
rm -rf node_modules yarn.lock
yarn install

# Clear React cache
rm -rf .cache build
yarn start
```

### MongoDB connection issues

```bash
# Test MongoDB connection
mongosh "mongodb://localhost:27017"

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

### Email not sending

1. Check email provider credentials in Settings > Email
2. Use "Send Test Email" button to verify
3. Check backend logs for error details
4. For Gmail: Ensure App Password is used (not regular password)
5. For SMTP: Verify port and TLS settings

### JWT Token Expired

Default token expiration is 24 hours. To change:

```python
# In backend/server.py
JWT_EXPIRATION_HOURS = 72  # Change to desired hours
```

---

## Scheduled Tasks

The application runs automated tasks using APScheduler:

| Task | Schedule | Description |
|------|----------|-------------|
| Expiry Check | Daily at 9:00 AM | Checks all services and sends notifications |

To modify the schedule, edit `server.py`:

```python
scheduler.add_job(
    check_expiring_services,
    CronTrigger(hour=9, minute=0),  # Change time here
    id="daily_expiry_check",
    replace_existing=True
)
```

---

## Security Recommendations

### Production Deployment

1. **Use HTTPS**: Always deploy behind HTTPS (nginx, Cloudflare, etc.)
2. **Strong JWT Secret**: Use a cryptographically secure random string
3. **Database Security**: 
   - Enable MongoDB authentication
   - Use strong passwords
   - Restrict network access
4. **Environment Variables**: Never commit `.env` files to version control
5. **CORS**: Restrict to your domain only
6. **Rate Limiting**: Consider adding rate limiting for API endpoints

### Example Nginx Configuration

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

    # Frontend
    location / {
        root /var/www/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

For issues and feature requests, please open an issue on GitHub.

# Service Renewal Hub - PRD

## Original Problem Statement
Design a complete web application for internal service management with:
- Service Dashboard: Searchable table for organizational services (subscriptions, licenses, hardware maintenance)
- Service Entry Form: Fields for Service Name, Provider, Category, Renewal/Expiry Date, Contact Email
- Automated Expiry Logic: Backend cron job checking for upcoming expiries daily
- Email Notification System: Automated reminders at 30, 7, 1 days before expiry
- Admin Panel: Secure login to add, edit, delete services

## User Personas
1. **IT Administrator**: Primary user managing organization's service subscriptions and licenses
2. **Operations Manager**: Oversees service costs and renewal schedules
3. **System Admin**: Technical user monitoring service health and integrations

## Architecture
- **Frontend**: React + TailwindCSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT-based custom auth
- **Email**: Resend API integration

## Core Requirements (Static)
- [x] JWT-based authentication (register/login)
- [x] Service CRUD operations
- [x] Category management (8 predefined categories)
- [x] Expiry status indicators (safe/warning/danger/expired)
- [x] Dashboard statistics
- [x] Email notification system (via Resend)
- [x] Background expiry check task
- [x] Responsive dark theme UI

## What's Been Implemented (December 2024)
### Backend
- User authentication (register/login) with JWT
- **RBAC (Role-Based Access Control)**:
  - Admin role: Full access to settings, user management, all services
  - User role: Limited access (view/edit services, no settings)
  - First registered user automatically becomes admin
- Services CRUD API endpoints with contact_name field
- Dashboard statistics endpoint
- **Multi-Provider Email Support**:
  - Resend API
  - Custom SMTP
  - Gmail (with app password)
  - Outlook / Office 365
  - Microsoft Exchange
  - SendGrid
  - Mailgun
  - Yahoo Mail
  - SMTP presets auto-configure host/port for known providers
- **Settings API** (admin only):
  - Email provider configuration
  - SMTP settings (host, port, username, password, TLS)
  - Branding settings (company name, tagline, logo URL)
  - Theme settings (dark/light/system mode, accent colors)
  - Notification thresholds
  - Test email endpoint
- **Public Settings API** (no auth): Returns branding for theming
- **User Management API** (admin only)
- Professional HTML email templates
- Automated daily expiry check via APScheduler (runs at 9 AM)

### Frontend
- Login/Register page with tabs
- Dashboard with stats cards
- Services table with search and filters
- Add/Edit service modal with all fields
- **Settings Page (Admin only)** with 4 tabs:
  - **Email**: Provider dropdown, Resend API key, SMTP config, sender info, test email button
  - **Branding**: Company name, tagline, logo URL, theme mode (Dark/Light/System), accent color picker
  - **Alerts**: Configurable notification thresholds
  - **Users**: User management with role changes
- Dynamic branding in sidebar (company name, tagline, logo)
- Responsive dark theme with customizable accent colors

## Prioritized Backlog
### P0 (Critical) - Done
- [x] User authentication
- [x] Service CRUD
- [x] Dashboard display

### P1 (High Priority)
- [ ] Configure Resend API key for email functionality
- [ ] Scheduled cron job for daily expiry checks (APScheduler ready)
- [ ] Email template customization

### P2 (Medium Priority)
- [ ] Bulk import services (CSV)
- [ ] Export services report
- [ ] Service cost analytics/charts
- [ ] Multi-user role management

### P3 (Nice to Have)
- [ ] Slack/Teams integration for notifications
- [ ] Service history/audit log
- [ ] Calendar view of renewals
- [ ] Mobile app

## Next Tasks
1. User to provide Resend API key to enable email notifications
2. Set up APScheduler for automated daily expiry checks
3. Add service cost analytics dashboard

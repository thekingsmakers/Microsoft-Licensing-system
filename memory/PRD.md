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
- Services CRUD API endpoints
- Dashboard statistics endpoint
- Email notification system with Resend integration
- Manual reminder sending per service
- Expiry check background task
- Categories endpoint

### Frontend
- Login/Register page with tabs
- Dashboard with stats cards
- Services table with search and filters
- Add/Edit service modal with calendar picker
- Category and status filtering
- Email logs/notifications page
- Responsive sidebar navigation
- Dark "Cyber-Swiss" theme design

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

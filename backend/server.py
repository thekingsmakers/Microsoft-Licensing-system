from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend configuration
resend.api_key = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI(title="Service Renewal Hub")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

# Owner/Stakeholder model for services
class ServiceOwner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    role: str = "App Owner"  # App Owner, Developer, Manager, Project Manager, Other

# Reminder threshold model
class ReminderThreshold(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    days_before: int
    label: str = ""  # e.g., "First reminder", "Final warning"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str = "user"  # "admin" or "user"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

# User-defined Category model
class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: str = ""
    color: str = "#06b6d4"
    icon: str = "folder"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    color: Optional[str] = "#06b6d4"
    icon: Optional[str] = "folder"

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class AppSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "app_settings"
    # Email Provider Settings
    email_provider: str = "resend"  # "resend", "smtp", "gmail", "outlook"
    resend_api_key: str = ""
    sender_email: str = "onboarding@resend.dev"
    sender_name: str = "Service Renewal Hub"
    # SMTP Settings
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    # General Settings
    company_name: str = "Your Organization"
    notification_thresholds: List[int] = [30, 7, 1]
    # Branding Settings
    logo_url: str = ""
    company_tagline: str = "Service Management System"
    primary_color: str = "#06b6d4"
    # Theme Settings
    theme_mode: str = "dark"  # "dark", "light", "system"
    accent_color: str = "#06b6d4"
    # Metadata
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_by: str = ""

class ServiceCreate(BaseModel):
    name: str
    provider: str
    category_id: Optional[str] = None  # Reference to user-defined category
    category_name: Optional[str] = "Uncategorized"  # Fallback display name
    # Expiry settings
    expiry_date: Optional[str] = None
    expiry_duration_months: Optional[int] = None  # Alternative: set duration instead of fixed date
    # Reminder thresholds (per-service)
    reminder_thresholds: Optional[List[dict]] = None  # [{days_before: 30, label: "First reminder"}]
    # Owners/Stakeholders
    owners: Optional[List[dict]] = None  # [{name, email, role}]
    # Legacy field for backward compatibility
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = ""
    notes: Optional[str] = ""
    cost: Optional[float] = 0.0

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    expiry_date: Optional[str] = None
    expiry_duration_months: Optional[int] = None
    reminder_thresholds: Optional[List[dict]] = None
    owners: Optional[List[dict]] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[float] = None

class Service(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""  # Owner of the service record
    name: str
    provider: str
    category_id: Optional[str] = None
    category_name: str = "Uncategorized"
    expiry_date: str
    expiry_duration_months: Optional[int] = None
    # Per-service reminder thresholds
    reminder_thresholds: List[dict] = Field(default_factory=lambda: [
        {"id": str(uuid.uuid4()), "days_before": 30, "label": "First reminder"},
        {"id": str(uuid.uuid4()), "days_before": 7, "label": "Second reminder"},
        {"id": str(uuid.uuid4()), "days_before": 1, "label": "Final reminder"}
    ])
    # Multiple owners/stakeholders
    owners: List[dict] = Field(default_factory=list)  # [{id, name, email, role}]
    # Legacy fields
    contact_email: Optional[str] = None
    contact_name: str = ""
    notes: str = ""
    cost: float = 0.0
    status: str = "active"
    notifications_sent: List[str] = []  # Changed to store threshold IDs instead of days
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class NotificationLog(BaseModel):
    """Enhanced notification log with owner tracking"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    service_name: str
    threshold_id: str
    threshold_label: str
    days_until_expiry: int
    recipients: List[dict] = []  # [{email, name, status}]
    sent_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "sent"  # sent, partial, failed

class EmailLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    service_name: str
    recipient_email: str
    recipient_name: str = ""
    threshold_id: str = ""
    threshold_label: str = ""
    days_until_expiry: int
    sent_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "sent"  # sent, failed, pending

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency that requires admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_app_settings():
    """Get app settings from database or create defaults"""
    settings = await db.settings.find_one({"id": "app_settings"}, {"_id": 0})
    if not settings:
        default_settings = AppSettings()
        await db.settings.insert_one(default_settings.model_dump())
        return default_settings.model_dump()
    return settings

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # First user becomes admin
    user_count = await db.users.count_documents({})
    role = "admin" if user_count == 0 else "user"
    
    user = User(email=user_data.email, name=user_data.name, role=role)
    user_doc = user.model_dump()
    user_doc["password_hash"] = hash_password(user_data.password)
    
    await db.users.insert_one(user_doc)
    token = create_token(user.id, user.email)
    
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role}
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"], user["email"])
    return {
        "token": token,
        "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user.get("role", "user")}
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# ==================== SETTINGS ROUTES (Admin Only) ====================

@api_router.get("/settings")
async def get_settings(current_user: dict = Depends(get_admin_user)):
    settings = await get_app_settings()
    # Mask API key for security (show only last 4 chars)
    if settings.get("resend_api_key"):
        key = settings["resend_api_key"]
        settings["resend_api_key_masked"] = f"{'*' * (len(key) - 4)}{key[-4:]}" if len(key) > 4 else "****"
    return settings

@api_router.put("/settings")
async def update_settings(
    resend_api_key: Optional[str] = None,
    sender_email: Optional[str] = None,
    company_name: Optional[str] = None,
    notification_thresholds: Optional[List[int]] = None,
    current_user: dict = Depends(get_admin_user)
):
    update_data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": current_user["id"]
    }
    
    if resend_api_key is not None:
        update_data["resend_api_key"] = resend_api_key
        # Update resend API key in memory
        resend.api_key = resend_api_key
        
    if sender_email is not None:
        update_data["sender_email"] = sender_email
        
    if company_name is not None:
        update_data["company_name"] = company_name
        
    if notification_thresholds is not None:
        update_data["notification_thresholds"] = sorted(notification_thresholds, reverse=True)
    
    await db.settings.update_one(
        {"id": "app_settings"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Settings updated successfully"}

class SettingsUpdate(BaseModel):
    # Email Provider
    email_provider: Optional[str] = None
    resend_api_key: Optional[str] = None
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    # SMTP
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: Optional[bool] = None
    # General
    company_name: Optional[str] = None
    notification_thresholds: Optional[List[int]] = None
    # Branding
    logo_url: Optional[str] = None
    company_tagline: Optional[str] = None
    primary_color: Optional[str] = None
    # Theme
    theme_mode: Optional[str] = None
    accent_color: Optional[str] = None

@api_router.put("/settings/update")
async def update_settings_json(
    settings_data: SettingsUpdate,
    current_user: dict = Depends(get_admin_user)
):
    update_data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": current_user["id"]
    }
    
    # Email provider settings
    if settings_data.email_provider is not None:
        update_data["email_provider"] = settings_data.email_provider
    if settings_data.resend_api_key is not None:
        update_data["resend_api_key"] = settings_data.resend_api_key
        resend.api_key = settings_data.resend_api_key
    if settings_data.sender_email is not None:
        update_data["sender_email"] = settings_data.sender_email
    if settings_data.sender_name is not None:
        update_data["sender_name"] = settings_data.sender_name
        
    # SMTP settings
    if settings_data.smtp_host is not None:
        update_data["smtp_host"] = settings_data.smtp_host
    if settings_data.smtp_port is not None:
        update_data["smtp_port"] = settings_data.smtp_port
    if settings_data.smtp_username is not None:
        update_data["smtp_username"] = settings_data.smtp_username
    if settings_data.smtp_password is not None:
        update_data["smtp_password"] = settings_data.smtp_password
    if settings_data.smtp_use_tls is not None:
        update_data["smtp_use_tls"] = settings_data.smtp_use_tls
        
    # General settings
    if settings_data.company_name is not None:
        update_data["company_name"] = settings_data.company_name
    if settings_data.notification_thresholds is not None:
        update_data["notification_thresholds"] = sorted(settings_data.notification_thresholds, reverse=True)
    
    # Branding settings
    if settings_data.logo_url is not None:
        update_data["logo_url"] = settings_data.logo_url
    if settings_data.company_tagline is not None:
        update_data["company_tagline"] = settings_data.company_tagline
    if settings_data.primary_color is not None:
        update_data["primary_color"] = settings_data.primary_color
        
    # Theme settings
    if settings_data.theme_mode is not None:
        update_data["theme_mode"] = settings_data.theme_mode
    if settings_data.accent_color is not None:
        update_data["accent_color"] = settings_data.accent_color
    
    await db.settings.update_one(
        {"id": "app_settings"},
        {"$set": update_data},
        upsert=True
    )
    
    return {"message": "Settings updated successfully"}

# Public settings endpoint (for theme/branding - no auth required)
@api_router.get("/settings/public")
async def get_public_settings():
    settings = await get_app_settings()
    return {
        "company_name": settings.get("company_name", "Your Organization"),
        "company_tagline": settings.get("company_tagline", "Service Management System"),
        "logo_url": settings.get("logo_url", ""),
        "primary_color": settings.get("primary_color", "#06b6d4"),
        "theme_mode": settings.get("theme_mode", "dark"),
        "accent_color": settings.get("accent_color", "#06b6d4")
    }

@api_router.post("/settings/test-email")
async def test_email_settings(current_user: dict = Depends(get_admin_user)):
    """Send a test email to verify email configuration"""
    settings = await get_app_settings()
    
    test_html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background: #121214; color: #fafafa;">
        <h2 style="color: {settings.get('primary_color', '#06b6d4')};">Email Configuration Test</h2>
        <p>This is a test email from {settings.get('company_name', 'Service Renewal Hub')}.</p>
        <p>If you received this email, your email settings are configured correctly!</p>
        <hr style="border-color: #27272a;">
        <p style="color: #71717a; font-size: 12px;">
            Provider: {settings.get('email_provider', 'resend').upper()}<br>
            Sent at: {datetime.now(timezone.utc).isoformat()}
        </p>
    </div>
    """
    
    try:
        await send_email_with_provider(
            to_email=current_user["email"],
            subject=f"[Test] Email Configuration - {settings.get('company_name', 'Service Renewal Hub')}",
            html_content=test_html,
            settings=settings
        )
        return {"message": f"Test email sent to {current_user['email']}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {str(e)}")

# ==================== USER MANAGEMENT ROUTES (Admin Only) ====================

@api_router.get("/users")
async def get_users(current_user: dict = Depends(get_admin_user)):
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return users

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(get_admin_user)):
    existing = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent demoting the last admin
    if user_data.role == "user" and existing.get("role") == "admin":
        admin_count = await db.users.count_documents({"role": "admin"})
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote the last admin")
    
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    if update_data:
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    return updated

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_admin_user)):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    existing = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting the last admin
    if existing.get("role") == "admin":
        admin_count = await db.users.count_documents({"role": "admin"})
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last admin")
    
    await db.users.delete_one({"id": user_id})
    return {"message": "User deleted successfully"}

# ==================== CATEGORY ROUTES ====================

@api_router.get("/categories")
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get all categories for the current user plus system defaults"""
    user_categories = await db.categories.find(
        {"user_id": current_user["id"]}, 
        {"_id": 0}
    ).to_list(100)
    
    # Add service counts to each category
    for cat in user_categories:
        count = await db.services.count_documents({"category_id": cat["id"]})
        cat["service_count"] = count
    
    return {"categories": user_categories}

@api_router.get("/categories/with-services")
async def get_categories_with_services(current_user: dict = Depends(get_current_user)):
    """Get categories with their services for sidebar navigation"""
    user_categories = await db.categories.find(
        {"user_id": current_user["id"]}, 
        {"_id": 0}
    ).sort("name", 1).to_list(100)
    
    # Get uncategorized services
    uncategorized_services = await db.services.find(
        {"$or": [{"category_id": None}, {"category_id": ""}]},
        {"_id": 0, "id": 1, "name": 1, "status": 1, "expiry_date": 1}
    ).to_list(1000)
    
    result = []
    
    # Add user categories with their services
    for cat in user_categories:
        services = await db.services.find(
            {"category_id": cat["id"]},
            {"_id": 0, "id": 1, "name": 1, "status": 1, "expiry_date": 1}
        ).to_list(1000)
        result.append({
            **cat,
            "services": services,
            "service_count": len(services)
        })
    
    # Add uncategorized at the end if there are any
    if uncategorized_services:
        result.append({
            "id": "uncategorized",
            "name": "Uncategorized",
            "description": "Services without a category",
            "color": "#71717a",
            "icon": "inbox",
            "services": uncategorized_services,
            "service_count": len(uncategorized_services)
        })
    
    return {"categories": result}

@api_router.post("/categories")
async def create_category(category_data: CategoryCreate, current_user: dict = Depends(get_current_user)):
    # Check for duplicate name
    existing = await db.categories.find_one({
        "user_id": current_user["id"],
        "name": {"$regex": f"^{category_data.name}$", "$options": "i"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = Category(
        user_id=current_user["id"],
        **category_data.model_dump()
    )
    await db.categories.insert_one(category.model_dump())
    return category

@api_router.put("/categories/{category_id}")
async def update_category(
    category_id: str, 
    category_data: CategoryUpdate, 
    current_user: dict = Depends(get_current_user)
):
    existing = await db.categories.find_one({
        "id": category_id,
        "user_id": current_user["id"]
    }, {"_id": 0})
    
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = {k: v for k, v in category_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    if update_data:
        await db.categories.update_one({"id": category_id}, {"$set": update_data})
    
    updated = await db.categories.find_one({"id": category_id}, {"_id": 0})
    return updated

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user)):
    existing = await db.categories.find_one({
        "id": category_id,
        "user_id": current_user["id"]
    }, {"_id": 0})
    
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update services in this category to uncategorized
    await db.services.update_many(
        {"category_id": category_id},
        {"$set": {"category_id": None, "category_name": "Uncategorized"}}
    )
    
    await db.categories.delete_one({"id": category_id})
    return {"message": "Category deleted successfully"}

# ==================== SERVICE ROUTES ====================

@api_router.get("/services", response_model=List[Service])
async def get_services(current_user: dict = Depends(get_current_user)):
    services = await db.services.find({}, {"_id": 0}).to_list(1000)
    return services

@api_router.post("/services", response_model=Service)
async def create_service(service_data: ServiceCreate, current_user: dict = Depends(get_current_user)):
    service = Service(**service_data.model_dump())
    await db.services.insert_one(service.model_dump())
    return service

@api_router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: str, current_user: dict = Depends(get_current_user)):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@api_router.put("/services/{service_id}", response_model=Service)
async def update_service(service_id: str, service_data: ServiceUpdate, current_user: dict = Depends(get_current_user)):
    existing = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = {k: v for k, v in service_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.services.update_one({"id": service_id}, {"$set": update_data})
    updated = await db.services.find_one({"id": service_id}, {"_id": 0})
    return updated

@api_router.delete("/services/{service_id}")
async def delete_service(service_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.services.delete_one({"id": service_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}

# ==================== EMAIL ROUTES ====================

@api_router.get("/email-logs", response_model=List[EmailLog])
async def get_email_logs(current_user: dict = Depends(get_current_user)):
    logs = await db.email_logs.find({}, {"_id": 0}).sort("sent_at", -1).to_list(100)
    return logs

@api_router.post("/services/{service_id}/send-reminder")
async def send_manual_reminder(service_id: str, current_user: dict = Depends(get_current_user)):
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    try:
        expiry_date = datetime.fromisoformat(service["expiry_date"].replace("Z", "+00:00"))
        if expiry_date.tzinfo is None:
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        days_until = (expiry_date - datetime.now(timezone.utc)).days
        
        await send_expiry_email(service, days_until)
        return {"message": f"Reminder sent to {service['contact_email']}"}
    except Exception as e:
        logger.error(f"Failed to send reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# ==================== EXPIRY CHECK & EMAIL ====================

NOTIFICATION_THRESHOLDS = [30, 7, 1]

COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Your Organization')

# SMTP Presets for common providers
SMTP_PRESETS = {
    "gmail": {
        "host": "smtp.gmail.com",
        "port": 587,
        "use_tls": True
    },
    "outlook": {
        "host": "smtp.office365.com", 
        "port": 587,
        "use_tls": True
    },
    "exchange": {
        "host": "smtp.office365.com",
        "port": 587,
        "use_tls": True
    },
    "yahoo": {
        "host": "smtp.mail.yahoo.com",
        "port": 587,
        "use_tls": True
    },
    "sendgrid": {
        "host": "smtp.sendgrid.net",
        "port": 587,
        "use_tls": True
    },
    "mailgun": {
        "host": "smtp.mailgun.org",
        "port": 587,
        "use_tls": True
    }
}

async def send_email_with_provider(to_email: str, subject: str, html_content: str, settings: dict):
    """Send email using the configured provider"""
    provider = settings.get("email_provider", "resend")
    sender_email = settings.get("sender_email", SENDER_EMAIL)
    sender_name = settings.get("sender_name", "Service Renewal Hub")
    
    if provider == "resend":
        # Use Resend API
        db_api_key = settings.get("resend_api_key", "")
        if db_api_key:
            resend.api_key = db_api_key
        
        params = {
            "from": f"{sender_name} <{sender_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        return await asyncio.to_thread(resend.Emails.send, params)
    
    else:
        # Use SMTP (works for smtp, gmail, outlook, exchange, etc.)
        smtp_host = settings.get("smtp_host", "")
        smtp_port = settings.get("smtp_port", 587)
        smtp_username = settings.get("smtp_username", "")
        smtp_password = settings.get("smtp_password", "")
        use_tls = settings.get("smtp_use_tls", True)
        
        # Apply presets for known providers
        if provider in SMTP_PRESETS:
            preset = SMTP_PRESETS[provider]
            smtp_host = smtp_host or preset["host"]
            smtp_port = smtp_port or preset["port"]
            use_tls = preset["use_tls"]
        
        if not smtp_host or not smtp_username or not smtp_password:
            raise ValueError(f"SMTP settings incomplete for provider: {provider}")
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Send via SMTP
        if use_tls:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_username,
                password=smtp_password,
                start_tls=True
            )
        else:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                username=smtp_username,
                password=smtp_password,
                use_tls=False
            )
        
        return {"id": "smtp_sent", "status": "sent"}

async def send_expiry_email(service: dict, days_until_expiry: int):
    # Get settings from database
    settings = await get_app_settings()
    sender_email = settings.get("sender_email", SENDER_EMAIL)
    company_name = settings.get("company_name", COMPANY_NAME)
    
    # Update resend API key if set in database
    db_api_key = settings.get("resend_api_key", "")
    if db_api_key:
        resend.api_key = db_api_key
    
    urgency = "URGENT" if days_until_expiry <= 1 else "WARNING" if days_until_expiry <= 7 else "REMINDER"
    urgency_text = "expiring TODAY" if days_until_expiry <= 0 else f"expiring in {days_until_expiry} day(s)"
    color = "#ef4444" if days_until_expiry <= 1 else "#f59e0b" if days_until_expiry <= 7 else "#06b6d4"
    btn_color = "#dc2626" if days_until_expiry <= 1 else "#d97706" if days_until_expiry <= 7 else "#0891b2"
    
    contact_name = service.get('contact_name', '').strip() or "Team"
    expiry_date_formatted = service['expiry_date'][:10]
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #0a0a0b; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0b;">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #121214; border-radius: 8px; overflow: hidden;">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, {color}22 0%, {color}05 100%); padding: 32px 40px; border-bottom: 1px solid #27272a;">
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td>
                                            <div style="display: inline-block; background-color: {color}20; border: 1px solid {color}40; border-radius: 4px; padding: 8px 12px; margin-bottom: 16px;">
                                                <span style="color: {color}; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{urgency}</span>
                                            </div>
                                            <h1 style="margin: 0; color: #fafafa; font-size: 24px; font-weight: 700;">
                                                Service {urgency_text}!
                                            </h1>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 24px 0; color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Dear {contact_name},
                                </p>
                                <p style="margin: 0 0 32px 0; color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    This is a reminder that the service <strong style="color: #fafafa;">{service['name']}</strong> is {urgency_text}.
                                </p>
                                
                                <!-- Service Details Card -->
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #1a1a1c; border-radius: 6px; border-left: 4px solid {color}; margin-bottom: 32px;">
                                    <tr>
                                        <td style="padding: 24px;">
                                            <h2 style="margin: 0 0 20px 0; color: #fafafa; font-size: 18px; font-weight: 600;">
                                                Service Details
                                            </h2>
                                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                                <tr>
                                                    <td style="padding: 10px 0; color: #71717a; font-size: 14px; width: 140px;">Service Name:</td>
                                                    <td style="padding: 10px 0; color: #fafafa; font-size: 14px; font-weight: 500;">{service['name']}</td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 10px 0; color: #71717a; font-size: 14px; border-top: 1px solid #27272a;">Expiry Date:</td>
                                                    <td style="padding: 10px 0; color: {color}; font-size: 14px; font-weight: 700; border-top: 1px solid #27272a;">{expiry_date_formatted}</td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 10px 0; color: #71717a; font-size: 14px; border-top: 1px solid #27272a;">Provider:</td>
                                                    <td style="padding: 10px 0; color: #fafafa; font-size: 14px; border-top: 1px solid #27272a;">{service['provider']}</td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 10px 0; color: #71717a; font-size: 14px; border-top: 1px solid #27272a;">Category:</td>
                                                    <td style="padding: 10px 0; color: #fafafa; font-size: 14px; border-top: 1px solid #27272a;">{service['category']}</td>
                                                </tr>
                                                <tr>
                                                    <td style="padding: 10px 0; color: #71717a; font-size: 14px; border-top: 1px solid #27272a;">Days Remaining:</td>
                                                    <td style="padding: 10px 0; color: {color}; font-size: 18px; font-weight: 700; border-top: 1px solid #27272a;">{days_until_expiry} day(s)</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin: 0 0 32px 0; color: #a1a1aa; font-size: 16px; line-height: 1.6;">
                                    Please take action to renew or contact the service provider as soon as possible to avoid any service interruption.
                                </p>
                                
                                <!-- CTA Button -->
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center">
                                            <a href="#" style="display: inline-block; background-color: {btn_color}; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 4px; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                                Renew Now →
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #0a0a0b; padding: 24px 40px; border-top: 1px solid #27272a;">
                                <p style="margin: 0 0 8px 0; color: #71717a; font-size: 14px; text-align: center;">
                                    Best regards,
                                </p>
                                <p style="margin: 0 0 16px 0; color: #a1a1aa; font-size: 14px; font-weight: 600; text-align: center;">
                                    The {company_name} Service Management Team
                                </p>
                                <p style="margin: 0; color: #52525b; font-size: 12px; text-align: center;">
                                    This is an automated notification from Service Renewal Hub
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    subject = f"Reminder: Service \"{service['name']}\" is Expiring Soon!"
    if days_until_expiry <= 1:
        subject = f"URGENT: Service \"{service['name']}\" expires {'TODAY' if days_until_expiry <= 0 else 'TOMORROW'}!"
    elif days_until_expiry <= 7:
        subject = f"WARNING: Service \"{service['name']}\" expires in {days_until_expiry} days!"
    
    try:
        await send_email_with_provider(
            to_email=service["contact_email"],
            subject=subject,
            html_content=html_content,
            settings=settings
        )
        
        # Log the email
        email_log = EmailLog(
            service_id=service["id"],
            service_name=service["name"],
            recipient_email=service["contact_email"],
            days_until_expiry=days_until_expiry
        )
        await db.email_logs.insert_one(email_log.model_dump())
        
        logger.info(f"Email sent to {service['contact_email']} for service {service['name']}")
        return {"status": "sent"}
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise

async def check_expiring_services():
    """Check for expiring services and send notifications"""
    logger.info("Running expiry check...")
    
    # Get notification thresholds from settings
    settings = await get_app_settings()
    thresholds = settings.get("notification_thresholds", NOTIFICATION_THRESHOLDS)
    
    services = await db.services.find({"status": "active"}, {"_id": 0}).to_list(1000)
    now = datetime.now(timezone.utc)
    
    for service in services:
        try:
            expiry_str = service.get("expiry_date", "")
            if not expiry_str:
                continue
                
            expiry_date = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                
            days_until = (expiry_date - now).days
            notifications_sent = service.get("notifications_sent", [])
            
            for threshold in thresholds:
                if days_until <= threshold and threshold not in notifications_sent:
                    try:
                        await send_expiry_email(service, days_until)
                        notifications_sent.append(threshold)
                        await db.services.update_one(
                            {"id": service["id"]},
                            {"$set": {"notifications_sent": notifications_sent}}
                        )
                        logger.info(f"Sent {threshold}-day notification for {service['name']}")
                    except Exception as e:
                        logger.error(f"Failed to send notification for {service['name']}: {str(e)}")
                    break
                    
        except Exception as e:
            logger.error(f"Error processing service {service.get('name', 'unknown')}: {str(e)}")
    
    logger.info("Expiry check completed")

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    services = await db.services.find({"status": "active"}, {"_id": 0}).to_list(1000)
    now = datetime.now(timezone.utc)
    
    total = len(services)
    expiring_soon = 0
    expired = 0
    safe = 0
    categories = {}
    total_cost = 0
    
    for service in services:
        try:
            expiry_str = service.get("expiry_date", "")
            if not expiry_str:
                continue
                
            expiry_date = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                
            days_until = (expiry_date - now).days
            
            if days_until < 0:
                expired += 1
            elif days_until <= 30:
                expiring_soon += 1
            else:
                safe += 1
            
            cat = service.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1
            total_cost += service.get("cost", 0)
            
        except Exception as e:
            logger.error(f"Error calculating stats for service: {str(e)}")
    
    return {
        "total": total,
        "expiring_soon": expiring_soon,
        "expired": expired,
        "safe": safe,
        "categories": categories,
        "total_cost": total_cost
    }

@api_router.post("/check-expiring")
async def trigger_expiry_check(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    background_tasks.add_task(check_expiring_services)
    return {"message": "Expiry check triggered"}

# ==================== CATEGORIES ====================

CATEGORIES = [
    "Software License",
    "Hardware Maintenance", 
    "Cloud Subscription",
    "SaaS",
    "Domain/Hosting",
    "Insurance",
    "Support Contract",
    "Other"
]

@api_router.get("/categories")
async def get_categories():
    return {"categories": CATEGORIES}

# ==================== HEALTH CHECK ====================

@api_router.get("/")
async def root():
    return {"message": "Service Renewal Hub API", "status": "healthy"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scheduler for automated expiry checks
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Run expiry check daily at 9 AM
    scheduler.add_job(
        check_expiring_services,
        CronTrigger(hour=9, minute=0),
        id="daily_expiry_check",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started - daily expiry check scheduled at 9:00 AM")

@app.on_event("shutdown")
async def shutdown_db_client():
    scheduler.shutdown()
    client.close()

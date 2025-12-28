import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth, API, useTheme } from "../App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Separator } from "./ui/separator";
import { Switch } from "./ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./ui/alert-dialog";
import { toast } from "sonner";
import { 
  Mail, 
  Users, 
  Bell,
  Save,
  Loader2,
  Shield,
  User,
  Trash2,
  Eye,
  EyeOff,
  Building2,
  Key,
  Palette,
  Image,
  Server,
  Send,
  Sun,
  Moon,
  Monitor
} from "lucide-react";
import { format, parseISO } from "date-fns";

const EMAIL_PROVIDERS = [
  { value: "resend", label: "Resend", icon: "✉️" },
  { value: "smtp", label: "Custom SMTP", icon: "📧" },
  { value: "gmail", label: "Gmail", icon: "📮" },
  { value: "outlook", label: "Outlook / Office 365", icon: "📨" },
  { value: "exchange", label: "Microsoft Exchange", icon: "🏢" },
  { value: "sendgrid", label: "SendGrid", icon: "📬" },
  { value: "mailgun", label: "Mailgun", icon: "📭" },
  { value: "yahoo", label: "Yahoo Mail", icon: "📪" },
];

const THEME_COLORS = [
  { value: "#06b6d4", label: "Cyan", class: "bg-cyan-500" },
  { value: "#8b5cf6", label: "Violet", class: "bg-violet-500" },
  { value: "#10b981", label: "Emerald", class: "bg-emerald-500" },
  { value: "#f59e0b", label: "Amber", class: "bg-amber-500" },
  { value: "#ef4444", label: "Red", class: "bg-red-500" },
  { value: "#ec4899", label: "Pink", class: "bg-pink-500" },
  { value: "#3b82f6", label: "Blue", class: "bg-blue-500" },
  { value: "#84cc16", label: "Lime", class: "bg-lime-500" },
];

const Settings = () => {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);
  const [settings, setSettings] = useState({
    // Email Provider
    email_provider: "resend",
    resend_api_key: "",
    resend_api_key_masked: "",
    sender_email: "",
    sender_name: "",
    // SMTP
    smtp_host: "",
    smtp_port: 587,
    smtp_username: "",
    smtp_password: "",
    smtp_use_tls: true,
    // General
    company_name: "",
    notification_thresholds: [30, 7, 1],
    // Branding
    logo_url: "",
    company_tagline: "",
    primary_color: "#06b6d4",
    // Theme
    theme_mode: "dark",
    accent_color: "#06b6d4"
  });
  const [showApiKey, setShowApiKey] = useState(false);
  const [showSmtpPassword, setShowSmtpPassword] = useState(false);
  const [users, setUsers] = useState([]);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, user: null });

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchSettings();
    fetchUsers();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`, { headers });
      setSettings(prev => ({
        ...prev,
        ...response.data,
        resend_api_key: "", // Don't show actual key
        smtp_password: "" // Don't show actual password
      }));
    } catch (error) {
      if (error.response?.status === 403) {
        toast.error("Admin access required");
      } else {
        toast.error("Failed to fetch settings");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`, { headers });
      setUsers(response.data);
    } catch (error) {
      console.error("Failed to fetch users");
    }
  };

  const handleSaveSettings = async (section) => {
    setSaving(true);
    try {
      let updateData = {};
      
      if (section === "email") {
        updateData = {
          email_provider: settings.email_provider,
          sender_email: settings.sender_email,
          sender_name: settings.sender_name,
        };
        
        if (settings.email_provider === "resend" && settings.resend_api_key) {
          updateData.resend_api_key = settings.resend_api_key;
        }
        
        if (settings.email_provider !== "resend") {
          updateData.smtp_host = settings.smtp_host;
          updateData.smtp_port = settings.smtp_port;
          updateData.smtp_username = settings.smtp_username;
          updateData.smtp_use_tls = settings.smtp_use_tls;
          if (settings.smtp_password) {
            updateData.smtp_password = settings.smtp_password;
          }
        }
      } else if (section === "notifications") {
        updateData = {
          notification_thresholds: settings.notification_thresholds
        };
      } else if (section === "branding") {
        updateData = {
          company_name: settings.company_name,
          company_tagline: settings.company_tagline,
          logo_url: settings.logo_url,
          primary_color: settings.primary_color,
          theme_mode: settings.theme_mode,
          accent_color: settings.accent_color
        };
      }
      
      await axios.put(`${API}/settings/update`, updateData, { headers });
      toast.success("Settings saved successfully");
      
      // Clear sensitive fields and refresh
      setSettings(prev => ({ ...prev, resend_api_key: "", smtp_password: "" }));
      fetchSettings();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleTestEmail = async () => {
    setTestingEmail(true);
    try {
      await axios.post(`${API}/settings/test-email`, {}, { headers });
      toast.success("Test email sent! Check your inbox.");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to send test email");
    } finally {
      setTestingEmail(false);
    }
  };

  const handleUpdateUserRole = async (userId, newRole) => {
    try {
      await axios.put(`${API}/users/${userId}`, { role: newRole }, { headers });
      toast.success("User role updated");
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update user");
    }
  };

  const handleDeleteUser = async () => {
    if (!deleteDialog.user) return;
    try {
      await axios.delete(`${API}/users/${deleteDialog.user.id}`, { headers });
      toast.success("User deleted");
      setDeleteDialog({ open: false, user: null });
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete user");
    }
  };

  const handleThresholdChange = (index, value) => {
    const newThresholds = [...settings.notification_thresholds];
    newThresholds[index] = parseInt(value) || 0;
    setSettings({ ...settings, notification_thresholds: newThresholds.sort((a, b) => b - a) });
  };

  const showSmtpFields = settings.email_provider !== "resend";

  if (loading) {
    return (
      <div className="animate-enter flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="animate-enter" data-testid="settings-page">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage application settings, branding, and user access
        </p>
      </div>

      <Tabs defaultValue="email" className="space-y-6">
        <TabsList className="grid w-full max-w-2xl grid-cols-4">
          <TabsTrigger value="email" data-testid="email-settings-tab">
            <Mail className="h-4 w-4 mr-2" />
            Email
          </TabsTrigger>
          <TabsTrigger value="branding" data-testid="branding-settings-tab">
            <Palette className="h-4 w-4 mr-2" />
            Branding
          </TabsTrigger>
          <TabsTrigger value="notifications" data-testid="notification-settings-tab">
            <Bell className="h-4 w-4 mr-2" />
            Alerts
          </TabsTrigger>
          <TabsTrigger value="users" data-testid="users-settings-tab">
            <Users className="h-4 w-4 mr-2" />
            Users
          </TabsTrigger>
        </TabsList>

        {/* Email Settings */}
        <TabsContent value="email">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-primary" />
                Email Configuration
              </CardTitle>
              <CardDescription>
                Configure email service for automated notifications. Supports Resend, SMTP, Gmail, Outlook, and more.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Email Provider */}
              <div className="space-y-2">
                <Label className="label-uppercase flex items-center gap-2">
                  <Server className="h-3.5 w-3.5" />
                  Email Provider
                </Label>
                <Select 
                  value={settings.email_provider} 
                  onValueChange={(value) => setSettings({ ...settings, email_provider: value })}
                >
                  <SelectTrigger className="w-full max-w-md" data-testid="email-provider-select">
                    <SelectValue placeholder="Select email provider" />
                  </SelectTrigger>
                  <SelectContent>
                    {EMAIL_PROVIDERS.map(provider => (
                      <SelectItem key={provider.value} value={provider.value}>
                        <span className="flex items-center gap-2">
                          <span>{provider.icon}</span>
                          {provider.label}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              {/* Resend API Key - Only show for Resend provider */}
              {settings.email_provider === "resend" && (
                <div className="space-y-2">
                  <Label htmlFor="resend_api_key" className="label-uppercase flex items-center gap-2">
                    <Key className="h-3.5 w-3.5" />
                    Resend API Key
                  </Label>
                  <div className="flex gap-2 max-w-md">
                    <div className="relative flex-1">
                      <Input
                        id="resend_api_key"
                        type={showApiKey ? "text" : "password"}
                        placeholder={settings.resend_api_key_masked || "Enter your Resend API key (re_...)"}
                        value={settings.resend_api_key}
                        onChange={(e) => setSettings({ ...settings, resend_api_key: e.target.value })}
                        className="bg-background pr-10"
                        data-testid="resend-api-key-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Get your API key from{" "}
                    <a href="https://resend.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                      resend.com/api-keys
                    </a>
                  </p>
                </div>
              )}

              {/* SMTP Settings - Show for non-Resend providers */}
              {showSmtpFields && (
                <div className="space-y-4 p-4 rounded-sm bg-muted/30 border border-border">
                  <h4 className="font-medium flex items-center gap-2">
                    <Server className="h-4 w-4 text-primary" />
                    SMTP Configuration
                    {settings.email_provider !== "smtp" && (
                      <span className="text-xs text-muted-foreground ml-2">
                        (Pre-configured for {EMAIL_PROVIDERS.find(p => p.value === settings.email_provider)?.label})
                      </span>
                    )}
                  </h4>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="smtp_host" className="label-uppercase">SMTP Host</Label>
                      <Input
                        id="smtp_host"
                        placeholder={settings.email_provider === "gmail" ? "smtp.gmail.com" : 
                                   settings.email_provider === "outlook" ? "smtp.office365.com" : "smtp.example.com"}
                        value={settings.smtp_host}
                        onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
                        className="bg-background"
                        data-testid="smtp-host-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="smtp_port" className="label-uppercase">Port</Label>
                      <Input
                        id="smtp_port"
                        type="number"
                        placeholder="587"
                        value={settings.smtp_port}
                        onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) || 587 })}
                        className="bg-background"
                        data-testid="smtp-port-input"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="smtp_username" className="label-uppercase">Username / Email</Label>
                      <Input
                        id="smtp_username"
                        placeholder="your-email@example.com"
                        value={settings.smtp_username}
                        onChange={(e) => setSettings({ ...settings, smtp_username: e.target.value })}
                        className="bg-background"
                        data-testid="smtp-username-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="smtp_password" className="label-uppercase">Password / App Password</Label>
                      <div className="relative">
                        <Input
                          id="smtp_password"
                          type={showSmtpPassword ? "text" : "password"}
                          placeholder="••••••••"
                          value={settings.smtp_password}
                          onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
                          className="bg-background pr-10"
                          data-testid="smtp-password-input"
                        />
                        <button
                          type="button"
                          onClick={() => setShowSmtpPassword(!showSmtpPassword)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {showSmtpPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Switch
                      id="smtp_use_tls"
                      checked={settings.smtp_use_tls}
                      onCheckedChange={(checked) => setSettings({ ...settings, smtp_use_tls: checked })}
                    />
                    <Label htmlFor="smtp_use_tls">Use TLS/STARTTLS (recommended)</Label>
                  </div>
                  
                  {settings.email_provider === "gmail" && (
                    <p className="text-xs text-amber-500 mt-2">
                      For Gmail, use an App Password instead of your regular password.{" "}
                      <a href="https://support.google.com/accounts/answer/185833" target="_blank" rel="noopener noreferrer" className="underline">
                        Learn how to create one
                      </a>
                    </p>
                  )}
                </div>
              )}

              <Separator />

              {/* Sender Info */}
              <div className="grid grid-cols-2 gap-4 max-w-2xl">
                <div className="space-y-2">
                  <Label htmlFor="sender_email" className="label-uppercase flex items-center gap-2">
                    <Mail className="h-3.5 w-3.5" />
                    Sender Email
                  </Label>
                  <Input
                    id="sender_email"
                    type="email"
                    placeholder="notifications@yourdomain.com"
                    value={settings.sender_email}
                    onChange={(e) => setSettings({ ...settings, sender_email: e.target.value })}
                    className="bg-background"
                    data-testid="sender-email-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sender_name" className="label-uppercase">Sender Name</Label>
                  <Input
                    id="sender_name"
                    placeholder="Service Renewal Hub"
                    value={settings.sender_name}
                    onChange={(e) => setSettings({ ...settings, sender_name: e.target.value })}
                    className="bg-background"
                    data-testid="sender-name-input"
                  />
                </div>
              </div>

              <div className="pt-4 flex gap-3">
                <Button
                  onClick={() => handleSaveSettings("email")}
                  disabled={saving}
                  className="btn-primary"
                  data-testid="save-email-settings-btn"
                >
                  {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                  Save Email Settings
                </Button>
                <Button
                  variant="outline"
                  onClick={handleTestEmail}
                  disabled={testingEmail}
                  data-testid="test-email-btn"
                >
                  {testingEmail ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
                  Send Test Email
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Branding & Theme Settings */}
        <TabsContent value="branding">
          <div className="grid gap-6">
            {/* Branding */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-primary" />
                  Company Branding
                </CardTitle>
                <CardDescription>
                  Customize your organization's branding across the application and email notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4 max-w-2xl">
                  <div className="space-y-2">
                    <Label htmlFor="company_name" className="label-uppercase">Company Name</Label>
                    <Input
                      id="company_name"
                      placeholder="Your Organization"
                      value={settings.company_name}
                      onChange={(e) => setSettings({ ...settings, company_name: e.target.value })}
                      className="bg-background"
                      data-testid="company-name-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="company_tagline" className="label-uppercase">Tagline</Label>
                    <Input
                      id="company_tagline"
                      placeholder="Service Management System"
                      value={settings.company_tagline}
                      onChange={(e) => setSettings({ ...settings, company_tagline: e.target.value })}
                      className="bg-background"
                      data-testid="company-tagline-input"
                    />
                  </div>
                </div>
                
                <div className="space-y-2 max-w-2xl">
                  <Label htmlFor="logo_url" className="label-uppercase flex items-center gap-2">
                    <Image className="h-3.5 w-3.5" />
                    Logo URL
                  </Label>
                  <Input
                    id="logo_url"
                    placeholder="https://example.com/logo.png"
                    value={settings.logo_url}
                    onChange={(e) => setSettings({ ...settings, logo_url: e.target.value })}
                    className="bg-background"
                    data-testid="logo-url-input"
                  />
                  <p className="text-xs text-muted-foreground">
                    Recommended: Square image, at least 128x128 pixels, PNG or SVG format
                  </p>
                </div>

                {settings.logo_url && (
                  <div className="p-4 rounded-sm bg-muted/30 border border-border inline-block">
                    <p className="text-xs text-muted-foreground mb-2">Preview:</p>
                    <img 
                      src={settings.logo_url} 
                      alt="Logo preview" 
                      className="h-12 w-auto object-contain"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Theme */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5 text-primary" />
                  Theme Customization
                </CardTitle>
                <CardDescription>
                  Customize the application's appearance and color scheme
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Theme Mode */}
                <div className="space-y-3">
                  <Label className="label-uppercase">Theme Mode</Label>
                  <div className="flex gap-3">
                    {[
                      { value: "dark", label: "Dark", icon: Moon },
                      { value: "light", label: "Light", icon: Sun },
                      { value: "system", label: "System", icon: Monitor }
                    ].map(({ value, label, icon: Icon }) => (
                      <button
                        key={value}
                        onClick={() => setSettings({ ...settings, theme_mode: value })}
                        className={`flex items-center gap-2 px-4 py-2 rounded-sm border transition-all ${
                          settings.theme_mode === value
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-border hover:border-primary/50"
                        }`}
                        data-testid={`theme-${value}-btn`}
                      >
                        <Icon className="h-4 w-4" />
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Accent Color */}
                <div className="space-y-3">
                  <Label className="label-uppercase">Primary Accent Color</Label>
                  <div className="flex flex-wrap gap-3">
                    {THEME_COLORS.map(({ value, label, class: bgClass }) => (
                      <button
                        key={value}
                        onClick={() => setSettings({ ...settings, primary_color: value, accent_color: value })}
                        className={`relative h-10 w-10 rounded-sm ${bgClass} transition-all hover:scale-110 ${
                          settings.primary_color === value ? "ring-2 ring-offset-2 ring-offset-background ring-white" : ""
                        }`}
                        title={label}
                        data-testid={`color-${label.toLowerCase()}-btn`}
                      >
                        {settings.primary_color === value && (
                          <span className="absolute inset-0 flex items-center justify-center text-white font-bold">✓</span>
                        )}
                      </button>
                    ))}
                    <div className="flex items-center gap-2 ml-4">
                      <Label className="text-sm text-muted-foreground">Custom:</Label>
                      <Input
                        type="color"
                        value={settings.primary_color}
                        onChange={(e) => setSettings({ ...settings, primary_color: e.target.value, accent_color: e.target.value })}
                        className="h-10 w-14 p-1 cursor-pointer"
                        data-testid="custom-color-input"
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <Button
                    onClick={() => handleSaveSettings("branding")}
                    disabled={saving}
                    className="btn-primary"
                    data-testid="save-branding-settings-btn"
                  >
                    {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                    Save Branding & Theme
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-primary" />
                Notification Thresholds
              </CardTitle>
              <CardDescription>
                Configure when reminder emails should be sent before service expiry
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-3 gap-4 max-w-xl">
                {settings.notification_thresholds.map((threshold, index) => (
                  <div key={index} className="space-y-2">
                    <Label className="label-uppercase">
                      {index === 0 ? "First Reminder" : index === 1 ? "Second Reminder" : "Final Reminder"}
                    </Label>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        min="1"
                        max="365"
                        value={threshold}
                        onChange={(e) => handleThresholdChange(index, e.target.value)}
                        className="bg-background"
                        data-testid={`threshold-${index}-input`}
                      />
                      <span className="text-sm text-muted-foreground whitespace-nowrap">days</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-sm bg-muted/30 border border-border max-w-xl">
                <p className="text-sm text-muted-foreground">
                  Emails will be sent at <strong className="text-foreground">{settings.notification_thresholds.join(", ")}</strong> days before a service expires. 
                  The daily check runs automatically at 9:00 AM.
                </p>
              </div>

              <div className="pt-4">
                <Button
                  onClick={() => handleSaveSettings("notifications")}
                  disabled={saving}
                  className="btn-primary"
                  data-testid="save-notification-settings-btn"
                >
                  {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
                  Save Notification Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* User Management */}
        <TabsContent value="users">
          <Card className="bg-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                User Management
              </CardTitle>
              <CardDescription>
                Manage user accounts and roles. Admins have full access, users have limited permissions.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-border hover:bg-transparent">
                      <TableHead className="table-header">User</TableHead>
                      <TableHead className="table-header">Email</TableHead>
                      <TableHead className="table-header">Role</TableHead>
                      <TableHead className="table-header">Joined</TableHead>
                      <TableHead className="table-header text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((u) => (
                      <TableRow key={u.id} className="border-border hover:bg-white/5" data-testid={`user-row-${u.id}`}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                              <span className="text-sm font-medium text-primary">
                                {u.name?.charAt(0).toUpperCase() || "U"}
                              </span>
                            </div>
                            <div>
                              <p className="font-medium">{u.name}</p>
                              {u.id === user?.id && (
                                <span className="text-xs text-muted-foreground">(You)</span>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{u.email}</TableCell>
                        <TableCell>
                          <Select
                            value={u.role || "user"}
                            onValueChange={(value) => handleUpdateUserRole(u.id, value)}
                            disabled={u.id === user?.id}
                          >
                            <SelectTrigger className="w-28 h-8" data-testid={`role-select-${u.id}`}>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="admin">
                                <div className="flex items-center gap-2">
                                  <Shield className="h-3.5 w-3.5 text-primary" />
                                  Admin
                                </div>
                              </SelectItem>
                              <SelectItem value="user">
                                <div className="flex items-center gap-2">
                                  <User className="h-3.5 w-3.5" />
                                  User
                                </div>
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell className="text-muted-foreground font-mono text-sm">
                          {u.created_at ? format(parseISO(u.created_at), "MMM d, yyyy") : "-"}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground hover:text-destructive"
                            onClick={() => setDeleteDialog({ open: true, user: u })}
                            disabled={u.id === user?.id}
                            data-testid={`delete-user-${u.id}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="mt-6 p-4 rounded-sm bg-muted/30 border border-border">
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-primary" />
                  Role Permissions
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-primary mb-1">Admin</p>
                    <ul className="text-muted-foreground space-y-1">
                      <li>• Full access to all services</li>
                      <li>• Manage application settings</li>
                      <li>• Manage users and roles</li>
                      <li>• Configure email & branding</li>
                    </ul>
                  </div>
                  <div>
                    <p className="font-medium mb-1">User</p>
                    <ul className="text-muted-foreground space-y-1">
                      <li>• View all services</li>
                      <li>• Add and edit services</li>
                      <li>• View notifications</li>
                      <li>• No access to settings</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete User Dialog */}
      <AlertDialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, user: null })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteDialog.user?.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteUser} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Settings;

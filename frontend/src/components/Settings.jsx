import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Separator } from "./ui/separator";
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
  Settings as SettingsIcon, 
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
  Key
} from "lucide-react";
import { format, parseISO } from "date-fns";

const Settings = () => {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    resend_api_key: "",
    sender_email: "",
    company_name: "",
    notification_thresholds: [30, 7, 1]
  });
  const [showApiKey, setShowApiKey] = useState(false);
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
      setSettings({
        resend_api_key: "",
        sender_email: response.data.sender_email || "",
        company_name: response.data.company_name || "",
        notification_thresholds: response.data.notification_thresholds || [30, 7, 1],
        resend_api_key_masked: response.data.resend_api_key_masked || ""
      });
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

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const updateData = {
        sender_email: settings.sender_email,
        company_name: settings.company_name,
        notification_thresholds: settings.notification_thresholds
      };
      
      // Only include API key if changed
      if (settings.resend_api_key) {
        updateData.resend_api_key = settings.resend_api_key;
      }
      
      await axios.put(`${API}/settings/update`, updateData, { headers });
      toast.success("Settings saved successfully");
      
      // Clear the raw API key and refresh masked version
      setSettings(prev => ({ ...prev, resend_api_key: "" }));
      fetchSettings();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to save settings");
    } finally {
      setSaving(false);
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
          Manage application settings and user access
        </p>
      </div>

      <Tabs defaultValue="email" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="email" data-testid="email-settings-tab">
            <Mail className="h-4 w-4 mr-2" />
            Email
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
                Configure email service settings for automated notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Resend API Key */}
              <div className="space-y-2">
                <Label htmlFor="resend_api_key" className="label-uppercase flex items-center gap-2">
                  <Key className="h-3.5 w-3.5" />
                  Resend API Key
                </Label>
                <div className="flex gap-2">
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
                  <a 
                    href="https://resend.com/api-keys" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    resend.com/api-keys
                  </a>
                </p>
              </div>

              <Separator />

              {/* Sender Email */}
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
                <p className="text-xs text-muted-foreground">
                  Email address that will appear as the sender. Must be verified in Resend.
                </p>
              </div>

              <Separator />

              {/* Company Name */}
              <div className="space-y-2">
                <Label htmlFor="company_name" className="label-uppercase flex items-center gap-2">
                  <Building2 className="h-3.5 w-3.5" />
                  Company Name
                </Label>
                <Input
                  id="company_name"
                  type="text"
                  placeholder="Your Organization"
                  value={settings.company_name}
                  onChange={(e) => setSettings({ ...settings, company_name: e.target.value })}
                  className="bg-background"
                  data-testid="company-name-input"
                />
                <p className="text-xs text-muted-foreground">
                  This name will appear in email notifications
                </p>
              </div>

              <div className="pt-4">
                <Button
                  onClick={handleSaveSettings}
                  disabled={saving}
                  className="btn-primary"
                  data-testid="save-email-settings-btn"
                >
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
                  Save Email Settings
                </Button>
              </div>
            </CardContent>
          </Card>
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
              <div className="grid grid-cols-3 gap-4">
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
                      <span className="text-sm text-muted-foreground whitespace-nowrap">days before</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-sm bg-muted/30 border border-border">
                <p className="text-sm text-muted-foreground">
                  Emails will be sent at <strong className="text-foreground">{settings.notification_thresholds.join(", ")}</strong> days before a service expires. 
                  The daily check runs automatically at 9:00 AM.
                </p>
              </div>

              <div className="pt-4">
                <Button
                  onClick={handleSaveSettings}
                  disabled={saving}
                  className="btn-primary"
                  data-testid="save-notification-settings-btn"
                >
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
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
                      <TableRow 
                        key={u.id} 
                        className="border-border hover:bg-white/5"
                        data-testid={`user-row-${u.id}`}
                      >
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
                        <TableCell className="text-muted-foreground">
                          {u.email}
                        </TableCell>
                        <TableCell>
                          <Select
                            value={u.role || "user"}
                            onValueChange={(value) => handleUpdateUserRole(u.id, value)}
                            disabled={u.id === user?.id}
                          >
                            <SelectTrigger 
                              className="w-28 h-8"
                              data-testid={`role-select-${u.id}`}
                            >
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
                      <li>• Send manual reminders</li>
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
      <AlertDialog 
        open={deleteDialog.open} 
        onOpenChange={(open) => setDeleteDialog({ open, user: null })}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deleteDialog.user?.name}"? 
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={handleDeleteUser}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Settings;

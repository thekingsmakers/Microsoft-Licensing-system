import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import { Button } from "./ui/button";
import { 
  Shield, 
  LayoutDashboard, 
  Bell, 
  LogOut,
  Menu,
  X,
  Settings
} from "lucide-react";
import { useState } from "react";

const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isAdmin = user?.role === "admin";

  const navItems = [
    { path: "/", label: "Dashboard", icon: LayoutDashboard, adminOnly: false },
    { path: "/notifications", label: "Notifications", icon: Bell, adminOnly: false },
    { path: "/settings", label: "Settings", icon: Settings, adminOnly: true },
  ];

  const filteredNavItems = navItems.filter(item => !item.adminOnly || isAdmin);

  const NavContent = () => (
    <>
      {/* Logo */}
      <div className="flex items-center gap-3 p-6 border-b border-white/10">
        <div className="p-2 rounded-sm bg-primary/10 border border-primary/20">
          <Shield className="h-6 w-6 text-primary" strokeWidth={1.5} />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-tight">Renewal Hub</h1>
          <p className="text-xs text-muted-foreground">Service Manager</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-1">
          {filteredNavItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-sm text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                }`
              }
              data-testid={`nav-${label.toLowerCase()}`}
            >
              <Icon className="h-5 w-5" strokeWidth={1.5} />
              {label}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="text-sm font-medium text-primary">
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              {isAdmin && (
                <span className="px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider bg-primary/20 text-primary rounded">
                  Admin
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          onClick={handleLogout}
          className="w-full justify-start mt-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
          data-testid="logout-btn"
        >
          <LogOut className="h-4 w-4 mr-3" strokeWidth={1.5} />
          Sign Out
        </Button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-sm bg-card border border-border"
        data-testid="mobile-menu-btn"
      >
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/60 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar - Mobile */}
      <aside
        className={`lg:hidden fixed inset-y-0 left-0 z-40 w-[280px] glass-sidebar flex flex-col transform transition-transform duration-300 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <NavContent />
      </aside>

      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex fixed inset-y-0 left-0 w-[280px] glass-sidebar flex-col">
        <NavContent />
      </aside>
    </>
  );
};

export default Sidebar;

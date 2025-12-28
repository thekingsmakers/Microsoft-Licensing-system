import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect, createContext, useContext } from "react";
import axios from "axios";
import { Toaster } from "sonner";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

// Theme/Branding Context
const ThemeContext = createContext(null);
export const useTheme = () => useContext(ThemeContext);

const ThemeProvider = ({ children }) => {
  const [branding, setBranding] = useState({
    company_name: "Renewal Hub",
    company_tagline: "Service Management System",
    logo_url: "",
    primary_color: "#06b6d4",
    theme_mode: "dark",
    accent_color: "#06b6d4"
  });
  const [loading, setLoading] = useState(true);

  const fetchBranding = async () => {
    try {
      const response = await axios.get(`${API}/settings/public`);
      setBranding(response.data);
      applyTheme(response.data);
    } catch (error) {
      console.log("Using default branding");
    } finally {
      setLoading(false);
    }
  };

  const applyTheme = (settings) => {
    const root = document.documentElement;
    const primaryColor = settings.primary_color || "#06b6d4";
    
    // Convert hex to HSL for CSS variables
    const hexToHSL = (hex) => {
      let r = parseInt(hex.slice(1, 3), 16) / 255;
      let g = parseInt(hex.slice(3, 5), 16) / 255;
      let b = parseInt(hex.slice(5, 7), 16) / 255;
      
      let max = Math.max(r, g, b), min = Math.min(r, g, b);
      let h, s, l = (max + min) / 2;
      
      if (max === min) {
        h = s = 0;
      } else {
        let d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
          case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
          case g: h = ((b - r) / d + 2) / 6; break;
          case b: h = ((r - g) / d + 4) / 6; break;
          default: h = 0;
        }
      }
      
      return `${Math.round(h * 360)} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`;
    };
    
    const primaryHSL = hexToHSL(primaryColor);
    root.style.setProperty('--primary', primaryHSL);
    root.style.setProperty('--ring', primaryHSL);
    
    // Apply theme mode
    const themeMode = settings.theme_mode || "dark";
    if (themeMode === "light") {
      root.style.setProperty('--background', '0 0% 100%');
      root.style.setProperty('--foreground', '240 10% 4%');
      root.style.setProperty('--card', '0 0% 98%');
      root.style.setProperty('--card-foreground', '240 10% 4%');
      root.style.setProperty('--popover', '0 0% 100%');
      root.style.setProperty('--popover-foreground', '240 10% 4%');
      root.style.setProperty('--secondary', '240 5% 92%');
      root.style.setProperty('--secondary-foreground', '240 6% 10%');
      root.style.setProperty('--muted', '240 5% 92%');
      root.style.setProperty('--muted-foreground', '240 4% 46%');
      root.style.setProperty('--accent', '240 5% 92%');
      root.style.setProperty('--accent-foreground', '240 6% 10%');
      root.style.setProperty('--border', '240 6% 90%');
      root.style.setProperty('--input', '240 6% 90%');
      root.style.colorScheme = 'light';
      document.body.classList.remove('dark');
      document.body.classList.add('light');
    } else {
      // Dark theme (default)
      root.style.setProperty('--background', '240 6% 4%');
      root.style.setProperty('--foreground', '0 0% 98%');
      root.style.setProperty('--card', '240 5% 7%');
      root.style.setProperty('--card-foreground', '0 0% 98%');
      root.style.setProperty('--popover', '240 6% 4%');
      root.style.setProperty('--popover-foreground', '0 0% 98%');
      root.style.setProperty('--secondary', '240 4% 16%');
      root.style.setProperty('--secondary-foreground', '0 0% 98%');
      root.style.setProperty('--muted', '240 4% 16%');
      root.style.setProperty('--muted-foreground', '240 5% 65%');
      root.style.setProperty('--accent', '240 4% 16%');
      root.style.setProperty('--accent-foreground', '0 0% 98%');
      root.style.setProperty('--border', '240 4% 16%');
      root.style.setProperty('--input', '240 4% 16%');
      root.style.colorScheme = 'dark';
      document.body.classList.remove('light');
      document.body.classList.add('dark');
    }
  };

  useEffect(() => {
    fetchBranding();
  }, []);

  const refreshBranding = () => {
    fetchBranding();
  };

  return (
    <ThemeContext.Provider value={{ branding, loading, refreshBranding, applyTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };
    verifyToken();
  }, [token]);

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    const { token: newToken, user: userData } = response.data;
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
    return userData;
  };

  const register = async (name, email, password) => {
    const response = await axios.post(`${API}/auth/register`, { name, email, password });
    const { token: newToken, user: userData } = response.data;
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-background">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
            </Routes>
            <Toaster 
              position="top-right" 
              theme="dark"
              toastOptions={{
                style: {
                  background: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  color: 'hsl(var(--foreground))',
                },
              }}
            />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;

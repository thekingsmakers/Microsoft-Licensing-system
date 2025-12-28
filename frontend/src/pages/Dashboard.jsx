import { useState, useEffect, useCallback } from "react";
import { Routes, Route } from "react-router-dom";
import axios from "axios";
import { useAuth, API } from "../App";
import Sidebar from "../components/Sidebar";
import ServiceTable from "../components/ServiceTable";
import ServiceModal from "../components/ServiceModal";
import StatsCards from "../components/StatsCards";
import EmailLogs from "../components/EmailLogs";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { toast } from "sonner";
import { Plus, Search, RefreshCw, Bell } from "lucide-react";

const Dashboard = () => {
  const { token } = useAuth();
  const [services, setServices] = useState([]);
  const [stats, setStats] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    try {
      const [servicesRes, statsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/services`, { headers }),
        axios.get(`${API}/dashboard/stats`, { headers }),
        axios.get(`${API}/categories`)
      ]);
      setServices(servicesRes.data);
      setStats(statsRes.data);
      setCategories(categoriesRes.data.categories);
    } catch (error) {
      toast.error("Failed to fetch data");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateService = async (data) => {
    try {
      await axios.post(`${API}/services`, data, { headers });
      toast.success("Service created successfully");
      setModalOpen(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create service");
    }
  };

  const handleUpdateService = async (data) => {
    try {
      await axios.put(`${API}/services/${editingService.id}`, data, { headers });
      toast.success("Service updated successfully");
      setModalOpen(false);
      setEditingService(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update service");
    }
  };

  const handleDeleteService = async (id) => {
    try {
      await axios.delete(`${API}/services/${id}`, { headers });
      toast.success("Service deleted successfully");
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete service");
    }
  };

  const handleSendReminder = async (service) => {
    try {
      await axios.post(`${API}/services/${service.id}/send-reminder`, {}, { headers });
      toast.success(`Reminder sent to ${service.contact_email}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to send reminder");
    }
  };

  const handleTriggerExpiryCheck = async () => {
    try {
      await axios.post(`${API}/check-expiring`, {}, { headers });
      toast.success("Expiry check triggered");
    } catch (error) {
      toast.error("Failed to trigger expiry check");
    }
  };

  const openEditModal = (service) => {
    setEditingService(service);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingService(null);
  };

  const getServiceStatus = (expiryDate) => {
    const now = new Date();
    const expiry = new Date(expiryDate);
    const daysUntil = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
    
    if (daysUntil < 0) return "expired";
    if (daysUntil <= 7) return "danger";
    if (daysUntil <= 30) return "warning";
    return "safe";
  };

  const filteredServices = services.filter(service => {
    const matchesSearch = service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         service.provider.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || service.category === categoryFilter;
    const status = getServiceStatus(service.expiry_date);
    const matchesStatus = statusFilter === "all" || 
                         (statusFilter === "expiring" && (status === "danger" || status === "warning")) ||
                         (statusFilter === "expired" && status === "expired") ||
                         (statusFilter === "safe" && status === "safe");
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const ServicesPage = () => (
    <div className="animate-enter">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Services</h1>
          <p className="text-muted-foreground mt-1">
            Manage your organization's service subscriptions and renewals
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleTriggerExpiryCheck}
            data-testid="trigger-expiry-check-btn"
            className="btn-secondary"
          >
            <Bell className="h-4 w-4 mr-2" />
            Check Expiring
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={fetchData}
            data-testid="refresh-btn"
            className="btn-secondary"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button 
            onClick={() => setModalOpen(true)}
            data-testid="add-service-btn"
            className="btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Service
          </Button>
        </div>
      </div>

      <StatsCards stats={stats} loading={loading} />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6 mt-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search services..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-card border-border"
            data-testid="search-input"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-full sm:w-[180px] bg-card border-border" data-testid="category-filter">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map(cat => (
              <SelectItem key={cat} value={cat}>{cat}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-[180px] bg-card border-border" data-testid="status-filter">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="safe">Safe</SelectItem>
            <SelectItem value="expiring">Expiring Soon</SelectItem>
            <SelectItem value="expired">Expired</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <ServiceTable
        services={filteredServices}
        loading={loading}
        onEdit={openEditModal}
        onDelete={handleDeleteService}
        onSendReminder={handleSendReminder}
        getServiceStatus={getServiceStatus}
      />
    </div>
  );

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 lg:ml-[280px] p-6 md:p-8 lg:p-12">
        <div className="max-w-[1600px] mx-auto">
          <Routes>
            <Route path="/" element={<ServicesPage />} />
            <Route path="/notifications" element={<EmailLogs />} />
          </Routes>
        </div>
      </main>

      <ServiceModal
        open={modalOpen}
        onClose={closeModal}
        onSubmit={editingService ? handleUpdateService : handleCreateService}
        service={editingService}
        categories={categories}
      />
    </div>
  );
};

export default Dashboard;

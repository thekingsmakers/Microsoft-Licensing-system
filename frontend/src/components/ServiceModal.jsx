import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Calendar } from "./ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { CalendarIcon, Loader2 } from "lucide-react";
import { format, parseISO } from "date-fns";
import { cn } from "../lib/utils";

const ServiceModal = ({ open, onClose, onSubmit, service, categories }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    provider: "",
    category: "",
    expiry_date: "",
    contact_email: "",
    notes: "",
    cost: ""
  });
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    if (service) {
      setFormData({
        name: service.name || "",
        provider: service.provider || "",
        category: service.category || "",
        expiry_date: service.expiry_date || "",
        contact_email: service.contact_email || "",
        notes: service.notes || "",
        cost: service.cost?.toString() || ""
      });
      if (service.expiry_date) {
        setSelectedDate(parseISO(service.expiry_date));
      }
    } else {
      setFormData({
        name: "",
        provider: "",
        category: "",
        expiry_date: "",
        contact_email: "",
        notes: "",
        cost: ""
      });
      setSelectedDate(null);
    }
  }, [service, open]);

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    if (date) {
      setFormData({ ...formData, expiry_date: date.toISOString() });
    }
    setCalendarOpen(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit({
        ...formData,
        cost: parseFloat(formData.cost) || 0
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{service ? "Edit Service" : "Add New Service"}</DialogTitle>
          <DialogDescription>
            {service 
              ? "Update the service details below." 
              : "Fill in the details to add a new service for tracking."}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="label-uppercase">Service Name</Label>
              <Input
                id="name"
                placeholder="e.g., Adobe Creative Cloud"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                data-testid="service-name-input"
                className="bg-background"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="provider" className="label-uppercase">Provider</Label>
              <Input
                id="provider"
                placeholder="e.g., Adobe Inc."
                value={formData.provider}
                onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                required
                data-testid="service-provider-input"
                className="bg-background"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="label-uppercase">Category</Label>
              <Select 
                value={formData.category} 
                onValueChange={(value) => setFormData({ ...formData, category: value })}
                required
              >
                <SelectTrigger data-testid="service-category-select" className="bg-background">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(cat => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="label-uppercase">Expiry Date</Label>
              <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal bg-background",
                      !selectedDate && "text-muted-foreground"
                    )}
                    data-testid="service-expiry-date-btn"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {selectedDate ? format(selectedDate, "MMM d, yyyy") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={selectedDate}
                    onSelect={handleDateSelect}
                    initialFocus
                    data-testid="service-calendar"
                  />
                </PopoverContent>
              </Popover>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact_email" className="label-uppercase">Contact Email</Label>
              <Input
                id="contact_email"
                type="email"
                placeholder="admin@company.com"
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                required
                data-testid="service-email-input"
                className="bg-background"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="cost" className="label-uppercase">Annual Cost ($)</Label>
              <Input
                id="cost"
                type="number"
                placeholder="0.00"
                value={formData.cost}
                onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
                data-testid="service-cost-input"
                className="bg-background"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes" className="label-uppercase">Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Add any additional notes about this service..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              data-testid="service-notes-input"
              className="bg-background resize-none"
            />
          </div>

          <DialogFooter className="gap-2 sm:gap-0 mt-6">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose}
              data-testid="cancel-service-btn"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading || !formData.name || !formData.category || !formData.expiry_date}
              className="btn-primary"
              data-testid="submit-service-btn"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                service ? "Update Service" : "Add Service"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ServiceModal;

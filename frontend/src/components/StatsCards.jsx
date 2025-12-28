import { Card, CardContent } from "./ui/card";
import { Skeleton } from "./ui/skeleton";
import { Package, AlertTriangle, XCircle, CheckCircle, DollarSign } from "lucide-react";

const StatsCards = ({ stats, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="bg-card border-border">
            <CardContent className="p-6">
              <Skeleton className="h-4 w-20 mb-2" />
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: "Total Services",
      value: stats?.total || 0,
      icon: Package,
      color: "text-primary",
      bgColor: "bg-primary/10",
      borderColor: "border-primary/20"
    },
    {
      label: "Expiring Soon",
      value: stats?.expiring_soon || 0,
      icon: AlertTriangle,
      color: "text-amber-500",
      bgColor: "bg-amber-500/10",
      borderColor: "border-amber-500/20"
    },
    {
      label: "Expired",
      value: stats?.expired || 0,
      icon: XCircle,
      color: "text-red-500",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/20"
    },
    {
      label: "Safe",
      value: stats?.safe || 0,
      icon: CheckCircle,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/20"
    },
    {
      label: "Total Cost",
      value: `$${(stats?.total_cost || 0).toLocaleString()}`,
      icon: DollarSign,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/20"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4" data-testid="stats-cards">
      {cards.map(({ label, value, icon: Icon, color, bgColor, borderColor }) => (
        <Card 
          key={label} 
          className={`bg-card border-border card-hover`}
          data-testid={`stat-${label.toLowerCase().replace(/\s+/g, '-')}`}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="label-uppercase mb-1">{label}</p>
                <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
              </div>
              <div className={`p-3 rounded-sm ${bgColor} border ${borderColor}`}>
                <Icon className={`h-5 w-5 ${color}`} strokeWidth={1.5} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default StatsCards;

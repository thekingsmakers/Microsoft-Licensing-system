import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Skeleton } from "./ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import { Mail, Clock, CheckCircle } from "lucide-react";
import { format, parseISO } from "date-fns";
import { toast } from "sonner";

const EmailLogs = () => {
  const { token } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get(`${API}/email-logs`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setLogs(response.data);
      } catch (error) {
        toast.error("Failed to fetch email logs");
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [token]);

  const getUrgencyBadge = (days) => {
    if (days <= 1) {
      return <Badge className="bg-red-500/10 text-red-500 border-red-500/20">Critical</Badge>;
    }
    if (days <= 7) {
      return <Badge className="bg-amber-500/10 text-amber-500 border-amber-500/20">Warning</Badge>;
    }
    return <Badge className="bg-blue-500/10 text-blue-500 border-blue-500/20">Reminder</Badge>;
  };

  if (loading) {
    return (
      <div className="animate-enter">
        <div className="mb-8">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="animate-enter" data-testid="email-logs-page">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Notification History</h1>
        <p className="text-muted-foreground mt-1">
          View all automated email reminders sent for expiring services
        </p>
      </div>

      <Card className="bg-card border-border">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <Mail className="h-5 w-5 text-primary" />
            Email Logs
            <span className="text-sm font-normal text-muted-foreground ml-1">
              ({logs.length})
            </span>
          </CardTitle>
          <CardDescription>
            Recent notification emails sent to service contacts
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {logs.length === 0 ? (
            <div className="p-12 text-center">
              <div className="p-4 rounded-full bg-muted/50 w-fit mx-auto mb-4">
                <Mail className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No notifications sent yet</h3>
              <p className="text-muted-foreground text-sm">
                Email reminders will appear here when services are approaching expiry
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="table-header">Service</TableHead>
                    <TableHead className="table-header">Recipient</TableHead>
                    <TableHead className="table-header">Days Until Expiry</TableHead>
                    <TableHead className="table-header">Urgency</TableHead>
                    <TableHead className="table-header">Sent At</TableHead>
                    <TableHead className="table-header">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow 
                      key={log.id} 
                      className="border-border hover:bg-white/5 transition-colors"
                      data-testid={`email-log-${log.id}`}
                    >
                      <TableCell className="font-medium">
                        {log.service_name}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {log.recipient_email}
                      </TableCell>
                      <TableCell className="font-mono">
                        {log.days_until_expiry} days
                      </TableCell>
                      <TableCell>
                        {getUrgencyBadge(log.days_until_expiry)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-muted-foreground">
                          <Clock className="h-3.5 w-3.5" />
                          <span className="font-mono text-sm">
                            {format(parseISO(log.sent_at), "MMM d, yyyy HH:mm")}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-emerald-500">
                          <CheckCircle className="h-4 w-4" />
                          <span className="text-sm">Sent</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default EmailLogs;

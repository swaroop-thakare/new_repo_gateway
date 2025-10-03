"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { RefreshCw, XCircle, Eye } from "lucide-react"
import { PageHeader } from "@/components/demo/page-header"
import { KpiCard } from "@/components/demo/kpi-card"
import { Download } from "lucide-react"
import { AdvisoryBanner } from "@/components/demo/advisory-banner"

const pendingPayments = [
  {
    id: "TRC-2024-001240",
    amount: "₹18,000",
    railCandidate: "IMPS",
    nextAction: "ACC Check",
    age: "12s",
    sla: "On track",
  },
  {
    id: "TRC-2024-001241",
    amount: "₹35,000",
    railCandidate: "NEFT",
    nextAction: "PDR Selection",
    age: "45s",
    sla: "On track",
  },
]

const releaseQueue = [
  {
    id: "TRC-2024-001234",
    amount: "₹25,000",
    selectedRail: "IMPS",
    rescoreAt: "10:25:00",
    shiftPossible: "Yes",
    age: "2m 15s",
  },
  {
    id: "TRC-2024-001235",
    amount: "₹50,000",
    selectedRail: "RTGS",
    rescoreAt: "10:26:30",
    shiftPossible: "No",
    age: "1m 30s",
  },
]

const dispatched = [
  {
    id: "TRC-2024-001230",
    amount: "₹20,000",
    rail: "IMPS",
    utr: "UTR2024001230456",
    status: "Success",
    time: "10:20:15",
  },
  {
    id: "TRC-2024-001231",
    amount: "₹15,000",
    rail: "NEFT",
    utr: "—",
    status: "Failed",
    time: "10:18:42",
  },
]

export default function LiveQueuePage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Operations"
        title="Live Queue"
        description="Real-time routing & dispatch visibility"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-3 w-3 mr-2" />
              Export CSV
            </Button>
          </div>
        }
      />
      <AdvisoryBanner className="mt-2" />
      <div className="grid gap-4 md:grid-cols-3">
        <KpiCard label="In Queue" value="2,847" delta="+18.2% vs 24h" trend="up" />
        <KpiCard label="Release Queue" value="312" delta="Re-score in next 2m" trend="flat" />
        <KpiCard label="Success Rate" value="98.7%" delta="Stable" trend="flat" />
      </div>

      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="bg-background/60 supports-[backdrop-filter]:bg-background/40 backdrop-blur border rounded-lg bg-gradient-to-r from-sky-500/20 via-blue-500/15 to-cyan-500/20">
          <TabsTrigger value="pending" className="tab-pill">
            Pending
          </TabsTrigger>
          <TabsTrigger value="release" className="tab-pill">
            Release Queue
          </TabsTrigger>
          <TabsTrigger value="dispatched" className="tab-pill">
            Dispatched
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Pending (Awaiting ACC/PDR)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Trace ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Rail Candidate</TableHead>
                    <TableHead>Next Action</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>SLA</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingPayments.map((payment) => (
                    <TableRow key={payment.id} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-mono text-sm">{payment.id}</TableCell>
                      <TableCell className="font-medium">{payment.amount}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {payment.railCandidate}
                        </Badge>
                      </TableCell>
                      <TableCell>{payment.nextAction}</TableCell>
                      <TableCell>{payment.age}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-success/15 text-success-foreground">
                          {payment.sla}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button size="sm" variant="ghost">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="release" className="space-y-4">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Release Queue (Pre-commit Re-score)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Trace ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Selected Rail</TableHead>
                    <TableHead>Re-score At</TableHead>
                    <TableHead>Shift Possible?</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {releaseQueue.map((payment) => (
                    <TableRow key={payment.id} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-mono text-sm">{payment.id}</TableCell>
                      <TableCell className="font-medium">{payment.amount}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {payment.selectedRail}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{payment.rescoreAt}</TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            payment.shiftPossible === "Yes"
                              ? "bg-success/15 text-success-foreground"
                              : "bg-muted text-muted-foreground"
                          }
                        >
                          {payment.shiftPossible}
                        </Badge>
                      </TableCell>
                      <TableCell>{payment.age}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            <RefreshCw className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <XCircle className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dispatched" className="space-y-4">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle>Dispatched (with UTR or Fail Code)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Trace ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Rail</TableHead>
                    <TableHead>UTR</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Time</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dispatched.map((payment) => (
                    <TableRow key={payment.id} className="hover:bg-muted/40 transition-colors">
                      <TableCell className="font-mono text-sm">{payment.id}</TableCell>
                      <TableCell className="font-medium">{payment.amount}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary text-secondary-foreground">
                          {payment.rail}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{payment.utr}</TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            payment.status === "Success"
                              ? "bg-success/15 text-success-foreground"
                              : "bg-destructive/15 text-destructive-foreground"
                          }
                        >
                          {payment.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">{payment.time}</TableCell>
                      <TableCell>
                        <Button size="sm" variant="ghost">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

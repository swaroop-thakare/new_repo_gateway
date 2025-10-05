"use client"

import Link from "next/link"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { GlassTimeline, type GlassStep } from "@/components/demo/glass-timeline"
import { MoreHorizontal, ArrowLeft } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export default function PayrollDetailPage() {
  const params = useParams()
  const id = params?.id as string

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/book-demo/payroll" className="inline-flex items-center text-sm text-blue-700 hover:underline">
            <ArrowLeft className="mr-1 h-4 w-4" /> Back to Payroll
          </Link>
          <h2 className="text-2xl font-semibold">Payroll details</h2>
          <span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">Batch {id}</span>
        </div>
        <div className="flex items-center gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">Request changes</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Request changes</DialogTitle>
              </DialogHeader>
              <div className="space-y-3">
                <textarea
                  className="w-full rounded-md border p-2 text-sm"
                  rows={5}
                  placeholder="Describe what needs to be updated..."
                  aria-label="Request changes details"
                />
                <Button className="bg-blue-600 text-white hover:bg-blue-700">Submit request</Button>
              </div>
            </DialogContent>
          </Dialog>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">Approve & Queue Execution</Button>
        </div>
      </header>

      <Card>
        <CardContent className="space-y-4 p-0">
          <div className="p-0">
            <GlassTimeline
              title="Payroll Run"
              subtitle="Biweekly"
              person={{
                name: "Julia Thompson",
                amount: "$6,200.00",
                currency: "USD",
                status: "Paid Out",
                avatarUrl: "/diverse-person-avatar.png",
              }}
              badges={["Needs Approval", "Payroll"]}
              steps={
                [
                  { label: "Data Ingested", status: "done", date: "Sep 1" },
                  { label: "Compliance Check", status: "done", date: "Sep 3" },
                  { label: "Awaiting Approval", status: "current", date: "Sep 12" },
                  { label: "Processing", status: "pending", date: "—" },
                  { label: "Completed", status: "pending", date: "—" },
                ] as GlassStep[]
              }
              className="mx-6 my-6"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <div>
            <CardTitle>Risk & Compliance</CardTitle>
            <CardDescription>Automated controls before routing and execution</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="text-sm">
              <div className="font-medium">Sanctions & PEP</div>
              <div className="text-muted-foreground">OFAC, UN, EU list checks</div>
            </div>
            <Badge>Pass</Badge>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="text-sm">
              <div className="font-medium">Amount variance</div>
              <div className="text-muted-foreground">Delta vs last cycle</div>
            </div>
            <Badge variant="secondary">Review</Badge>
          </div>
          <div className="flex items-center justify-between rounded-lg border p-3">
            <div className="text-sm">
              <div className="font-medium">Bank details</div>
              <div className="text-muted-foreground">IBAN/IFSC format & status</div>
            </div>
            <Badge>Pass</Badge>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Batch Breakdown</CardTitle>
            <CardDescription>Total Amount and sub-totals</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Total Amount</span>
              <span className="font-semibold">$243,500</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Base Payouts</span>
              <span className="font-semibold">$236,800</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Fees</span>
              <span className="font-semibold">$4,200</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Taxes</span>
              <span className="font-semibold">$2,500</span>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Documents</CardTitle>
            <CardDescription>Uploaded inputs and generated outputs</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="source">
                <AccordionTrigger>Source Files</AccordionTrigger>
                <AccordionContent>
                  <ul className="list-disc pl-5 text-sm text-slate-700">
                    <li>Payroll_India_Sep26.csv</li>
                  </ul>
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="outputs">
                <AccordionTrigger>Outputs</AccordionTrigger>
                <AccordionContent>
                  <ul className="list-disc pl-5 text-sm text-slate-700">
                    <li>Audit_Pack_B-{id}.pdf</li>
                  </ul>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transactions</CardTitle>
          <CardDescription>All items in this batch</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {[
                  { id: "E-1201", name: "Julia Thompson", amount: "$6,200", status: "Ready" },
                  { id: "E-1202", name: "Arjun Mehta", amount: "$5,950", status: "Ready" },
                  { id: "E-1203", name: "Li Wei", amount: "$6,400", status: "Flagged" },
                ].map((t) => (
                  <TableRow key={t.id}>
                    <TableCell>{t.id}</TableCell>
                    <TableCell>{t.name}</TableCell>
                    <TableCell>{t.amount}</TableCell>
                    <TableCell>{t.status}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger className="inline-flex items-center rounded border px-2 py-1 text-sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem>View Transaction Lineage</DropdownMenuItem>
                          <DropdownMenuItem>Open Comments</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

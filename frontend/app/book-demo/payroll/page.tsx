"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { GlassRunCard } from "@/components/demo/glass-run-card"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

const inProgress = [
  {
    id: "1001",
    date: "Sep 26",
    name: "Sep 26, India Main",
    entity: "ACME India Ltd",
    amount: "$243,500",
    status: "In Progress",
  },
  {
    id: "1002",
    date: "Sep 27",
    name: "Sep 27, UK Contractors",
    entity: "ACME UK Ltd",
    amount: "£82,900",
    status: "In Progress",
  },
]

const completed = [
  {
    id: "0999",
    date: "Sep 24",
    name: "Sep 24, US HQ",
    entity: "ACME International",
    amount: "$199,040",
    status: "Completed",
  },
]

export default function PayrollPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Payroll</h2>
        <div className="hidden gap-2 md:flex">
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">Run payroll</Button>
          <Button variant="outline">Import CSV</Button>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardDescription>This month volume</CardDescription>
            <CardTitle className="text-2xl">$1,287,440</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">+8.2% vs last month</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>In-progress runs</CardDescription>
            <CardTitle className="text-2xl">2</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">India, UK contractors</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Exceptions</CardDescription>
            <CardTitle className="text-2xl">3</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">1 flagged KYC, 2 amount variances</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Avg. processing time</CardDescription>
            <CardTitle className="text-2xl">2h 14m</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">-18m vs 30-day avg</CardContent>
        </Card>
      </div>

      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <select
            aria-label="Filter entity"
            className="rounded-md border bg-background px-3 py-2 text-sm"
            defaultValue=""
          >
            <option value="" disabled>
              Entity
            </option>
            <option>ACME India Ltd</option>
            <option>ACME UK Ltd</option>
            <option>ACME International</option>
          </select>
          <select
            aria-label="Filter status"
            className="rounded-md border bg-background px-3 py-2 text-sm"
            defaultValue=""
          >
            <option value="" disabled>
              Status
            </option>
            <option>In Progress</option>
            <option>Completed</option>
            <option>Flagged</option>
          </select>
          <input
            aria-label="Search batches"
            placeholder="Search by batch, entity, or amount"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm md:w-64"
          />
        </div>
        <div className="flex gap-2 md:hidden">
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">Run payroll</Button>
          <Button variant="outline">Import CSV</Button>
        </div>
      </div>

      <Tabs defaultValue="in-progress" className="space-y-4">
        <TabsList>
          <TabsTrigger value="in-progress">In Progress</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>
        <TabsContent value="in-progress" className="space-y-3">
          {inProgress.map((b) => {
            const region = b.name.split(", ")[1] || b.name
            return (
              <GlassRunCard
                key={b.id}
                href={`/book-demo/payroll/${b.id}`}
                dateLabel={b.date}
                region={region}
                company={b.entity}
                totalAmount={b.amount}
                status={b.status}
                steps={[
                  { key: "Data Ingested", status: "done" },
                  { key: "Compliance Check", status: "done" },
                  { key: "Awaiting Approval", status: "current" },
                  { key: "Processing", status: "upcoming" },
                  { key: "Completed", status: "upcoming" },
                ]}
              />
            )
          })}
        </TabsContent>
        <TabsContent value="completed" className="space-y-3">
          {completed.map((b) => {
            const region = b.name.split(", ")[1] || b.name
            return (
              <GlassRunCard
                key={b.id}
                href={`/book-demo/payroll/${b.id}`}
                dateLabel={b.date}
                region={region}
                company={b.entity}
                totalAmount={b.amount}
                status={b.status}
                steps={[
                  { key: "Data Ingested", status: "done" },
                  { key: "Compliance Check", status: "done" },
                  { key: "Awaiting Approval", status: "done" },
                  { key: "Processing", status: "done" },
                  { key: "Completed", status: "done" },
                ]}
              />
            )
          })}
        </TabsContent>
      </Tabs>
    </div>
  )
}

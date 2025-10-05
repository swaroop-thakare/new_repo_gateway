"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { GlassRunCard } from "@/components/demo/glass-run-card"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useEffect, useState } from "react"
import { fetchPayrollData, formatCurrency, PayrollData } from "@/lib/api"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts"

export default function PayrollPage() {
  const [payrollData, setPayrollData] = useState<PayrollData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch payroll data on component mount
  useEffect(() => {
    const loadPayrollData = async () => {
      try {
        setLoading(true)
        const data = await fetchPayrollData()
        if (data) {
          setPayrollData(data)
        } else {
          setError("Failed to load payroll data")
        }
      } catch (err) {
        setError("Error loading payroll data")
        console.error("Error loading payroll data:", err)
      } finally {
        setLoading(false)
      }
    }

    loadPayrollData()
  }, [])

  // Separate payroll entries by status
  const inProgressEntries = payrollData?.payroll_entries.filter(entry => 
    entry.status === "In Progress" || entry.status === "Exceptions"
  ) || []
  
  const completedEntries = payrollData?.payroll_entries.filter(entry => 
    entry.status === "Completed"
  ) || []

  // Clear Data functionality
  const handleClearPayrollData = async () => {
    const confirmed = window.confirm(
      "⚠️ WARNING: This will permanently delete ALL payroll data from the database.\n\n" +
      "This action cannot be undone. Are you sure you want to continue?"
    )
    
    if (!confirmed) return
    
    try {
      console.log(`🗑️ Clearing all payroll data...`)
      
      // Call the clear payroll data API
      const response = await fetch('http://localhost:8000/acc/clear-payroll-data', {
        method: 'DELETE',
        headers: {
          'X-API-Key': 'arealis_api_key_2024',
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        alert("✅ All payroll data has been cleared successfully!")
        // Refresh the data
        window.location.reload()
      } else {
        alert("❌ Failed to clear data. Please try again.")
      }
    } catch (error) {
      console.error("Error clearing data:", error)
      alert("❌ Error clearing data. Please try again.")
    }
  }

  // Prepare chart data
  const chartData = payrollData?.payroll_entries.map(entry => ({
    name: entry.entity,
    amount: entry.total_amount,
    employees: entry.employees,
    status: entry.status
  })) || []

  const pieData = payrollData?.payroll_entries.map(entry => ({
    name: entry.entity,
    value: entry.total_amount
  })) || []

  const COLORS = ['#22c55e', '#38bdf8', '#f59e0b', '#f43f5e', '#8b5cf6']

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Payroll</h2>
        <div className="hidden gap-2 md:flex">
          <Button 
            variant="destructive"
            onClick={handleClearPayrollData}
          >
            Clear Data
          </Button>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">Run payroll</Button>
          <Button variant="outline">Import CSV</Button>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardDescription>This month volume</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "Loading..." : payrollData ? formatCurrency(payrollData.kpis.this_month_volume) : "₹0"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {payrollData ? "+8.2% vs last month" : "No data available"}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>In-progress runs</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "Loading..." : payrollData ? payrollData.kpis.in_progress_runs : "0"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {payrollData ? `${inProgressEntries.length} active runs` : "No active runs"}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Exceptions</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "Loading..." : payrollData ? payrollData.kpis.exceptions : "0"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {payrollData ? `${payrollData.kpis.exceptions} flagged transactions` : "No exceptions"}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Avg. processing time</CardDescription>
            <CardTitle className="text-2xl">
              {loading ? "Loading..." : payrollData ? payrollData.kpis.avg_processing_time : "0h 0m"}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {payrollData ? "-18m vs 30-day avg" : "No data available"}
          </CardContent>
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
            {payrollData?.payroll_entries.map((entry, index) => (
              <option key={index} value={entry.entity}>
                {entry.sub_entity}
              </option>
            ))}
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
            <option>Exceptions</option>
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
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading payroll data...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-500">Error loading payroll data: {error}</div>
          ) : inProgressEntries.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No in-progress payroll runs</div>
          ) : (
            inProgressEntries.map((entry) => {
              const progressSteps = entry.status === "In Progress" ? [
                { key: "Data Ingested", status: "done" as const },
                { key: "Compliance Check", status: "done" as const },
                { key: "Awaiting Approval", status: "current" as const },
                { key: "Processing", status: "upcoming" as const },
                { key: "Completed", status: "upcoming" as const },
              ] : [
                { key: "Data Ingested", status: "done" as const },
                { key: "Compliance Check", status: "done" as const },
                { key: "Awaiting Approval", status: "done" as const },
                { key: "Processing", status: "current" as const },
                { key: "Completed", status: "upcoming" as const },
              ]
              
              return (
                <GlassRunCard
                  key={entry.id}
                  href={`/book-demo/payroll/${entry.id}`}
                  dateLabel={entry.date}
                  region={entry.entity}
                  company={entry.sub_entity}
                  totalAmount={formatCurrency(entry.total_amount)}
                  status={entry.status}
                  steps={progressSteps}
                />
              )
            })
          )}
        </TabsContent>
        <TabsContent value="completed" className="space-y-3">
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading payroll data...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-500">Error loading payroll data: {error}</div>
          ) : completedEntries.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No completed payroll runs</div>
          ) : (
            completedEntries.map((entry) => {
              return (
                <GlassRunCard
                  key={entry.id}
                  href={`/book-demo/payroll/${entry.id}`}
                  dateLabel={entry.date}
                  region={entry.entity}
                  company={entry.sub_entity}
                  totalAmount={formatCurrency(entry.total_amount)}
                  status={entry.status}
                  steps={[
                    { key: "Data Ingested", status: "done" as const },
                    { key: "Compliance Check", status: "done" as const },
                    { key: "Awaiting Approval", status: "done" as const },
                    { key: "Processing", status: "done" as const },
                    { key: "Completed", status: "done" as const },
                  ]}
                />
              )
            })
          )}
        </TabsContent>
      </Tabs>

      {/* Modern Visualizations Section */}
      {payrollData && payrollData.payroll_entries.length > 0 && (
        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Payroll Amount by Company */}
            <Card className="glass-card border">
              <CardHeader>
                <CardTitle className="text-lg text-white">Payroll Amount by Company</CardTitle>
                <CardDescription className="text-gray-400">Total payroll amounts by company</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis 
                      dataKey="name" 
                      stroke="rgba(255,255,255,0.6)"
                      fontSize={12}
                    />
                    <YAxis 
                      stroke="rgba(255,255,255,0.6)"
                      fontSize={12}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "#0f0f0f",
                        border: "1px solid rgba(255,255,255,0.12)",
                        color: "white",
                        borderRadius: "8px",
                      }}
                      formatter={(value: any) => [`₹${value.toLocaleString()}`, 'Amount']}
                    />
                    <Bar dataKey="amount" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Company Distribution */}
            <Card className="glass-card border">
              <CardHeader>
                <CardTitle className="text-lg text-white">Company Distribution</CardTitle>
                <CardDescription className="text-gray-400">Payroll distribution by company</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "#0f0f0f",
                        border: "1px solid rgba(255,255,255,0.12)",
                        color: "white",
                        borderRadius: "8px",
                      }}
                      formatter={(value: any) => [`₹${value.toLocaleString()}`, 'Amount']}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Employee Count by Company */}
          <Card className="glass-card border">
            <CardHeader>
              <CardTitle className="text-lg text-white">Employee Count by Company</CardTitle>
              <CardDescription className="text-gray-400">Number of employees processed per company</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="name" 
                    stroke="rgba(255,255,255,0.6)"
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.6)"
                    fontSize={12}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#0f0f0f",
                      border: "1px solid rgba(255,255,255,0.12)",
                      color: "white",
                      borderRadius: "8px",
                    }}
                    formatter={(value: any) => [`${value}`, 'Employees']}
                  />
                  <Bar dataKey="employees" fill="#22c55e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Payroll Status Overview */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="glass-card border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-300">Total Companies</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">
                  {payrollData.payroll_entries.length}
                </div>
                <p className="text-xs text-gray-400">Active payroll runs</p>
              </CardContent>
            </Card>
            
            <Card className="glass-card border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-300">Total Employees</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">
                  {payrollData.payroll_entries.reduce((sum, entry) => sum + entry.employees, 0)}
                </div>
                <p className="text-xs text-gray-400">Employees processed</p>
              </CardContent>
            </Card>
            
            <Card className="glass-card border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-300">Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">
                  {payrollData.payroll_entries.length > 0 
                    ? Math.round((payrollData.payroll_entries.filter(e => e.status === "Completed").length / payrollData.payroll_entries.length) * 100)
                    : 0}%
                </div>
                <p className="text-xs text-gray-400">Completed runs</p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}

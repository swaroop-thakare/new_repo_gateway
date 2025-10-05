"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, TrendingDown, MoreHorizontal, Clock, AlertCircle, CheckCircle2, XCircle } from "lucide-react"
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts"
import VendorPaymentsCard from "@/components/dashboard/vendor-payments-card"
import LoanDisbursementsCard from "@/components/dashboard/loan-disbursements-card"
import FunnelStage from "@/components/dashboard/funnel-stage"
import EventItem from "@/components/dashboard/event-item"
import TaskItem from "@/components/dashboard/task-item"

export default function OverviewPage() {
  const railMixData = [
    { name: "UPI", value: 45, color: "#3b82f6" },
    { name: "IMPS", value: 25, color: "#60a5fa" },
    { name: "NEFT", value: 15, color: "#93c5fd" },
    { name: "RTGS", value: 10, color: "#bfdbfe" },
    { name: "NACH", value: 5, color: "#dbeafe" },
  ]

  const slaBreachData = [
    { time: "00:00", expiry: 2, rail: 1 },
    { time: "04:00", expiry: 1, rail: 2 },
    { time: "08:00", expiry: 3, rail: 1 },
    { time: "12:00", expiry: 2, rail: 3 },
    { time: "16:00", expiry: 4, rail: 2 },
    { time: "20:00", expiry: 1, rail: 1 },
  ]

  const overdueTasksData = [
    { category: "Approvals", count: 12 },
    { category: "Recon", count: 8 },
    { category: "Filings", count: 5 },
    { category: "Investigations", count: 3 },
  ]

  return (
    <div className="space-y-6">
      {/* Header with Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M2 6L8 2L14 6V13C14 13.5304 13.7893 14.0391 13.4142 14.4142C13.0391 14.7893 12.5304 15 12 15H4C3.46957 15 2.96086 14.7893 2.58579 14.4142C2.21071 14.0391 2 13.5304 2 13V6Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span>›</span>
        <span className="text-white">Dashboard</span>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Today's Volume */}
        <Card className="glass-card glass-primary border">
          <CardHeader className="relative flex flex-row items-start justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-300">Today's Volume</CardTitle>
            <button className="text-gray-400 hover:text-white">
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </CardHeader>
          <CardContent className="relative space-y-3">
            <div className="space-y-1">
              <div className="text-3xl font-bold text-white">
                ₹8.4<span className="text-2xl text-gray-400">Cr</span>
              </div>
              <div className="text-xs text-gray-400">2,847 transactions</div>
              <div className="flex items-center gap-1 text-xs text-blue-400">
                <TrendingUp className="h-3 w-3" />
                <span>+18.2%</span>
              </div>
            </div>
            {/* Hourly volume sparkline */}
            <svg className="h-12 w-full opacity-50" viewBox="0 0 200 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="48">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d="M0 40 L20 38 L40 35 L60 30 L80 28 L100 25 L120 20 L140 18 L160 15 L180 12 L200 10 L200 48 L0 48 Z"
                fill="url(#volumeGradient)"
              />
              <path
                d="M0 40 L20 38 L40 35 L60 30 L80 28 L100 25 L120 20 L140 18 L160 15 L180 12 L200 10"
                stroke="#3b82f6"
                strokeWidth="2"
                fill="none"
              />
            </svg>
          </CardContent>
        </Card>

        {/* Success Rate */}
        <Card className="glass-card glass-success border">
          <CardHeader className="relative flex flex-row items-start justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-300">Success Rate</CardTitle>
            <button className="text-gray-400 hover:text-white">
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </CardHeader>
          <CardContent className="relative space-y-3">
            <div className="space-y-1">
              <div className="text-3xl font-bold text-white">
                98.7<span className="text-2xl text-gray-400">%</span>
              </div>
              <div className="text-xs text-gray-400">2,810 success / 37 failed</div>
              <div className="flex items-center gap-1 text-xs text-blue-400">
                <TrendingUp className="h-3 w-3" />
                <span>+0.3%</span>
              </div>
            </div>
            {/* Success vs Fail bar sparkline */}
            <div className="flex h-12 items-end gap-1">
              {[95, 97, 96, 98, 99, 97, 98, 99, 98, 99, 98, 99].map((rate, i) => (
                <div key={i} className="flex flex-1 flex-col gap-0.5">
                  <div className="w-full rounded-t bg-blue-500/50" style={{ height: `${rate}%` }} />
                  <div className="w-full rounded-b bg-red-500/50" style={{ height: `${100 - rate}%` }} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Avg Time to Settle */}
        <Card className="glass-card glass-primary border">
          <CardHeader className="relative flex flex-row items-start justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-300">Avg Time to Settle</CardTitle>
            <button className="text-gray-400 hover:text-white">
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </CardHeader>
          <CardContent className="relative space-y-3">
            <div className="space-y-1">
              <div className="text-3xl font-bold text-white">
                2.4<span className="text-2xl text-gray-400">min</span>
              </div>
              <div className="text-xs text-gray-400">144 seconds average</div>
              <div className="flex items-center gap-1 text-xs text-green-400">
                <TrendingDown className="h-3 w-3" />
                <span>-12% faster</span>
              </div>
            </div>
            {/* Time trend sparkline */}
            <svg className="h-12 w-full opacity-50" viewBox="0 0 200 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M0 30 L20 28 L40 32 L60 26 L80 24 L100 22 L120 20 L140 18 L160 16 L180 14 L200 12"
                stroke="#3b82f6"
                strokeWidth="2"
                fill="none"
              />
            </svg>
          </CardContent>
        </Card>

        {/* Approvals Pending */}
        <Card className="glass-card glass-warning border">
          <CardHeader className="relative flex flex-row items-start justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-300">Approvals Pending</CardTitle>
            <button className="text-gray-400 hover:text-white">
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </CardHeader>
          <CardContent className="relative space-y-3">
            <div className="space-y-1">
              <div className="text-3xl font-bold text-white">24</div>
              <div className="text-xs text-gray-400">12 high priority</div>
              <div className="flex items-center gap-1 text-xs text-yellow-400">
                <AlertCircle className="h-3 w-3" />
                <span>3 expiring soon</span>
              </div>
            </div>
            {/* Pending trend sparkline */}
            <svg className="h-12 w-full opacity-50" viewBox="0 0 200 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M0 35 L20 32 L40 30 L60 28 L80 32 L100 30 L120 28 L140 25 L160 22 L180 20 L200 18"
                stroke="#3b82f6"
                strokeWidth="2"
                fill="none"
              />
            </svg>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        {/* Live Funnel */}
        <Card className="relative overflow-hidden border-white/10 bg-[#0d0d0d]/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white">Live Funnel</CardTitle>
            <p className="text-sm text-gray-400">Transaction flow stages</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <FunnelStage label="Created" count={2847} percentage={100} width={100} dropoff={null} />
              <FunnelStage label="Approved" count={2820} percentage={99} width={98} dropoff={0.9} />
              <FunnelStage label="ACC" count={2815} percentage={98.9} width={96} dropoff={0.2} />
              <FunnelStage label="Routed" count={2810} percentage={98.7} width={94} dropoff={0.2} />
              <FunnelStage label="Dispatched" count={2805} percentage={98.5} width={92} dropoff={0.2} />
              <FunnelStage label="Settled" count={2795} percentage={98.2} width={90} dropoff={0.4} />
            </div>

            {/* Summary Stats */}
            <div className="mt-6 grid grid-cols-3 gap-4 rounded-lg border border-white/10 bg-white/5 p-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">2,795</div>
                <div className="text-xs text-gray-400">Settled Today</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">98.2%</div>
                <div className="text-xs text-gray-400">Completion Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">52</div>
                <div className="text-xs text-gray-400">Total Dropoffs</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Vendor Payments and Loan Disbursements */}
        <div className="grid gap-4 lg:grid-cols-2">
          <VendorPaymentsCard />
          <LoanDisbursementsCard />
        </div>

        {/* SLA Breaches */}
        <Card className="relative overflow-hidden border-white/10 bg-[#0d0d0d]/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-white">SLA Breaches</CardTitle>
            <p className="text-sm text-gray-400">Breach counts over time</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={slaBreachData}>
                <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: "12px" }} />
                <YAxis stroke="#6b7280" style={{ fontSize: "12px" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1a1a1a",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "8px",
                  }}
                  labelStyle={{ color: "#fff" }}
                />
                <Bar dataKey="expiry" fill="#f97316" name="Expiry Breaches" />
                <Bar dataKey="rail" fill="#ef4444" name="Rail Failures" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 flex items-center justify-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded bg-orange-500" />
                <span className="text-gray-400">Expiry Breaches</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded bg-red-500" />
                <span className="text-gray-400">Rail Failures</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Events and Open Tasks side by side */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Recent Events Feed */}
        <Card className="relative overflow-hidden border-white/10 bg-[#0d0d0d]/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Recent Events</CardTitle>
            <button className="text-sm text-blue-400 hover:text-blue-300">View all</button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <EventItem
                icon={<CheckCircle2 className="h-4 w-4 text-green-400" />}
                title="Payment settled successfully"
                description="TXN-2847 • ₹2,45,000 • IMPS"
                time="2 min ago"
              />
              <EventItem
                icon={<AlertCircle className="h-4 w-4 text-yellow-400" />}
                title="Approval required"
                description="Batch-1024 • 45 transactions • High priority"
                time="5 min ago"
              />
              <EventItem
                icon={<Clock className="h-4 w-4 text-blue-400" />}
                title="Recon exception detected"
                description="UTR mismatch • ₹1,20,000 • NEFT"
                time="12 min ago"
              />
              <EventItem
                icon={<XCircle className="h-4 w-4 text-red-400" />}
                title="Rail failure"
                description="TXN-2842 • RTGS timeout • Retrying"
                time="18 min ago"
              />
              <EventItem
                icon={<CheckCircle2 className="h-4 w-4 text-green-400" />}
                title="Batch approved"
                description="Batch-1023 • 120 transactions • ₹8.4Cr"
                time="25 min ago"
              />
            </div>
          </CardContent>
        </Card>

        {/* Open Tasks with Overdue Chart */}
        <Card className="relative overflow-hidden border-white/10 bg-[#0d0d0d]/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Open Tasks</CardTitle>
            <span className="text-sm text-gray-400">28 overdue</span>
          </CardHeader>
          <CardContent>
            <div className="mb-6 space-y-3">
              <TaskItem
                title="Approve high-value batch"
                description="Batch-1024 • 45 txns • ₹12.5Cr"
                priority="high"
                time="Due in 2h"
              />
              <TaskItem
                title="Resolve recon exception"
                description="UTR-8472 • ₹1.2L mismatch"
                priority="medium"
                time="Due today"
              />
              <TaskItem
                title="Review investigation case"
                description="Case-892 • Suspicious pattern"
                priority="high"
                time="Overdue 1d"
              />
              <TaskItem
                title="Vendor payouts pending approval"
                description="5 payouts require approver action"
                priority="medium"
                time="Due today"
              />
              <TaskItem
                title="Loan disbursements stuck in routing"
                description="2 disbursements awaiting IMPS retry"
                priority="high"
                time="Investigate now"
              />
            </div>

            {/* Overdue Tasks Bar Chart */}
            <div className="rounded-lg border border-white/10 bg-white/5 p-4">
              <h4 className="mb-3 text-sm font-medium text-white">Overdue by Category</h4>
              <ResponsiveContainer width="100%" height={150}>
                <BarChart data={overdueTasksData} layout="vertical">
                  <XAxis type="number" stroke="#6b7280" style={{ fontSize: "12px" }} />
                  <YAxis dataKey="category" type="category" stroke="#6b7280" style={{ fontSize: "12px" }} width={80} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1a1a1a",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: "8px",
                    }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

"use client"

import { Cell, Pie, PieChart, Bar, BarChart, XAxis, YAxis, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const loanTypeData = [
  { name: "Personal", value: 45, fill: "#10b981" },
  { name: "MSME", value: 30, fill: "#3b82f6" },
  { name: "Business", value: 25, fill: "#8b5cf6" },
]

const creditScoreData = [
  { range: "<600", count: 15 },
  { range: "600-700", count: 45 },
  { range: "700-800", count: 95 },
  { range: ">800", count: 55 },
]

export function LoanPortfolioCharts() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-medium text-slate-200 mb-3">Loan Distribution by Type</h3>
        <ChartContainer
          config={{
            value: {
              label: "Loans",
              color: "hsl(var(--chart-1))",
            },
          }}
          className="h-[150px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={loanTypeData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={60}
                paddingAngle={2}
                dataKey="value"
              >
                {loanTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <ChartTooltip content={<ChartTooltipContent />} />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>
        <div className="flex justify-center gap-4 mt-2">
          {loanTypeData.map((item) => (
            <div key={item.name} className="flex items-center gap-1">
              <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.fill }} />
              <span className="text-xs text-slate-400">{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-slate-200 mb-3">Disbursements by Credit Score</h3>
        <ChartContainer
          config={{
            count: {
              label: "Count",
              color: "#10b981",
            },
          }}
          className="h-[150px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={creditScoreData}>
              <XAxis dataKey="range" stroke="#64748b" fontSize={10} />
              <YAxis stroke="#64748b" fontSize={10} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>
    </div>
  )
}

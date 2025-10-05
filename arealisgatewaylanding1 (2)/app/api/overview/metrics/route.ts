import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Aggregate data from MCP, PDR, ARL services
    const overviewData = {
      todayVolume: 15420,
      approvalsPending: 23,
      liveFunnel: 156,
      vendorPayments: 8920,
      loanDisbursements: 6500,
      slaBreaches: 3,
      recentEvents: [
        {
          id: "EVT-001",
          type: "TRANSACTION_COMPLETED",
          message: "Batch B-2025-001 processed successfully",
          timestamp: "2025-01-05T10:30:00Z",
          severity: "info"
        },
        {
          id: "EVT-002", 
          type: "SLA_BREACH",
          message: "Transaction TXN-001 exceeded SLA",
          timestamp: "2025-01-05T10:25:00Z",
          severity: "warning"
        }
      ],
      openTasks: [
        {
          id: "TASK-001",
          title: "Review failed transaction L-2",
          priority: "High",
          assignee: "Operations Team",
          dueDate: "2025-01-05T18:00:00Z"
        },
        {
          id: "TASK-002",
          title: "Update KYC for Beta Corp",
          priority: "Medium", 
          assignee: "Compliance Team",
          dueDate: "2025-01-06T12:00:00Z"
        }
      ],
      metrics: {
        totalTransactions: 15420,
        successRate: 98.1,
        avgProcessingTime: "2.3s",
        complianceRate: 99.5
      }
    }

    return NextResponse.json(overviewData)
  } catch (error) {
    console.error('Overview metrics API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get open tasks from ACC, ARL, RCA
    const openTasks = [
      {
        id: "TASK-001",
        title: "Review failed transaction L-2",
        description: "Transaction L-2 failed due to sanction list match",
        priority: "High",
        assignee: "Operations Team",
        dueDate: "2025-01-05T18:00:00Z",
        status: "OPEN",
        source: "ACC",
        relatedTransaction: "TXN-2025-001",
        createdAt: "2025-01-05T10:30:00Z"
      },
      {
        id: "TASK-002",
        title: "Update KYC for Beta Corp",
        description: "Re-verify KYC details for Beta Corp using updated UIDAI/PAN data",
        priority: "Medium",
        assignee: "Compliance Team",
        dueDate: "2025-01-06T12:00:00Z",
        status: "OPEN",
        source: "RCA",
        relatedTransaction: "TXN-2025-001",
        createdAt: "2025-01-05T10:25:00Z"
      },
      {
        id: "TASK-003",
        title: "Reconcile orphan transaction",
        description: "Transaction TXN-2025-002 has no matching bank statement",
        priority: "Medium",
        assignee: "ARL Team",
        dueDate: "2025-01-06T09:00:00Z",
        status: "IN_PROGRESS",
        source: "ARL",
        relatedTransaction: "TXN-2025-002",
        createdAt: "2025-01-05T10:20:00Z"
      },
      {
        id: "TASK-004",
        title: "Investigate root cause for TXN-2025-003",
        description: "Analyze why transaction TXN-2025-003 failed",
        priority: "Low",
        assignee: "RCA Team",
        dueDate: "2025-01-07T15:00:00Z",
        status: "OPEN",
        source: "RCA",
        relatedTransaction: "TXN-2025-003",
        createdAt: "2025-01-05T10:15:00Z"
      }
    ]

    return NextResponse.json({
      total: openTasks.length,
      tasks: openTasks,
      summary: {
        high: openTasks.filter(t => t.priority === "High").length,
        medium: openTasks.filter(t => t.priority === "Medium").length,
        low: openTasks.filter(t => t.priority === "Low").length,
        open: openTasks.filter(t => t.status === "OPEN").length,
        inProgress: openTasks.filter(t => t.status === "IN_PROGRESS").length
      }
    })
  } catch (error) {
    console.error('Open tasks API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

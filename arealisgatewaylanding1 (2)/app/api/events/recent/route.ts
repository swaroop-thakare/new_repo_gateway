import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get recent events from MCP, ARL, PDR
    const recentEvents = [
      {
        id: "EVT-001",
        type: "TRANSACTION_COMPLETED",
        source: "MCP",
        message: "Batch B-2025-001 processed successfully",
        timestamp: "2025-01-05T10:30:00Z",
        severity: "info",
        data: {
          batchId: "B-2025-001",
          transactionCount: 25,
          successRate: 100
        }
      },
      {
        id: "EVT-002",
        type: "RECONCILIATION_COMPLETED",
        source: "ARL",
        message: "ARL reconciliation completed for batch B-2025-001",
        timestamp: "2025-01-05T10:25:00Z",
        severity: "info",
        data: {
          batchId: "B-2025-001",
          matchedTransactions: 23,
          exceptions: 2
        }
      },
      {
        id: "EVT-003",
        type: "ROUTE_SELECTED",
        source: "PDR",
        message: "IMPS route selected for transaction TXN-2025-001",
        timestamp: "2025-01-05T10:20:00Z",
        severity: "info",
        data: {
          transactionId: "TXN-2025-001",
          selectedRoute: "IMPS@HDFC",
          estimatedTime: "2 minutes"
        }
      },
      {
        id: "EVT-004",
        type: "SLA_BREACH",
        source: "MCP",
        message: "Transaction TXN-2025-002 exceeded SLA",
        timestamp: "2025-01-05T10:15:00Z",
        severity: "warning",
        data: {
          transactionId: "TXN-2025-002",
          expectedTime: "2 minutes",
          actualTime: "5 minutes"
        }
      },
      {
        id: "EVT-005",
        type: "COMPLIANCE_FAILURE",
        source: "ACC",
        message: "Sanction list match detected for Beta Corp",
        timestamp: "2025-01-05T10:10:00Z",
        severity: "error",
        data: {
          beneficiary: "Beta Corp",
          reason: "SANCTION_LIST_MATCH",
          action: "TRANSACTION_BLOCKED"
        }
      }
    ]

    return NextResponse.json({
      total: recentEvents.length,
      events: recentEvents,
      summary: {
        info: recentEvents.filter(e => e.severity === "info").length,
        warnings: recentEvents.filter(e => e.severity === "warning").length,
        errors: recentEvents.filter(e => e.severity === "error").length
      }
    })
  } catch (error) {
    console.error('Recent events API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

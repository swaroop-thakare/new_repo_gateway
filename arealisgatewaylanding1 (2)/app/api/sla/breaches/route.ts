import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get SLA breaches from PDR and RCA
    const slaBreaches = [
      {
        id: "SLA-001",
        transactionId: "TXN-2025-001",
        breachType: "PROCESSING_TIME",
        expectedTime: "2 minutes",
        actualTime: "5 minutes",
        severity: "HIGH",
        assignedTo: "Operations Team",
        status: "INVESTIGATING",
        timestamp: "2025-01-05T10:30:00Z",
        rcaResult: "Network latency in PDR routing"
      },
      {
        id: "SLA-002",
        transactionId: "TXN-2025-002",
        breachType: "RESPONSE_TIME",
        expectedTime: "30 seconds",
        actualTime: "2 minutes",
        severity: "MEDIUM",
        assignedTo: "Technical Team",
        status: "RESOLVED",
        timestamp: "2025-01-05T09:45:00Z",
        rcaResult: "Database connection timeout"
      }
    ]

    return NextResponse.json({
      total: slaBreaches.length,
      breaches: slaBreaches,
      summary: {
        totalBreaches: slaBreaches.length,
        highSeverity: slaBreaches.filter(b => b.severity === "HIGH").length,
        resolved: slaBreaches.filter(b => b.status === "RESOLVED").length,
        investigating: slaBreaches.filter(b => b.status === "INVESTIGATING").length
      }
    })
  } catch (error) {
    console.error('SLA breaches API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

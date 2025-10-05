import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get pending approvals from ACC and MCP
    const pendingApprovals = [
      {
        id: "APP-001",
        transactionId: "TXN-2025-001",
        amount: 50000,
        beneficiary: "ABC Corp",
        reason: "Amount exceeds limit",
        priority: "High",
        submittedBy: "System",
        submittedAt: "2025-01-05T10:00:00Z",
        status: "PENDING",
        accDecision: "FAIL",
        mcpStatus: "AWAITING_APPROVAL"
      },
      {
        id: "APP-002",
        transactionId: "TXN-2025-002", 
        amount: 25000,
        beneficiary: "XYZ Ltd",
        reason: "KYC verification required",
        priority: "Medium",
        submittedBy: "Compliance Team",
        submittedAt: "2025-01-05T09:30:00Z",
        status: "PENDING",
        accDecision: "HOLD",
        mcpStatus: "AWAITING_APPROVAL"
      }
    ]

    return NextResponse.json({
      total: pendingApprovals.length,
      approvals: pendingApprovals
    })
  } catch (error) {
    console.error('Pending approvals API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

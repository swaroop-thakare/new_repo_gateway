import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get payment reports from MCP and ARL
    const paymentReport = {
      summary: {
        totalPayments: 8920,
        successfulPayments: 8750,
        failedPayments: 170,
        successRate: 98.1
      },
      byType: [
        {
          type: "Vendor Payments",
          count: 4500,
          amount: 12500000,
          successRate: 98.5
        },
        {
          type: "Payroll",
          count: 3200,
          amount: 8500000,
          successRate: 99.2
        },
        {
          type: "Loan Disbursements",
          count: 1220,
          amount: 15000000,
          successRate: 96.8
        }
      ],
      recentTransactions: [
        {
          id: "TXN-2025-001",
          type: "Vendor Payment",
          amount: 50000,
          beneficiary: "ABC Corp",
          status: "COMPLETED",
          timestamp: "2025-01-05T10:30:00Z",
          utr: "IFT20251005001254"
        },
        {
          id: "TXN-2025-002",
          type: "Payroll",
          amount: 25000,
          beneficiary: "Employee 001",
          status: "COMPLETED", 
          timestamp: "2025-01-05T10:25:00Z",
          utr: "IFT20251005001255"
        }
      ],
      generatedAt: "2025-01-05T10:30:00Z"
    }

    return NextResponse.json(paymentReport)
  } catch (error) {
    console.error('Payments report API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get reconciled ledger data from ARL
    const reconciledData = {
      summary: {
        totalTransactions: 15420,
        reconciled: 15200,
        pending: 180,
        exceptions: 40,
        reconciliationRate: 98.8
      },
      journalEntries: [
        {
          id: "J-001",
          transactionId: "TXN-2025-001",
          debit: "Expense:Vendors",
          credit: "Bank:HDFC",
          amount: 50000,
          status: "POSTED",
          timestamp: "2025-01-05T10:30:00Z",
          utr: "IFT20251005001254"
        },
        {
          id: "J-002",
          transactionId: "TXN-2025-002",
          debit: "Expense:Payroll",
          credit: "Bank:SBI",
          amount: 25000,
          status: "POSTED",
          timestamp: "2025-01-05T10:25:00Z",
          utr: "IFT20251005001255"
        },
        {
          id: "J-003",
          transactionId: "TXN-2025-003",
          debit: "Expense:Loan Disbursement",
          credit: "Bank:ICICI",
          amount: 100000,
          status: "PENDING",
          timestamp: "2025-01-05T10:20:00Z",
          utr: null
        }
      ],
      exceptions: [
        {
          id: "EXC-001",
          transactionId: "TXN-2025-004",
          type: "AMOUNT_MISMATCH",
          description: "Bank statement shows ₹45,000 but ledger shows ₹50,000",
          status: "INVESTIGATING",
          assignedTo: "ARL Team",
          createdAt: "2025-01-05T10:15:00Z"
        },
        {
          id: "EXC-002",
          transactionId: "TXN-2025-005",
          type: "MISSING_UTR",
          description: "Transaction completed but no UTR received from bank",
          status: "OPEN",
          assignedTo: "Operations Team",
          createdAt: "2025-01-05T10:10:00Z"
        }
      ],
      generatedAt: "2025-01-05T10:30:00Z"
    }

    return NextResponse.json(reconciledData)
  } catch (error) {
    console.error('Ledger reconciled API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

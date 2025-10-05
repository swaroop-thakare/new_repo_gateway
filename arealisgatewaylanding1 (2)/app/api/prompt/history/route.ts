import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const line_id = searchParams.get('line_id')
    const batch_id = searchParams.get('batch_id')

    // Mock query history - in production, fetch from database
    const mockHistory = [
      {
        id: "1",
        query: "Why did line L-2 fail?",
        timestamp: "2025-01-05T10:00:00Z",
        line_id: line_id || "L-2",
        batch_id: batch_id || "B-2025-001",
        response: {
          failureReason: "Insufficient Balance",
          confidence: 95
        }
      },
      {
        id: "2",
        query: "What is the status of transaction TXN-001?",
        timestamp: "2025-01-05T09:30:00Z",
        line_id: line_id || "L-2",
        batch_id: batch_id || "B-2025-001",
        response: {
          failureReason: "Processing",
          confidence: 88
        }
      },
      {
        id: "3",
        query: "Show me all failed transactions in batch B-2025-001",
        timestamp: "2025-01-05T09:00:00Z",
        line_id: line_id || "L-2",
        batch_id: batch_id || "B-2025-001",
        response: {
          failureReason: "Multiple failures detected",
          confidence: 92
        }
      }
    ]

    return NextResponse.json(mockHistory)
  } catch (error) {
    console.error('History API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

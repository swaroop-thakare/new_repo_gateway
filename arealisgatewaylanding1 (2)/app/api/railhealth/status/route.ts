import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Mock rail health data - in production, fetch from PDR service
    const railHealthData = {
      timestamp: new Date().toISOString(),
      rails: [
        {
          name: "IMPS",
          status: "healthy",
          successRate: 98.5,
          avgResponseTime: "2.3s",
          failures: 12,
          lastFailure: "2025-01-05T08:30:00Z"
        },
        {
          name: "NEFT",
          status: "healthy", 
          successRate: 99.2,
          avgResponseTime: "45m",
          failures: 3,
          lastFailure: "2025-01-04T15:20:00Z"
        },
        {
          name: "RTGS",
          status: "degraded",
          successRate: 95.8,
          avgResponseTime: "1.2h",
          failures: 8,
          lastFailure: "2025-01-05T09:15:00Z"
        },
        {
          name: "UPI",
          status: "healthy",
          successRate: 99.7,
          avgResponseTime: "1.8s",
          failures: 2,
          lastFailure: "2025-01-03T14:45:00Z"
        }
      ],
      overallHealth: "healthy",
      totalTransactions: 15420,
      successRate: 98.1,
      criticalIssues: 0,
      warnings: 1
    }

    return NextResponse.json(railHealthData)
  } catch (error) {
    console.error('Rail Health API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

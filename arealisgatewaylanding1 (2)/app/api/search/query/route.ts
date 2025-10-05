import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json()
    
    if (!query) {
      return NextResponse.json({ 
        error: 'query is required' 
      }, { status: 400 })
    }

    // Mock search results - in production, this would search your database
    const mockResults = [
      {
        id: "TXN-2025-001",
        type: "transaction",
        title: "Transaction TXN-2025-001",
        description: "Payment to ABC Corp - ₹15,000",
        status: "completed",
        timestamp: "2025-01-05T10:30:00Z",
        amount: "₹15,000",
        beneficiary: "ABC Corp",
        utr: "IFT20251005001254"
      },
      {
        id: "B-2025-001",
        type: "batch",
        title: "Batch B-2025-001",
        description: "Vendor payments batch - 25 transactions",
        status: "processing",
        timestamp: "2025-01-05T10:00:00Z",
        amount: "₹2,50,000",
        beneficiary: "Multiple",
        utr: "N/A"
      },
      {
        id: "L-2",
        type: "line",
        title: "Line L-2",
        description: "Payment line item - ₹50,000",
        status: "failed",
        timestamp: "2025-01-05T10:15:00Z",
        amount: "₹50,000",
        beneficiary: "XYZ Ltd",
        utr: "N/A"
      }
    ]

    // Filter results based on query
    const filteredResults = mockResults.filter(result => 
      result.id.toLowerCase().includes(query.toLowerCase()) ||
      result.title.toLowerCase().includes(query.toLowerCase()) ||
      result.description.toLowerCase().includes(query.toLowerCase()) ||
      result.beneficiary.toLowerCase().includes(query.toLowerCase())
    )

    return NextResponse.json({
      query,
      results: filteredResults,
      total: filteredResults.length
    })
  } catch (error) {
    console.error('Search API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

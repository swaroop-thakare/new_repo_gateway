import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { line_id, batch_id, query } = await request.json()
    
    if (!line_id || !batch_id || !query) {
      return NextResponse.json({ 
        error: 'line_id, batch_id, and query are required' 
      }, { status: 400 })
    }

    // Call the Prompt Layer backend service
    try {
      const response = await fetch('http://localhost:8011/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          batch_id: batch_id,
          line_id: line_id
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Transform the backend response to frontend format
        const transformedResponse = {
          id: Date.now().toString(),
          query: data.query,
          timestamp: data.timestamp,
          line_id: line_id,
          batch_id: batch_id,
          response: {
            failureReason: data.response.failure_reason,
            detailedAnalysis: data.response.detailed_analysis,
            recommendedActions: data.response.recommended_actions.map((action: any, index: number) => ({
              priority: index + 1,
              action: action.action,
              timeline: action.estimated_time,
              responsibility: action.responsible_party,
              link: action.link || `/book-demo/ledger`
            })),
            additionalNotes: data.response.additional_notes,
            evidenceLinks: data.evidence_refs.map((ref: string, index: number) => ({
              name: `Evidence ${index + 1}`,
              url: ref
            })),
            confidence: Math.round(data.response.confidence_score * 100)
          }
        }

        return NextResponse.json(transformedResponse)
      } else {
        console.error('Prompt Layer service error:', response.status)
        // Fallback to mock response if service is unavailable
        return getMockResponse(query, line_id, batch_id)
      }
    } catch (error) {
      console.error('Error calling Prompt Layer service:', error)
      // Fallback to mock response if service is unavailable
      return getMockResponse(query, line_id, batch_id)
    }
  } catch (error) {
    console.error('Prompt API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

function getMockResponse(query: string, line_id: string, batch_id: string) {
  return NextResponse.json({
    id: Date.now().toString(),
    query: query,
    timestamp: new Date().toISOString(),
    line_id: line_id,
    batch_id: batch_id,
    response: {
      failureReason: "Insufficient Balance - Account HDFC0001234 has insufficient funds for transaction amount ₹50,000",
      detailedAnalysis: `
**Technical Analysis:**
- Transaction ID: TXN-2025-001-002
- Line ID: ${line_id}
- Batch: ${batch_id}
- Timestamp: ${new Date().toISOString()}
- Bank Response: "Insufficient Balance" (Code: 51)
- Available Balance: ₹25,000
- Required Amount: ₹50,000
- Shortfall: ₹25,000

**Root Cause Analysis:**
The transaction failed due to insufficient account balance. The remitter account (HDFC0001234) had only ₹25,000 available, but the transaction required ₹50,000. This is a common issue in high-volume payment processing where account balances are not updated in real-time.

**Confidence Score: 95%**
      `,
      recommendedActions: [
        {
          priority: 1,
          action: "Verify account balance with HDFC Bank",
          timeline: "Immediate",
          responsibility: "Operations Team",
          link: "/book-demo/ledger"
        },
        {
          priority: 2,
          action: "Contact customer for fund transfer",
          timeline: "Within 2 hours",
          responsibility: "Customer Service",
          link: "/book-demo/approvals"
        },
        {
          priority: 3,
          action: "Update payment retry logic",
          timeline: "Next business day",
          responsibility: "Engineering Team"
        }
      ],
      additionalNotes: "This transaction is part of a batch processing workflow. Consider implementing real-time balance checks before transaction initiation to prevent similar failures.",
      evidenceLinks: [
        {
          name: "Bank Statement (HDFC)",
          url: "s3://arealis-evidence/statements/HDFC_20250105.pdf"
        },
        {
          name: "Transaction Log",
          url: "s3://arealis-evidence/logs/TXN-2025-001-002.json"
        },
        {
          name: "ARL Reconciliation Report",
          url: `s3://arealis-evidence/arl/${batch_id}/${line_id}/arl.json`
        }
      ],
      confidence: 95
    }
  })
}
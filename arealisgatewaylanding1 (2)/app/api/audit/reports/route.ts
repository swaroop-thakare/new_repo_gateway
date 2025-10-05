import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Get audit reports from CRRAK
    const auditReports = [
      {
        id: "AUDIT-001",
        batchId: "B-2025-001",
        complianceStatus: "COMPLIANT",
        reportType: "REGULATORY",
        generatedAt: "2025-01-05T10:30:00Z",
        reportUrl: "s3://audit/HDFC/B-2025-001/audit_report.pdf",
        summary: {
          totalTransactions: 25,
          compliant: 25,
          nonCompliant: 0,
          complianceRate: 100
        },
        details: {
          accChecks: "All transactions passed ACC compliance",
          rcaAnalysis: "No root cause analysis required",
          arlReconciliation: "All transactions reconciled successfully",
          crrakAudit: "Audit trail complete and compliant"
        }
      },
      {
        id: "AUDIT-002",
        batchId: "B-2025-002",
        complianceStatus: "NON_COMPLIANT",
        reportType: "REGULATORY",
        generatedAt: "2025-01-05T09:45:00Z",
        reportUrl: "s3://audit/HDFC/B-2025-002/audit_report.pdf",
        summary: {
          totalTransactions: 30,
          compliant: 28,
          nonCompliant: 2,
          complianceRate: 93.3
        },
        details: {
          accChecks: "2 transactions failed ACC compliance",
          rcaAnalysis: "Root cause: Sanction list match for Beta Corp",
          arlReconciliation: "2 transactions failed reconciliation",
          crrakAudit: "Audit trail shows compliance violations"
        }
      }
    ]

    return NextResponse.json({
      total: auditReports.length,
      reports: auditReports,
      summary: {
        totalReports: auditReports.length,
        compliant: auditReports.filter(r => r.complianceStatus === "COMPLIANT").length,
        nonCompliant: auditReports.filter(r => r.complianceStatus === "NON_COMPLIANT").length,
        avgComplianceRate: auditReports.reduce((sum, r) => sum + r.summary.complianceRate, 0) / auditReports.length
      }
    })
  } catch (error) {
    console.error('Audit reports API error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

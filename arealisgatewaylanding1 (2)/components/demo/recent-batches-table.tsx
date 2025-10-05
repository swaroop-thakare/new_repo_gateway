import Link from "next/link"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

const rows = [
  {
    id: "B-1001",
    type: "Payroll",
    amount: "$243,500",
    status: "In Progress",
    submittedOn: "Sep 28, 2025",
    href: "/book-demo/payroll/1001",
  },
  {
    id: "B-1000",
    type: "Vendor Payment",
    amount: "$98,220",
    status: "Awaiting Approval",
    submittedOn: "Sep 27, 2025",
    href: "/book-demo/vendor-payments",
  },
  {
    id: "B-0999",
    type: "Loan Disbursement",
    amount: "$1,200,000",
    status: "Completed",
    submittedOn: "Sep 27, 2025",
    href: "/book-demo/loan-disbursements",
  },
  {
    id: "B-0998",
    type: "Payroll",
    amount: "$199,040",
    status: "Completed",
    submittedOn: "Sep 26, 2025",
    href: "/book-demo/payroll/998",
  },
  {
    id: "B-0997",
    type: "Payroll",
    amount: "$221,080",
    status: "In Progress",
    submittedOn: "Sep 25, 2025",
    href: "/book-demo/payroll/997",
  },
]

export function RecentBatchesTable() {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Batch ID</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Submitted On</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r) => (
            <TableRow key={r.id} className="hover:bg-muted/50 cursor-pointer">
              <TableCell>
                <Link href={r.href} aria-label={`View ${r.type} ${r.id}`} className="block w-full h-full py-2">
                  {r.id}
                </Link>
              </TableCell>
              <TableCell>
                <Link href={r.href} aria-label={`View ${r.type} ${r.id}`} className="block w-full h-full py-2">
                  {r.type}
                </Link>
              </TableCell>
              <TableCell>
                <Link href={r.href} aria-label={`View ${r.type} ${r.id}`} className="block w-full h-full py-2">
                  {r.amount}
                </Link>
              </TableCell>
              <TableCell>
                <Link href={r.href} aria-label={`View ${r.type} ${r.id}`} className="block w-full h-full py-2">
                  {r.status}
                </Link>
              </TableCell>
              <TableCell>
                <Link href={r.href} aria-label={`View ${r.type} ${r.id}`} className="block w-full h-full py-2">
                  {r.submittedOn}
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

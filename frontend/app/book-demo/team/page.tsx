import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function TeamPage() {
  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Team Management</h2>
        <Button className="bg-blue-600 text-white hover:bg-blue-700">Invite Team Member</Button>
      </header>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[
              { name: "Admin User", email: "admin@acme.com", role: "Admin", status: "Active" },
              { name: "Maker User", email: "maker@acme.com", role: "Maker", status: "Active" },
              { name: "Checker User", email: "checker@acme.com", role: "Checker", status: "Invited" },
            ].map((u) => (
              <TableRow key={u.email}>
                <TableCell>{u.name}</TableCell>
                <TableCell>{u.email}</TableCell>
                <TableCell>{u.role}</TableCell>
                <TableCell>{u.status}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

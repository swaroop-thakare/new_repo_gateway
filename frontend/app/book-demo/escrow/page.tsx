import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ShieldCheck, Landmark, Users, ArrowDownUp } from "lucide-react"

export default function EscrowTrackingPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-balance">Escrow Tracking</h1>
          <p className="text-sm text-muted-foreground text-pretty">
            Monitor balances, releases, and jurisdictional rules across all active escrows.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild>
            <Link href="/book-demo/create">{"Create Escrow"}</Link>
          </Button>
        </div>
      </div>

      {/* Overview cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="glass-card glass-primary">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total in escrow</span>
              <ShieldCheck className="h-4 w-4 text-primary" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{"$2.8M"}</div>
            <div className="text-xs text-muted-foreground">{"USD equivalent"}</div>
          </CardContent>
        </Card>

        <Card className="glass-card glass-success">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Active escrows</span>
              <Users className="h-4 w-4 text-primary" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <div className="text-xs text-muted-foreground">Across 5 parties</div>
          </CardContent>
        </Card>

        <Card className="glass-card glass-warning">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Pending releases</span>
              <ArrowDownUp className="h-4 w-4 text-primary" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2</div>
            <div className="text-xs text-muted-foreground">Dual-approval required</div>
          </CardContent>
        </Card>

        <Card className="glass-card glass-success">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Compliance</span>
              <Landmark className="h-4 w-4 text-primary" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{"Up to date"}</div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              <Badge variant="outline" className="bg-primary/20 text-primary ring-1 ring-primary/25 border-primary/25">
                {"IN: RBI"}
              </Badge>
              <Badge variant="outline" className="bg-primary/20 text-primary ring-1 ring-primary/25 border-primary/25">
                {"EU: PSD2"}
              </Badge>
              <Badge variant="outline" className="bg-primary/20 text-primary ring-1 ring-primary/25 border-primary/25">
                {"US: Reg E"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Accounts table */}
      <Card className="glass-card">
        <CardHeader className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <span>{"Escrow Accounts"}</span>
            <Badge variant="outline" className="bg-accent/20 text-foreground">
              3
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Escrow</TableHead>
                <TableHead>Parties</TableHead>
                <TableHead>Balance</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Jurisdiction</TableHead>
                <TableHead>Next milestone</TableHead>
                <TableHead className="text-right">{"Actions"}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[
                {
                  id: "ESC-1027",
                  parties: "Acme ↔ Northstar",
                  balance: "$1,150,000",
                  status: { label: "Active", tone: "success" as const },
                  juris: "IN",
                  milestone: "Docs verification • T+2",
                },
                {
                  id: "ESC-1026",
                  parties: "Bright Labs ↔ Nova",
                  balance: "$980,000",
                  status: { label: "Pending Release", tone: "warning" as const },
                  juris: "EU",
                  milestone: "Dual approval • Awaiting",
                },
                {
                  id: "ESC-1018",
                  parties: "Horizon ↔ Delta",
                  balance: "$720,000",
                  status: { label: "Closed", tone: "default" as const },
                  juris: "US",
                  milestone: "Archived",
                },
              ].map((row) => (
                <TableRow key={row.id}>
                  <TableCell className="font-medium">{row.id}</TableCell>
                  <TableCell>{row.parties}</TableCell>
                  <TableCell>{row.balance}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        row.status.tone === "success"
                          ? "bg-success/25 text-success-foreground border-success/30 ring-1 ring-success/25"
                          : row.status.tone === "warning"
                            ? "bg-warning/25 text-warning-foreground border-warning/30 ring-1 ring-warning/25"
                            : "bg-muted text-muted-foreground"
                      }
                    >
                      {row.status.label}
                    </Badge>
                  </TableCell>
                  <TableCell>{row.juris}</TableCell>
                  <TableCell className="text-muted-foreground">{row.milestone}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="outline" size="sm" aria-label={`View ${row.id}`}>
                      {"View"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Rules hint */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{"Rules in effect (auto-applied)"}</span>
            <Badge variant="outline" className="bg-primary/10 text-primary">
              {"Auto"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <li className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">{"India (RBI)"}</span>
                <Badge
                  variant="outline"
                  className="bg-warning/25 text-warning-foreground border-warning/30 ring-1 ring-warning/25"
                >
                  {"KYC/limits"}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">{"Release caps, beneficiary KYC, cut-off windows."}</p>
            </li>
            <li className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">{"EU (PSD2)"}</span>
                <Badge
                  variant="outline"
                  className="bg-primary/20 text-primary border-primary/25 ring-1 ring-primary/25"
                >
                  {"SCA"}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">{"Strong customer auth and reporting."}</p>
            </li>
            <li className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">{"US (Reg E)"}</span>
                <Badge
                  variant="outline"
                  className="bg-success/25 text-success-foreground border-success/30 ring-1 ring-success/25"
                >
                  {"Disclosures"}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">{"Notice and error-resolution timing."}</p>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

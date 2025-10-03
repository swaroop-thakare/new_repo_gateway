"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function CompanySettingsPage() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold">Settings</h2>
      </header>

      <Tabs defaultValue="routing" className="space-y-4">
        <TabsList className="flex flex-wrap gap-1">
          <TabsTrigger value="routing">Routing Preferences</TabsTrigger>
          <TabsTrigger value="compliance">Compliance Thresholds</TabsTrigger>
          <TabsTrigger value="policies">Policies & Versions</TabsTrigger>
          <TabsTrigger value="users">Users & Roles</TabsTrigger>
          <TabsTrigger value="privacy">PII Masking</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          {/* keep original tabs for backwards-compat */}
          <TabsTrigger value="api">API Credentials</TabsTrigger>
          <TabsTrigger value="general">General</TabsTrigger>
        </TabsList>

        {/* Routing Preferences */}
        <TabsContent value="routing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Cost vs Speed Bias</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <Label htmlFor="bias">Bias</Label>
              <Select defaultValue="balanced">
                <SelectTrigger id="bias" className="w-60">
                  <SelectValue placeholder="Select bias" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cost">Cost-optimized</SelectItem>
                  <SelectItem value="balanced">Balanced</SelectItem>
                  <SelectItem value="speed">Speed-optimized</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Allowed Rails & Caps</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Checkbox id="rail-imps" defaultChecked />
                  <Label htmlFor="rail-imps">IMPS</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox id="rail-neft" defaultChecked />
                  <Label htmlFor="rail-neft">NEFT</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox id="rail-rtgs" defaultChecked />
                  <Label htmlFor="rail-rtgs">RTGS</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox id="rail-upi" defaultChecked />
                  <Label htmlFor="rail-upi">UPI</Label>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <Label htmlFor="cap-imps">IMPS per txn cap (₹)</Label>
                  <Input id="cap-imps" type="number" className="mt-1 w-56" defaultValue={200000} />
                </div>
                <div>
                  <Label htmlFor="cap-neft">NEFT per txn cap (₹)</Label>
                  <Input id="cap-neft" type="number" defaultValue={2000000} className="mt-1 w-56" />
                </div>
                <div>
                  <Label htmlFor="cap-rtgs">RTGS per txn cap (₹)</Label>
                  <Input id="cap-rtgs" type="number" defaultValue={5000000} className="mt-1 w-56" />
                </div>
                <div>
                  <Label htmlFor="cap-upi">UPI per txn cap (₹)</Label>
                  <Input id="cap-upi" type="number" defaultValue={100000} className="mt-1 w-56" />
                </div>
                <Button className="mt-1 bg-blue-600 text-white hover:bg-blue-700">Save Routing</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Thresholds */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Approval Requirements</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <Label htmlFor="approval-threshold">Manual approval over (₹)</Label>
              <div className="flex items-center gap-2">
                <Input id="approval-threshold" type="number" defaultValue={100000} className="w-56" />
                <Button className="bg-blue-600 text-white hover:bg-blue-700">Save</Button>
              </div>
              <p className="text-sm text-muted-foreground">Transactions ≥ threshold require Compliance sign-off.</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Disallowed Countries & Watchlists</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Disallowed Countries</Label>
                <div className="flex items-center gap-2">
                  <Checkbox id="cntr-ru" />
                  <Label htmlFor="cntr-ru">Russia</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox id="cntr-ir" />
                  <Label htmlFor="cntr-ir">Iran</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox id="cntr-kp" />
                  <Label htmlFor="cntr-kp">North Korea</Label>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Watchlists</Label>
                <div className="flex items-center justify-between">
                  <span>UN Sanctions</span>
                  <Switch defaultChecked aria-label="UN Sanctions watchlist" />
                </div>
                <div className="flex items-center justify-between">
                  <span>OFAC</span>
                  <Switch defaultChecked aria-label="OFAC watchlist" />
                </div>
                <div className="flex items-center justify-between">
                  <span>Local PEP</span>
                  <Switch aria-label="Local PEP watchlist" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Policies & Versions */}
        <TabsContent value="policies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Active Policy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2">
                <Badge className="bg-emerald-600">Active</Badge>
                <span className="font-mono text-sm">v2.3</span>
              </div>
              <div className="rounded-md border p-3 text-sm">
                Change log:
                <ul className="ml-4 list-disc">
                  <li>v2.3: Urgency-based routing preference tweak</li>
                  <li>v2.2: Raised IMPS cap to ₹2L</li>
                  <li>v2.1: Added PII masking to logs</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Users & Roles */}
        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Team Access</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { name: "A. Gupta", email: "anita@company.com", role: "Ops" },
                { name: "M. Iyer", email: "mohan@company.com", role: "Finance" },
                { name: "S. Khan", email: "sara@company.com", role: "Compliance" },
              ].map((u, i) => (
                <div key={i} className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3">
                  <div>
                    <div className="font-medium">{u.name}</div>
                    <div className="text-xs text-muted-foreground">{u.email}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="sr-only">Role</Label>
                    <Select defaultValue={u.role.toLowerCase()}>
                      <SelectTrigger className="w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ops">Ops</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="compliance">Compliance</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button variant="outline">Update</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* PII Masking */}
        <TabsContent value="privacy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">PII Controls</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Mask PII in views</span>
                <Switch defaultChecked aria-label="PII masking in views" />
              </div>
              <div className="flex items-center justify-between">
                <span>Mask PII in exports</span>
                <Switch defaultChecked aria-label="PII masking in exports" />
              </div>
              <div>
                <Label>Vault tokenization rules</Label>
                <pre className="mt-2 rounded-md border bg-muted p-3 text-xs">
                  {`rules:
  account_number: tokenized_last4
  ifsc: passthrough
  phone: redacted_full`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integrations */}
        <TabsContent value="integrations" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">Bank Feeds</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-muted-foreground">Webhooks and SFTP folders</p>
                <div className="flex items-center gap-2 text-xs">
                  <Badge variant="outline">HDFC</Badge>
                  <Badge variant="outline">ICICI</Badge>
                </div>
                <Button className="bg-blue-600 text-white hover:bg-blue-700">Configure</Button>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">ERP</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-muted-foreground">Tally, Zoho, NetSuite connectors</p>
                <Button variant="outline">Connect ERP</Button>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">Webhooks</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-muted-foreground">Subscribe to events</p>
                <ul className="ml-4 list-disc text-sm">
                  <li>ledger_posted</li>
                  <li>recon_resolved</li>
                  <li>filing_ready</li>
                </ul>
                <Button variant="outline">Manage Subscriptions</Button>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">API Keys</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-muted-foreground">Rotate and scope keys</p>
                <div className="flex items-center gap-2">
                  <code className="rounded bg-muted px-2 py-1 text-xs">sk_live_••••••</code>
                  <Badge className="bg-emerald-600">Active</Badge>
                </div>
                <Button className="bg-blue-600 text-white hover:bg-blue-700">Generate New Key</Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* keep existing API/general tabs content for compatibility */}
        <TabsContent value="api" className="space-y-3">
          <div className="rounded-md border p-4">
            <div className="mb-3 text-sm text-slate-600">Manage your API keys for programmatic access.</div>
            <Button className="bg-blue-600 text-white hover:bg-blue-700">Generate New API Key</Button>
          </div>
        </TabsContent>

        <TabsContent value="general">
          <div className="rounded-md border p-4 text-sm text-slate-600">General company settings go here.</div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

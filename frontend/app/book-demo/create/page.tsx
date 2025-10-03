"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { Upload, AlertCircle, CheckCircle2 } from "lucide-react"

export default function CreatePage() {
  const [requiresApproval, setRequiresApproval] = useState(true)

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Create Payment</h1>
        <p className="text-gray-400">Single payment or batch upload</p>
      </div>

      <Tabs defaultValue="single" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="single">Single Payment</TabsTrigger>
          <TabsTrigger value="batch">Batch Upload</TabsTrigger>
        </TabsList>

        <TabsContent value="single" className="space-y-6">
          <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent backdrop-blur-xl">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
            <CardHeader className="relative">
              <CardTitle className="text-white">Payment Details</CardTitle>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="ifsc" className="text-gray-300">
                    IFSC Code
                  </Label>
                  <Input
                    id="ifsc"
                    placeholder="HDFC0001234"
                    className="bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                  />
                  <p className="text-xs text-gray-400">Bank name will appear here</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="account" className="text-gray-300">
                    Account Number
                  </Label>
                  <Input
                    id="account"
                    placeholder="1234567890"
                    className="bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="amount" className="text-gray-300">
                    Amount (₹)
                  </Label>
                  <Input
                    id="amount"
                    type="number"
                    placeholder="25000"
                    className="bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="purpose" className="text-gray-300">
                    Purpose Code
                  </Label>
                  <Input
                    id="purpose"
                    placeholder="P0101"
                    className="bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes" className="text-gray-300">
                  Notes
                </Label>
                <Textarea
                  id="notes"
                  placeholder="Payment for invoice #INV-2024-001"
                  className="bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="urgency" className="text-gray-300">
                  Urgency
                </Label>
                <select
                  id="urgency"
                  className="flex h-10 w-full rounded-md border border-white/10 bg-gradient-to-br from-blue-600/20 to-blue-500/10 px-3 py-2 text-sm text-white backdrop-blur-xl"
                >
                  <option className="bg-[#0d0d0d] text-white">Standard</option>
                  <option className="bg-[#0d0d0d] text-white">High</option>
                  <option className="bg-[#0d0d0d] text-white">Critical</option>
                </select>
              </div>

              <div className="flex items-center justify-between rounded-lg border border-white/10 bg-gradient-to-br from-blue-600/20 to-blue-500/10 p-4 backdrop-blur-xl">
                <div className="space-y-0.5">
                  <Label htmlFor="approval" className="text-white">
                    Requires approval before dispatch
                  </Label>
                  <p className="text-sm text-gray-400">On by default for amounts ≥ ₹10,000</p>
                </div>
                <Switch
                  id="approval"
                  checked={requiresApproval}
                  onCheckedChange={setRequiresApproval}
                  className="data-[state=checked]:bg-blue-600"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent backdrop-blur-xl">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
            <CardHeader className="relative">
              <CardTitle className="text-white">Routing Hints</CardTitle>
            </CardHeader>
            <CardContent className="relative space-y-3">
              <div className="flex items-start gap-2 text-sm">
                <AlertCircle className="mt-0.5 h-4 w-4 text-amber-400" />
                <div>
                  <p className="font-medium text-white">NEFT window closes in 45 minutes</p>
                  <p className="text-gray-400">Consider IMPS for faster settlement</p>
                </div>
              </div>
              <div className="flex items-start gap-2 text-sm">
                <CheckCircle2 className="mt-0.5 h-4 w-4 text-green-400" />
                <div>
                  <p className="font-medium text-white">IMPS success rate: 99.2%</p>
                  <p className="text-gray-400">Estimated fee: ₹5, ETA: 2 minutes</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-3">
            <Button variant="outline" className="border-white/10 text-gray-300 hover:bg-white/5 bg-transparent">
              Cancel
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">Submit Payment</Button>
          </div>
        </TabsContent>

        <TabsContent value="batch" className="space-y-6">
          <Card className="relative overflow-hidden border-white/10 bg-gradient-to-br from-blue-600/20 via-blue-500/10 to-transparent backdrop-blur-xl">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent" />
            <CardHeader className="relative">
              <CardTitle className="text-white">Batch Upload</CardTitle>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">Upload a CSV file with payment details</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-white/10 text-gray-300 hover:bg-white/5 bg-transparent"
                >
                  Download Template
                </Button>
              </div>

              <div className="flex min-h-[200px] items-center justify-center rounded-lg border-2 border-dashed border-blue-500/30 bg-gradient-to-br from-blue-600/10 to-blue-500/5 backdrop-blur-xl">
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-blue-400" />
                  <p className="mt-2 text-sm font-medium text-white">Drop CSV file here</p>
                  <p className="text-xs text-gray-400">or click to browse</p>
                </div>
              </div>

              <div className="rounded-lg border border-blue-500/30 bg-gradient-to-br from-blue-600/20 to-blue-500/10 p-4 backdrop-blur-xl">
                <p className="text-sm font-medium text-blue-300">Validation checks</p>
                <ul className="mt-2 space-y-1 text-sm text-blue-200">
                  <li>✓ IFSC code validation</li>
                  <li>✓ Duplicate detection</li>
                  <li>✓ Amount caps per rail</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-3">
            <Button variant="outline" className="border-white/10 text-gray-300 hover:bg-white/5 bg-transparent">
              Cancel
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">Upload & Validate</Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

"use client"

import { CheckCircle, Copy, RotateCcw, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"

interface SuccessStateProps {
  batchId: string
  onReset: () => void
}

export function SuccessState({ batchId, onReset }: SuccessStateProps) {
  const [copied, setCopied] = useState(false)

  const copyBatchId = async () => {
    await navigator.clipboard.writeText(batchId)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="text-center space-y-6 py-8">
      <div className="w-20 h-20 bg-success/10 rounded-full flex items-center justify-center mx-auto">
        <CheckCircle className="w-12 h-12 text-success" />
      </div>

      <div className="space-y-3">
        <h2 className="text-2xl font-bold text-foreground">Batch Submitted Successfully</h2>
        <p className="text-muted-foreground text-balance max-w-md mx-auto leading-relaxed">
          Your payout batch has been securely sent to Arealis Gateway for processing. You will be notified upon
          completion.
        </p>
      </div>

      <div className="flex items-center justify-center gap-2 p-4 bg-muted/30 rounded-lg">
        <span className="text-sm font-medium text-foreground">Batch ID:</span>
        <Badge variant="secondary" className="font-mono text-sm">
          {batchId}
        </Badge>
        <Button
          variant="ghost"
          size="icon"
          onClick={copyBatchId}
          className="h-6 w-6 text-muted-foreground hover:text-foreground"
        >
          <Copy className="w-3 h-3" />
        </Button>
        {copied && <span className="text-xs text-success font-medium">Copied!</span>}
      </div>

            <div className="flex justify-center mt-8">
              <Button onClick={onReset} variant="outline" className="bg-transparent" size="lg">
                <RotateCcw className="w-4 h-4 mr-2" />
                Upload Another Batch
              </Button>
            </div>
    </div>
  )
}

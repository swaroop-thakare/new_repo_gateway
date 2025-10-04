"use client"

import { FileText, Radio } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface MethodSelectionProps {
  onSelectMethod: (method: "batch" | "streaming") => void
}

export function MethodSelection({ onSelectMethod }: MethodSelectionProps) {
  return (
    <div className="max-w-5xl mx-auto">
      <Card className="shadow-lg">
        <CardHeader className="text-center pb-8">
          <CardTitle className="text-3xl font-semibold text-balance">Choose Your Ingestion Method</CardTitle>
        </CardHeader>

        <CardContent className="pb-8">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Batch Payout Column */}
            <div className="flex flex-col items-center text-center space-y-6 p-6 rounded-lg border border-border hover:border-primary/50 transition-colors">
              <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
                <FileText className="w-10 h-10 text-primary" />
              </div>

              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-foreground">Batch Payout (CSV)</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Upload a CSV file containing multiple transaction records for batch processing.
                </p>
              </div>

              <Button onClick={() => onSelectMethod("batch")} size="lg" className="w-full">
                Start Batch Upload
              </Button>
            </div>

            {/* Real-time Streaming Column */}
            <div className="flex flex-col items-center text-center space-y-6 p-6 rounded-lg border border-border hover:border-secondary/50 transition-colors">
              <div className="w-20 h-20 bg-secondary/10 rounded-full flex items-center justify-center">
                <Radio className="w-10 h-10 text-secondary" />
              </div>

              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-foreground">Real-time Streaming</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Simulate a live data stream from your ERP system for real-time compliance validation.
                </p>
              </div>

              <Button onClick={() => onSelectMethod("streaming")} variant="outline" size="lg" className="w-full">
                Begin Live Stream
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

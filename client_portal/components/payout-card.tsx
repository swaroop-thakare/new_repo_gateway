"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { FileUpload } from "@/components/file-upload"
import { BatchPreview } from "@/components/batch-preview"
import { SuccessState } from "@/components/success-state"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

type PayoutState = "initial" | "file-selected" | "submitting" | "success"

interface CSVData {
  headers: string[]
  rows: string[][]
}

export function PayoutCard() {
  const [state, setState] = useState<PayoutState>("initial")
  const [file, setFile] = useState<File | null>(null)
  const [csvData, setCsvData] = useState<CSVData | null>(null)
  const [batchId, setBatchId] = useState<string>("")

  const handleFileSelect = useCallback((selectedFile: File, data: CSVData) => {
    setFile(selectedFile)
    setCsvData(data)
    setState("file-selected")
  }, [])

  const handleFileRemove = useCallback(() => {
    setFile(null)
    setCsvData(null)
    setState("initial")
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!file || !csvData) return

    setState("submitting")

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Generate batch ID
    const now = new Date()
    const dateStr = now.toISOString().split("T")[0]
    const timeStr = String(now.getHours()).padStart(2, "0") + String(now.getMinutes()).padStart(2, "0")
    setBatchId(`B-${dateStr}-${timeStr}`)

    setState("success")
  }, [file, csvData])

  const handleReset = useCallback(() => {
    setFile(null)
    setCsvData(null)
    setBatchId("")
    setState("initial")
  }, [])

  if (state === "success") {
    return (
      <Card className="w-full max-w-2xl mx-auto shadow-lg">
        <CardContent className="p-8">
          <SuccessState batchId={batchId} onReset={handleReset} />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg">
      <CardHeader className="pb-6">
        <CardTitle className="text-2xl font-semibold text-balance">Create a New Payout Batch</CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        <FileUpload file={file} onFileSelect={handleFileSelect} onFileRemove={handleFileRemove} />

        {csvData && state === "file-selected" && <BatchPreview data={csvData} />}

        <Button
          onClick={handleSubmit}
          disabled={!file || state === "submitting"}
          className="w-full h-12 text-base font-medium"
          size="lg"
        >
          {state === "submitting" ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Processing Batch...
            </>
          ) : (
            "Proceed to Payout"
          )}
        </Button>
      </CardContent>
    </Card>
  )
}

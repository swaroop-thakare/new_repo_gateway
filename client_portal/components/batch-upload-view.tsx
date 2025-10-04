"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { FileUpload } from "@/components/file-upload"
import { BatchPreview } from "@/components/batch-preview"
import { SuccessState } from "@/components/success-state"
import { Button } from "@/components/ui/button"
import { Loader2, ArrowLeft } from "lucide-react"
import { arealisApi, Transaction } from "@/lib/api"
import { parseCSV, ParsedTransaction } from "@/lib/csv-parser"

type BatchState = "initial" | "file-selected" | "submitting" | "success"

interface CSVData {
  headers: string[]
  rows: string[][]
}

interface BatchUploadViewProps {
  onBack: () => void
}

export function BatchUploadView({ onBack }: BatchUploadViewProps) {
  const [state, setState] = useState<BatchState>("initial")
  const [file, setFile] = useState<File | null>(null)
  const [csvData, setCsvData] = useState<CSVData | null>(null)
  const [batchId, setBatchId] = useState<string>("")
  const [error, setError] = useState<string>("")
  const [transactions, setTransactions] = useState<ParsedTransaction[]>([])

  const handleFileSelect = useCallback((selectedFile: File, data: CSVData) => {
    console.log('📁 File selected:', selectedFile.name, 'Size:', selectedFile.size)
    console.log('📊 CSV data:', { headers: data.headers, rows: data.rows.length })
    setFile(selectedFile)
    setCsvData(data)
    setError("")
    
    // Parse CSV content to transactions
    try {
      // Reconstruct the full CSV text including headers
      const csvText = [data.headers.join(','), ...data.rows.map(row => row.join(','))].join('\n')
      console.log('📄 Reconstructed CSV length:', csvText.length)
      console.log('📄 Reconstructed CSV preview:', csvText.substring(0, 300) + '...')
      
      console.log('🔄 Starting CSV parsing...')
      const parsedTransactions = parseCSV(csvText)
      console.log('✅ CSV parsing successful!')
      console.log('📊 Parsed transactions count:', parsedTransactions.length)
      console.log('📊 Parsed transactions:', parsedTransactions.map(t => ({ id: t.transaction_id, type: t.payment_type })))
      
      // CRITICAL: Ensure we have transactions from CSV
      if (parsedTransactions.length === 0) {
        throw new Error('CSV file contains no valid transactions. Please check the file format.')
      }
      
      console.log('✅ CSV file successfully parsed with', parsedTransactions.length, 'transactions')
      setTransactions(parsedTransactions)
      setState("file-selected")
    } catch (err) {
      console.error('❌ CSV parsing error:', err)
      setError(err instanceof Error ? err.message : 'Failed to parse CSV file')
      setState("initial")
    }
  }, [])

  const handleFileRemove = useCallback(() => {
    setFile(null)
    setCsvData(null)
    setTransactions([])
    setError("")
    setState("initial")
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!file) return

    setState("submitting")
    setError("")

    try {
      // Validate API key first
      const isValidKey = await arealisApi.validateApiKey()
      if (!isValidKey) {
        throw new Error('Invalid API key. Please check your .env.local file.')
      }

      // Debug: Log current state
      console.log('🚀 Starting batch submission...')
      console.log('📊 Current transactions count:', transactions.length)
      console.log('📊 Current transactions:', transactions.map(t => ({ id: t.transaction_id, type: t.payment_type })))
      console.log('📄 CSV data available:', !!csvData)
      
      // STRICT: Only process uploaded CSV data - NO MOCK FALLBACK
      if (transactions.length === 0) {
        throw new Error('No transactions found in the uploaded CSV file. Please check the file format and ensure it contains valid transaction data.')
      }
      
      const transactionsToProcess = transactions
      console.log('✅ Processing', transactionsToProcess.length, 'transactions from uploaded CSV file')

      // Save payment file first - send the CSV data, not parsed transactions
      console.log('💾 Saving payment file...', { filename: file.name, csvDataLength: csvData ? csvData.rows.length : 0 })
      const fileResult = await arealisApi.savePaymentFile(file.name, csvData || '')
      if (!fileResult.success) {
        throw new Error(fileResult.message)
      }
      console.log('✅ Payment file saved successfully')

      // Process transactions through ACC agent
      console.log('🔄 Processing transactions through ACC agent...', { count: transactionsToProcess.length })
      const batchResult = await arealisApi.processBatch(transactionsToProcess as Transaction[])
      if (!batchResult.success) {
        throw new Error(batchResult.message)
      }
      console.log('✅ Batch processing completed successfully')

      setBatchId(batchResult.batch_id)
      setState("success")
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process batch')
      setState("file-selected")
    }
  }, [file, transactions])

  const handleReset = useCallback(() => {
    setFile(null)
    setCsvData(null)
    setTransactions([])
    setBatchId("")
    setError("")
    setState("initial")
  }, [])

  if (state === "success") {
    return (
      <div className="max-w-2xl mx-auto">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Selection
        </Button>
        <Card className="shadow-lg">
          <CardContent className="p-8">
            <SuccessState batchId={batchId} onReset={handleReset} />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Selection
      </Button>

      <Card className="shadow-lg">
        <CardHeader className="pb-6">
          <CardTitle className="text-2xl font-semibold text-balance">Create a New Payout Batch</CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <FileUpload file={file} onFileSelect={handleFileSelect} onFileRemove={handleFileRemove} />

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          {csvData && state === "file-selected" && <BatchPreview data={csvData} />}

          {/* Debug info */}
          {state === "file-selected" && (
            <div className="p-2 bg-blue-50 border border-blue-200 rounded text-sm">
              <p>Debug: Transactions parsed: {transactions.length}</p>
              <p>File: {file?.name}</p>
            </div>
          )}

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
    </div>
  )
}

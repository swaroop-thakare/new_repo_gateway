"use client"

import { useState, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { useBatchUpload } from "@/hooks/use-api"

interface UploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error'
  message: string
  progress: number
  batchId?: string
  workflowId?: string
}

export function CSVUpload() {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    status: 'idle',
    message: 'Ready to upload CSV file',
    progress: 0
  })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [tenantId, setTenantId] = useState('DEMO')
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const { uploadBatch, uploading, error } = useBatchUpload()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === 'text/csv') {
      setSelectedFile(file)
      setUploadStatus({
        status: 'idle',
        message: `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`,
        progress: 0
      })
    } else {
      toast.error('Please select a valid CSV file')
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a CSV file first')
      return
    }

    try {
      setUploadStatus({
        status: 'uploading',
        message: 'Uploading CSV file...',
        progress: 20
      })

      // Read CSV content
      const csvContent = await selectedFile.text()
      const lines = csvContent.split('\n').filter(line => line.trim())
      const headers = lines[0].split(',')
      const dataLines = lines.slice(1)

      // Parse CSV data
      const transactions = dataLines.map((line, index) => {
        const values = line.split(',')
        const transaction: any = {}
        headers.forEach((header, i) => {
          transaction[header.trim()] = values[i]?.trim() || ''
        })
        return {
          transactionId: transaction.transactionId || `TXN-${index + 1}`,
          date: transaction.date || new Date().toISOString().split('T')[0],
          beneficiary: transaction.beneficiary || `User ${index + 1}`,
          amount: parseFloat(transaction.amount) || 0,
          currency: transaction.currency || 'INR',
          purpose: transaction.purpose || 'VENDOR_PAYMENT',
          transactionType: transaction.transactionType || 'NEFT',
          creditScore: parseInt(transaction.creditScore) || 700,
          reference: transaction.reference || `REF-${index + 1}`
        }
      })

      setUploadStatus({
        status: 'processing',
        message: `Processing ${transactions.length} transactions...`,
        progress: 50
      })

      // Create batch data
      const batchData = {
        batch_id: `B-${tenantId}-${new Date().toISOString().replace(/[-:]/g, '').slice(0, 14)}`,
        tenant_id: tenantId,
        source: 'CSV_UPLOAD',
        upload_ts: new Date().toISOString(),
        transactions: transactions
      }

      // Upload batch
      const result = await uploadBatch(batchData)
      
      setUploadStatus({
        status: 'completed',
        message: `Successfully processed ${transactions.length} transactions`,
        progress: 100,
        batchId: result.batch_id,
        workflowId: result.workflow_id
      })

      toast.success(`Batch ${result.batch_id} uploaded successfully!`)
      
      // Reset form after successful upload
      setTimeout(() => {
        setSelectedFile(null)
        setUploadStatus({
          status: 'idle',
          message: 'Ready to upload CSV file',
          progress: 0
        })
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }, 3000)

    } catch (err) {
      setUploadStatus({
        status: 'error',
        message: `Upload failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
        progress: 0
      })
      toast.error('Upload failed. Please try again.')
    }
  }

  const getStatusIcon = () => {
    switch (uploadStatus.status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <FileText className="h-4 w-4 text-slate-400" />
    }
  }

  const getStatusColor = () => {
    switch (uploadStatus.status) {
      case 'completed':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'error':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'uploading':
      case 'processing':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      default:
        return 'bg-slate-500/10 text-slate-500 border-slate-500/20'
    }
  }

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Upload className="h-5 w-5" />
          CSV File Upload
        </CardTitle>
        <p className="text-sm text-slate-400">
          Upload a CSV file to process transactions and update the dashboard
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Tenant ID Input */}
        <div className="space-y-2">
          <Label htmlFor="tenant-id" className="text-slate-200">Tenant ID</Label>
          <Input
            id="tenant-id"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            className="bg-slate-800 border-slate-700 text-white"
            placeholder="Enter tenant ID"
          />
        </div>

        {/* File Selection */}
        <div className="space-y-2">
          <Label htmlFor="csv-file" className="text-slate-200">CSV File</Label>
          <Input
            ref={fileInputRef}
            id="csv-file"
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            className="bg-slate-800 border-slate-700 text-white file:bg-slate-700 file:text-white file:border-0 file:rounded file:px-3 file:py-1"
          />
        </div>

        {/* Upload Status */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-sm text-slate-200">{uploadStatus.message}</span>
          </div>
          
          {uploadStatus.progress > 0 && (
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadStatus.progress}%` }}
              />
            </div>
          )}

          {uploadStatus.batchId && (
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={getStatusColor()}>
                Batch: {uploadStatus.batchId}
              </Badge>
              {uploadStatus.workflowId && (
                <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20">
                  Workflow: {uploadStatus.workflowId.slice(-8)}
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Upload Button */}
        <Button 
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className="w-full bg-blue-600 hover:bg-blue-700"
        >
          {uploading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Processing...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Upload CSV
            </>
          )}
        </Button>

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-slate-500 space-y-1">
          <p><strong>CSV Format:</strong> transactionId,date,beneficiary,amount,currency,purpose,transactionType,creditScore,reference</p>
          <p><strong>Example:</strong> TXN-001,2025-10-04,John Doe,50000,INR,VENDOR_PAYMENT,NEFT,750,UTR123456</p>
        </div>
      </CardContent>
    </Card>
  )
}

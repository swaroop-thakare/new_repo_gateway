"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Cloud, X, FileText, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface CSVData {
  headers: string[]
  rows: string[][]
}

interface FileUploadProps {
  file: File | null
  onFileSelect: (file: File, data: CSVData) => void
  onFileRemove: () => void
}

export function FileUpload({ file, onFileSelect, onFileRemove }: FileUploadProps) {
  const [error, setError] = useState<string>("")

  const parseCSV = useCallback((text: string): CSVData => {
    console.log('📄 FileUpload parseCSV - Raw text length:', text.length)
    const lines = text.trim().split("\n").filter(line => line.trim())
    console.log('📄 FileUpload parseCSV - Lines count:', lines.length)
    
    if (lines.length < 2) {
      throw new Error('CSV file must have at least a header and one data row')
    }
    
    // Handle potential Byte Order Mark (BOM) character
    let headerLine = lines[0]
    if (headerLine.charCodeAt(0) === 0xFEFF) {
      headerLine = headerLine.substring(1)
    }
    
    const headers = headerLine.split(",").map((h) => h.trim().replace(/"/g, ""))
    console.log('📄 FileUpload parseCSV - Headers:', headers)
    
    const rows = lines.slice(1).map((line, index) => {
      const cells = line.split(",").map((cell) => cell.trim().replace(/"/g, ""))
      console.log(`📄 FileUpload parseCSV - Row ${index + 1}:`, cells.length, 'cells')
      return cells
    })
    
    console.log('📄 FileUpload parseCSV - Total rows:', rows.length)
    return { headers, rows }
  }, [])

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const selectedFile = acceptedFiles[0]
      if (!selectedFile) return

      if (selectedFile.type !== "text/csv" && !selectedFile.name.endsWith(".csv")) {
        setError("Please select a CSV file")
        return
      }

      if (selectedFile.size > 10 * 1024 * 1024) {
        // 10MB limit
        setError("File size must be less than 10MB")
        return
      }

      setError("")

      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string
          const csvData = parseCSV(text)

          if (csvData.rows.length === 0) {
            setError("CSV file appears to be empty")
            return
          }

          onFileSelect(selectedFile, csvData)
        } catch (err) {
          setError("Failed to parse CSV file")
        }
      }
      reader.readAsText(selectedFile)
    },
    [onFileSelect, parseCSV],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
    },
    multiple: false,
  })

  const downloadTemplate = () => {
    const csvContent = `payment_type,transaction_id,sender_name,sender_account_number,sender_ifsc_code,sender_bank_name,receiver_name,receiver_account_number,receiver_ifsc_code,receiver_bank_name,amount,currency,method,purpose,schedule_datetime,city,latitude,longitude,employee_id,department,payment_frequency,invoice_number,invoice_date,gst_number,pan_number,vendor_code,loan_account_number,loan_type,sanction_date,interest_rate,tenure_months,borrower_verification_status
payroll,TXN001,ABC Corp,1234567890,HDFC0001234,HDFC Bank,John Doe,9876543210,SBIN0001234,State Bank of India,50000,INR,NEFT,Salary Payment,2025-10-02T10:00:00Z,Mumbai,19.076,72.8777,EMP001,IT,Monthly,,,,,ABCDE1234A,,,,,,,,
vendor_payment,TXN002,XYZ Ltd,2345678901,ICIC0001234,ICICI Bank,Jane Smith,8765432109,HDFC0005678,HDFC Bank,75000,INR,RTGS,Vendor Payment,2025-10-02T11:00:00Z,Delhi,28.6139,77.2090,,,,,INV001,2025-10-01,29ABCDE1234F1Z5,VENDOR001,,,,,,,
loan_disbursement,TXN003,Loan Bank,3456789012,SBIN0005678,State Bank of India,Bob Wilson,7654321098,PNB0001234,Punjab National Bank,100000,INR,NEFT,Loan Disbursement,2025-10-02T12:00:00Z,Bangalore,12.9716,77.5946,,,,,,,,LOAN001,Personal Loan,2025-10-01,12.5,24,APPROVED`
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "arealis_payout_template.csv"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (file) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-accent/20 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-accent" />
            </div>
            <div>
              <p className="font-medium text-foreground">{file.name}</p>
              <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onFileRemove}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-muted/30",
          error && "border-destructive bg-destructive/5",
        )}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center">
            <Cloud className="w-8 h-8 text-muted-foreground" />
          </div>

          <div className="space-y-2">
            <p className="text-lg font-medium text-foreground">
              {isDragActive ? "Drop your CSV file here" : "Drag & drop your CSV file here, or click to browse"}
            </p>
            <p className="text-sm text-muted-foreground">Maximum file size: 10MB</p>
          </div>

          {error && <p className="text-sm text-destructive font-medium">{error}</p>}
        </div>
      </div>

      <div className="flex justify-center">
        <Button
          variant="link"
          onClick={downloadTemplate}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          <Download className="w-4 h-4 mr-2" />
          Download CSV Template
        </Button>
      </div>
    </div>
  )
}

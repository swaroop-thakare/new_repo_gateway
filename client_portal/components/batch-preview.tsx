"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface CSVData {
  headers: string[]
  rows: string[][]
}

interface BatchPreviewProps {
  data: CSVData
}

export function BatchPreview({ data }: BatchPreviewProps) {
  const previewRows = data.rows.slice(0, 5)
  const totalRows = data.rows.length
  const totalAmount = data.rows.reduce((sum, row) => {
    const amountIndex = data.headers.findIndex((h) => h.toLowerCase().includes("amount"))
    if (amountIndex !== -1) {
      const amount = Number.parseFloat(row[amountIndex]?.replace(/[^\d.-]/g, "") || "0")
      return sum + (isNaN(amount) ? 0 : amount)
    }
    return sum
  }, 0)

  return (
    <Card className="border-accent/20">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Batch Preview</CardTitle>
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="font-medium">
              {totalRows} transactions
            </Badge>
            <Badge variant="outline" className="font-medium">
              ₹{totalAmount.toLocaleString("en-IN")}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="rounded-lg border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                {data.headers.map((header, index) => (
                  <TableHead key={index} className="font-semibold text-foreground">
                    {header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {previewRows.map((row, rowIndex) => (
                <TableRow key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <TableCell key={cellIndex} className="font-medium">
                      {data.headers[cellIndex]?.toLowerCase().includes("amount")
                        ? `₹${Number.parseFloat(cell?.replace(/[^\d.-]/g, "") || "0").toLocaleString("en-IN")}`
                        : cell}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {totalRows > 5 && (
          <p className="text-sm text-muted-foreground mt-3 text-center">Showing first 5 of {totalRows} transactions</p>
        )}
      </CardContent>
    </Card>
  )
}

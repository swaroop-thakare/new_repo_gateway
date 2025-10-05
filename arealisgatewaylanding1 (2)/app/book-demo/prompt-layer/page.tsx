"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { 
  MessageSquare, 
  Send, 
  Copy, 
  ExternalLink, 
  Clock, 
  User, 
  Calendar,
  CheckCircle,
  AlertCircle,
  FileText,
  Link as LinkIcon
} from "lucide-react"
import { PageHeader } from "@/components/demo/page-header"
import { useTransactions } from "@/hooks/use-api"

interface QueryResponse {
  id: string
  query: string
  timestamp: string
  line_id: string
  batch_id: string
  response: {
    failureReason: string
    detailedAnalysis: string
    recommendedActions: Array<{
      priority: number
      action: string
      timeline: string
      responsibility: string
      link?: string
    }>
    additionalNotes: string
    evidenceLinks: Array<{
      name: string
      url: string
    }>
    confidence: number
  }
}

interface QueryHistory {
  id: string
  query: string
  timestamp: string
  line_id: string
  batch_id: string
}

export default function PromptLayerPage() {
  const [query, setQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<QueryResponse | null>(null)
  const [queryHistory, setQueryHistory] = useState<QueryHistory[]>([])
  const [selectedLineId, setSelectedLineId] = useState("L-2")
  const [selectedBatchId, setSelectedBatchId] = useState("B-2025-001")
  const { transactions } = useTransactions()

  // Load query history on component mount
  useEffect(() => {
    loadQueryHistory()
  }, [])

  const loadQueryHistory = async () => {
    try {
      // Mock query history - in production, fetch from /api/prompt/history
      const mockHistory = [
        {
          id: "1",
          query: "Why did line L-1 fail?",
          timestamp: "2025-01-05T10:00:00Z",
          line_id: "L-1",
          batch_id: "B-2025-001"
        },
        {
          id: "2", 
          query: "What is the status of transaction TXN-001?",
          timestamp: "2025-01-05T09:30:00Z",
          line_id: "L-1",
          batch_id: "B-2025-001"
        },
        {
          id: "3",
          query: "Show me all failed transactions in batch B-2025-001",
          timestamp: "2025-01-05T09:00:00Z",
          line_id: "L-1",
          batch_id: "B-2025-001"
        }
      ]
      setQueryHistory(mockHistory)
    } catch (error) {
      console.error("Failed to load query history:", error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch('/api/prompt/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          line_id: selectedLineId,
          batch_id: selectedBatchId,
          query: query
        })
      })

      if (response.ok) {
        const data = await response.json()
        setResponse(data)
        // Add to query history
        setQueryHistory(prev => [data, ...prev])
      } else {
        console.error('Failed to get response')
      }
    } catch (error) {
      console.error('Error submitting query:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  const openEvidenceLink = (url: string) => {
    window.open(url, '_blank')
  }

  const viewHistoryResponse = (historyItem: QueryHistory) => {
    // In production, this would fetch the full response
    console.log('Viewing history response:', historyItem)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI Assistant"
        title="Arealis Prompt Layer"
        description="Ask xAI about transactions, failures, and system behavior"
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Query Interface */}
        <div className="lg:col-span-3 space-y-6">
          {/* Query Input */}
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Ask xAI
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Line ID</label>
                    <Input
                      value={selectedLineId}
                      onChange={(e) => setSelectedLineId(e.target.value)}
                      placeholder="L-2"
                      className="bg-background/50"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">Batch ID</label>
                    <Input
                      value={selectedBatchId}
                      onChange={(e) => setSelectedBatchId(e.target.value)}
                      placeholder="B-2025-001"
                      className="bg-background/50"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Query</label>
                  <Textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about a transaction (e.g., Why did line L-2 fail?)"
                    className="min-h-[100px] bg-background/50"
                  />
                </div>
                <Button 
                  type="submit" 
                  disabled={isLoading || !query.trim()}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4 mr-2" />
                      Ask xAI
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Response Panel */}
          {response && (
            <Card className="glass-card glass-primary">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    AI Response
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(JSON.stringify(response, null, 2))}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Response
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Failure Reason */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Failure Reason</h3>
                  <p className="text-muted-foreground bg-muted/50 p-3 rounded-lg">
                    {response.response.failureReason}
                  </p>
                </div>

                {/* Detailed Analysis */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Detailed Analysis</h3>
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm text-muted-foreground">
                      {response.response.detailedAnalysis}
                    </pre>
                  </div>
                </div>

                {/* Recommended Actions */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Recommended Actions</h3>
                  <div className="space-y-3">
                    {response.response.recommendedActions.map((action, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                        <Badge variant="outline" className="mt-1">
                          {action.priority}
                        </Badge>
                        <div className="flex-1">
                          <p className="font-medium">{action.action}</p>
                          <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {action.timeline}
                            </span>
                            <span className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {action.responsibility}
                            </span>
                            {action.link && (
                              <Button
                                variant="link"
                                size="sm"
                                className="h-auto p-0"
                                onClick={() => window.open(action.link, '_blank')}
                              >
                                <LinkIcon className="h-3 w-3 mr-1" />
                                View
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional Notes */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Additional Notes</h3>
                  <p className="text-muted-foreground bg-muted/50 p-3 rounded-lg">
                    {response.response.additionalNotes}
                  </p>
                </div>

                {/* Evidence Links */}
                <div>
                  <h3 className="font-semibold text-lg mb-2">Evidence Links</h3>
                  <div className="space-y-2">
                    {response.response.evidenceLinks.map((link, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-muted/30 rounded-lg">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          <span className="text-sm">{link.name}</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEvidenceLink(link.url)}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Confidence Score */}
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Confidence:</span>
                  <Badge 
                    variant={response.response.confidence >= 90 ? "default" : "secondary"}
                    className={response.response.confidence >= 90 ? "bg-green-500" : "bg-yellow-500"}
                  >
                    {response.response.confidence}%
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Query History Sidebar */}
        <div className="lg:col-span-1">
          <Card className="glass-card glass-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Query History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-3">
                  {queryHistory.map((item) => (
                    <div key={item.id} className="p-3 bg-muted/30 rounded-lg">
                      <p className="text-sm font-medium mb-1">{item.query}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                        <Calendar className="h-3 w-3" />
                        {new Date(item.timestamp).toLocaleString()}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                        <span>Line: {item.line_id}</span>
                        <span>Batch: {item.batch_id}</span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => viewHistoryResponse(item)}
                      >
                        View Response
                      </Button>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

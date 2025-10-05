"use client"

import { useState } from "react"
import { Send, Clock, Calendar, FileText, Brain } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

export default function ExplainabilityPage() {
  const [lineId, setLineId] = useState("L-2")
  const [batchId, setBatchId] = useState("B-2025-001")
  const [query, setQuery] = useState("")

  const handleAskXAI = () => {
    if (query.trim()) {
      alert(`🤖 Asking xAI about:\n\nLine ID: ${lineId}\nBatch ID: ${batchId}\nQuery: ${query}\n\nThis would typically send the query to the xAI system for analysis.`)
    }
  }

  const handleViewResponse = (queryText: string) => {
    alert(`📋 Viewing response for:\n\n"${queryText}"\n\nThis would typically show the AI's detailed analysis and explanation.`)
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-white">
      {/* AI Assistant Banner */}
      <div className="bg-gradient-to-r from-blue-900/30 to-blue-800/30 border-b border-blue-800/20">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-blue-600/20 px-3 py-1 rounded-full">
              <span className="text-xs font-medium text-blue-300">AI ASSISTANT</span>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Arealis Prompt Layer</h1>
          <p className="text-lg text-gray-300">Ask xAI about transactions, failures, and system behavior</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content - Ask xAI Section */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <FileText className="w-5 h-5" />
                  Ask xAI
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Line ID</label>
                    <Input
                      value={lineId}
                      onChange={(e) => setLineId(e.target.value)}
                      className="bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500"
                      placeholder="Enter Line ID"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Batch ID</label>
                    <Input
                      value={batchId}
                      onChange={(e) => setBatchId(e.target.value)}
                      className="bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500"
                      placeholder="Enter Batch ID"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Query</label>
                  <Textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about a transaction (e.g., Why did line L-2 fail?)"
                    className="bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500 min-h-[120px]"
                  />
                </div>
                
                <Button 
                  onClick={handleAskXAI}
                  className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Ask xAI
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar - Query History */}
          <div className="lg:col-span-1">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Clock className="w-5 h-5" />
                  Query History
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Query History Items */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                  <p className="text-white text-sm mb-2">"Why did line L-1 fail?"</p>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                    <Calendar className="w-3 h-3" />
                    <span>05/01/2025, 15:30:00</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-3">Line: L-1 Batch: B-2025-001</p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleViewResponse("Why did line L-1 fail?")}
                    className="text-xs"
                  >
                    View Response
                  </Button>
                </div>

                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                  <p className="text-white text-sm mb-2">"What is the status of transaction TXN-001?"</p>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                    <Calendar className="w-3 h-3" />
                    <span>05/01/2025, 15:00:00</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-3">Line: L-1 Batch: B-2025-001</p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleViewResponse("What is the status of transaction TXN-001?")}
                    className="text-xs"
                  >
                    View Response
                  </Button>
                </div>

                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                  <p className="text-white text-sm mb-2">"Show me all failed transactions in batch B-2025-001"</p>
                  <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
                    <Calendar className="w-3 h-3" />
                    <span>05/01/2025, 14:30:00</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-3">Line: L-1 Batch: B-2025-001</p>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleViewResponse("Show me all failed transactions in batch B-2025-001")}
                    className="text-xs"
                  >
                    View Response
                  </Button>
                </div>

                {/* Floating Brain Icon */}
                <div className="fixed bottom-6 right-6 z-50">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform cursor-pointer">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

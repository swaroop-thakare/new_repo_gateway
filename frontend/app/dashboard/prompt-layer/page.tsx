"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Sparkles, PanelRightOpen } from "lucide-react"
import { AgentDrawer } from "@/components/demo/agent-drawer"

const quickQuestions = [
  "Why was transaction ID 12345678 flagged?",
  "What is the current model accuracy?",
  "Summarize the risk profile for Loan ID L-789.",
  "Show me recent compliance violations.",
  "What's the average processing time today?",
]

export default function PromptLayerPage() {
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI Explainability Assistant. I can help you understand decisions made by our loan disbursement system, analyze risk profiles, and provide insights into model performance. How can I assist you today?",
    },
  ])
  const [input, setInput] = useState("")
  const [drawerOpen, setDrawerOpen] = useState(false)

  const handleSend = () => {
    if (!input.trim()) return
    setMessages([...messages, { role: "user", content: input }])
    setInput("")
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I've analyzed your query. Based on the evidence graph and policy versions, here's what I found...",
        },
      ])
    }, 1000)
  }

  const handleQuickQuestion = (question: string) => {
    setMessages([...messages, { role: "user", content: question }])
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Analyzing: "${question}". Let me retrieve the relevant information from our system...`,
        },
      ])
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-emerald-500" />
            Prompt Layer (AI Explainability Assistant)
          </h1>
          <p className="text-slate-400 mt-1">Ask questions about transactions, models, and system decisions</p>
        </div>
        <Button
          onClick={() => setDrawerOpen(true)}
          className="bg-blue-600 text-white hover:bg-blue-700"
          aria-label="Open Agent Console"
        >
          <PanelRightOpen className="mr-2 h-4 w-4" />
          Open Agent Console (Why?)
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Chat Interface */}
        <Card className="bg-slate-900 border-slate-800 lg:col-span-2">
          <CardContent className="p-0">
            <div className="flex flex-col h-[600px]">
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message, index) => (
                  <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === "user" ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-200"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="border-t border-slate-800 p-4">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSend()}
                    placeholder="Ask a question about transactions, models, or decisions..."
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                  <Button onClick={handleSend} className="bg-emerald-600 hover:bg-emerald-700" aria-label="Send">
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Questions Sidebar */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white text-base">Quick Questions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {quickQuestions.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                className="w-full justify-start text-left h-auto py-3 px-4 bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700 hover:text-white"
                onClick={() => handleQuickQuestion(question)}
              >
                <span className="text-sm">{question}</span>
              </Button>
            ))}
          </CardContent>
        </Card>
      </div>

      <AgentDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} defaultTab="why" />
    </div>
  )
}

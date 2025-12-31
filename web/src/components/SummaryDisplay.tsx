'use client'

import { Copy, CheckCircle } from 'lucide-react'
import { useState } from 'react'

interface SummaryDisplayProps {
  summary: any
}

export default function SummaryDisplay({ summary }: SummaryDisplayProps) {
  const [copied, setCopied] = useState(false)

  // Handle both nested summary object or direct summary fields
  const summaryData = summary.summary || summary;

  const handleCopy = () => {
    const text = formatSummaryAsText(summaryData)
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const formatSummaryAsText = (data: any) => {
    return `# Content Summary

## Executive Summary
${data.executive_summary || 'N/A'}

## Key Topics
${data.key_topics?.map((topic: string) => `- ${topic}`).join('\n') || 'N/A'}

## Main Takeaways
${data.main_takeaways?.map((takeaway: string) => `- ${takeaway}`).join('\n') || 'N/A'}

## Action Items
${data.action_items?.map((item: string) => `- ${item}`).join('\n') || 'None'}

---
Generated on: ${new Date().toLocaleString()}
`
  }

  return (
    <div className="mt-8 space-y-6">
      {/* Action Buttons */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all shadow-md"
        >
          {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          {copied ? 'Copied!' : 'Copy Summary'}
        </button>
      </div>

      {/* Summary Content */}
      <div className="bg-white rounded-xl shadow-lg p-8 space-y-8">
        {/* Executive Summary */}
        {summaryData.executive_summary && (
          <section>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
              Executive Summary
            </h2>
            <p className="text-gray-700 text-lg leading-relaxed">
              {summaryData.executive_summary}
            </p>
          </section>
        )}

        {/* Key Topics */}
        {summaryData.key_topics && summaryData.key_topics.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
              Key Topics
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {summaryData.key_topics.map((topic: string, idx: number) => (
                <li key={idx}>{topic}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Main Takeaways */}
        {summaryData.main_takeaways && summaryData.main_takeaways.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
              Main Takeaways
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {summaryData.main_takeaways.map((takeaway: string, idx: number) => (
                <li key={idx}>{takeaway}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Action Items */}
        {summaryData.action_items && summaryData.action_items.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
              Action Items
            </h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {summaryData.action_items.map((item: string, idx: number) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}

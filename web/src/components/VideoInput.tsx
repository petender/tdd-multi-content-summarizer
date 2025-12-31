'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'

interface VideoInputProps {
  onSubmit: (videoUrl: string, userId: string) => void
  loading: boolean
}

export default function VideoInput({ onSubmit, loading }: VideoInputProps) {
  const [videoUrl, setVideoUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (videoUrl.trim()) {
      onSubmit(videoUrl, 'anonymous')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="videoUrl" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          YouTube Video URL
        </label>
        <input
          type="text"
          id="videoUrl"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          required
          disabled={loading}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
      >
        <Send className="w-5 h-5" />
        {loading ? 'Processing...' : 'Summarize Video'}
      </button>
    </form>
  )
}

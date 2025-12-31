import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Video Summarizer',
  description: 'Summarize YouTube videos with Azure OpenAI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script src="/config.js"></script>
      </head>
      <body>{children}</body>
    </html>
  )
}

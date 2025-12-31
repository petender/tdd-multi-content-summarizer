'use client';

import Link from 'next/link';
import Navigation from '../components/Navigation';

export default function Home() {
  const contentTypes = [
    {
      href: '/article',
      icon: '📄',
      title: 'Web Articles',
      description: 'Summarize blog posts, news articles, and web pages',
      color: 'from-blue-500 to-cyan-500',
      features: ['Works in Azure', 'Any public URL', 'Fast extraction']
    },
    {
      href: '/text',
      icon: '📝',
      title: 'Direct Text',
      description: 'Paste any text content for instant summarization',
      color: 'from-purple-500 to-pink-500',
      features: ['Paste & go', 'No limits', 'Manual transcripts']
    },
    {
      href: '/pdf',
      icon: '📋',
      title: 'PDF Documents',
      description: 'Upload PDF files to extract and summarize content',
      color: 'from-green-500 to-teal-500',
      features: ['Upload PDFs', 'Multi-page', 'Document analysis']
    },
    {
      href: '/youtube',
      icon: '🎥',
      title: 'YouTube Videos',
      description: 'Get AI summaries from YouTube video transcripts',
      color: 'from-red-500 to-orange-500',
      badge: 'Local Only',
      features: ['Video transcripts', 'Local use', 'Requires captions']
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <Navigation />
      
      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            ✨ AI Content Summarizer
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-6">
            Powered by Azure OpenAI & GPT-4
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
              Multi-language support
            </span>
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
              4 content sources
            </span>
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
              Cloud-ready
            </span>
          </div>
        </div>

        {/* Content Type Cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-6xl mx-auto">
          {contentTypes.map((type) => (
            <Link
              key={type.href}
              href={type.href}
              className="group block bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden transform hover:-translate-y-1"
            >
              <div className={`h-2 bg-gradient-to-r ${type.color}`} />
              <div className="p-8">
                <div className="flex items-start justify-between mb-4">
                  <span className="text-5xl">{type.icon}</span>
                  {type.badge && (
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full">
                      {type.badge}
                    </span>
                  )}
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                  {type.title}
                </h2>
                
                <p className="text-gray-600 mb-4">
                  {type.description}
                </p>
                
                <ul className="space-y-2">
                  {type.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-sm text-gray-500">
                      <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <div className="mt-6 flex items-center text-blue-600 font-semibold group-hover:translate-x-2 transition-transform">
                  Get started
                  <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Tech Stack */}
        <div className="mt-16 text-center">
          <p className="text-sm font-semibold text-gray-500 mb-4">POWERED BY</p>
          <div className="flex flex-wrap justify-center gap-6 items-center text-gray-400">
            <span className="font-semibold">Azure OpenAI</span>
            <span>•</span>
            <span className="font-semibold">GPT-4</span>
            <span>•</span>
            <span className="font-semibold">Azure Functions</span>
            <span>•</span>
            <span className="font-semibold">Cosmos DB</span>
            <span>•</span>
            <span className="font-semibold">Next.js</span>
          </div>
        </div>
      </main>
    </div>
  );
}

'use client';

import { useState } from 'react';
import Navigation from '../../components/Navigation';
import LanguageSelector from '../../components/LanguageSelector';
import SummaryDisplay from '../../components/SummaryDisplay';

export default function TextPage() {
  const [textContent, setTextContent] = useState('');
  const [language, setLanguage] = useState('English');
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [error, setError] = useState('');
  const [textInfo, setTextInfo] = useState<any>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7071/api';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSummary(null);
    setTextInfo(null);

    try {
      const response = await fetch(`${API_BASE}/summarize-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: textContent,
          userId: 'demo-user',
          language
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to summarize text');
      }

      const data = await response.json();
      setSummary(data.summary);
      setTextInfo({
        word_count: data.word_count,
        char_count: data.char_count,
        language: data.language
      });
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const wordCount = textContent.trim().split(/\s+/).filter(w => w.length > 0).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              📝 Text Summarizer
            </h1>
            <p className="text-gray-600">
              Paste any text content to get an AI-powered summary in your preferred language
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-2">
                Your Text Content
              </label>
              <textarea
                id="text"
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Paste your text here... (minimum 50 characters)"
                rows={12}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                required
                minLength={50}
              />
              <p className="mt-1 text-sm text-gray-500">
                {wordCount} words • {textContent.length} characters
              </p>
            </div>

            <LanguageSelector
              selectedLanguage={language}
              onLanguageChange={setLanguage}
            />

            <button
              type="submit"
              disabled={loading || textContent.length < 50}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Analyzing Text...
                </span>
              ) : (
                '✨ Summarize Text'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          {textInfo && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                📊 Analyzed {textInfo.word_count} words ({textInfo.char_count} characters) • Summary in {textInfo.language}
              </p>
            </div>
          )}

          {summary && <SummaryDisplay summary={summary} />}
        </div>
      </main>
    </div>
  );
}

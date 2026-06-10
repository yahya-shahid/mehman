import React from 'react';
import { Info, AlertTriangle, CheckCircle, Shield } from 'lucide-react';

export default function AboutScreen() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <div className="w-12 h-12 rounded-full bg-[#14a44d] flex items-center justify-center">
          <Info size={24} className="text-white" />
        </div>
        <div>
          <h1 className="text-white text-3xl">About Mehman</h1>
          <p className="text-[#9ca3af]">Your AI travel companion for Pakistan</p>
        </div>
      </div>

      {/* Introduction */}
      <div className="bg-[#232730] rounded-xl p-6 mb-6">
        <p className="text-[#d1d5db] leading-relaxed mb-4">
          Mehman ("guest" in Urdu) is an AI-powered assistant designed to help international visitors navigate Pakistan with confidence. Built on Grok (and Llama 3.3) and trained on real travel conversations, local customs, and practical insights, Mehman provides contextual advice for your journey through Pakistan.
        </p>
        <p className="text-[#d1d5db] leading-relaxed">
          Whether you need help with translations, directions, cultural etiquette, or local recommendations, Mehman is here to make your Pakistani adventure smoother and more enriching.
        </p>
      </div>

      {/* Important Warning */}
      <div className="bg-[#78350f] bg-opacity-20 border-2 border-[#fbbf24] rounded-xl p-5 mb-6 flex gap-4">
        <div className="flex-shrink-0">
          <AlertTriangle size={24} className="text-[#fbbf24]" />
        </div>
        <div>
          <h2 className="text-[#fbbf24] mb-2">Important: Verify Official Travel Advisories</h2>
          <p className="text-[#fef3c7] leading-relaxed">
            Always consult your government's official travel advisories and the Pakistani Embassy before traveling. Mehman provides general guidance but cannot replace official safety information, visa requirements, or current security updates. Check with trusted sources for the latest information.
          </p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* What Mehman is Good At */}
        <div className="bg-[#232730] rounded-xl p-6 border border-[#14a44d]">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle size={20} className="text-[#14a44d]" />
            <h2 className="text-white text-xl">What Mehman is Good At</h2>
          </div>
          <ul className="space-y-3">
            {[
              'Translating common phrases to polite Urdu',
              'Explaining local customs and etiquette',
              'Recommending authentic food and restaurants',
              'Navigating transportation options',
              'Understanding cultural contexts',
              'Suggesting tourist attractions and hidden gems',
              'Providing conversational travel tips'
            ].map((item, index) => (
              <li key={index} className="flex gap-3 text-[#d1d5db]">
                <span className="text-[#14a44d] mt-1">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Use Responsibly */}
        <div className="bg-[#232730] rounded-xl p-6 border border-[#fbbf24]">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={20} className="text-[#fbbf24]" />
            <h2 className="text-white text-xl">Use Responsibly</h2>
          </div>
          <ul className="space-y-3">
            {[
              'AI can make mistakes—verify critical information',
              'Respect local customs and traditions always',
              'Do not rely solely on AI for emergency situations',
              'Keep emergency contact numbers handy',
              'Be mindful of cultural and religious sensitivities',
              'Check official sources for visa and travel requirements',
              'Exercise common sense and personal judgment'
            ].map((item, index) => (
              <li key={index} className="flex gap-3 text-[#d1d5db]">
                <span className="text-[#fbbf24] mt-1">⚠</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Technical Info */}
      <div className="bg-[#232730] rounded-xl p-6">
        <h2 className="text-white text-xl mb-4">Technical Details</h2>
        <div className="space-y-3 text-[#d1d5db]">
          <div className="flex gap-3">
            <span className="text-[#14a44d]">AI Model:</span>
            <span>Grok and Llama 3.3</span>
          </div>
          <div className="flex gap-3">
            <span className="text-[#14a44d]">Version:</span>
            <span>Beta 2.0</span>
          </div>
          <div className="flex gap-3">
            <span className="text-[#14a44d]">Last Updated:</span>
            <span>June 2026</span>
          </div>
          <div className="flex gap-3">
            <span className="text-[#14a44d]">Focus Region:</span>
            <span>Pakistan (all provinces and territories)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

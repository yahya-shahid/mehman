import React, { useState } from 'react';
import { MessageSquare, Languages, Info } from 'lucide-react';
import ChatbotScreen from './components/ChatbotScreen';
import TranslatorScreen from './components/TranslatorScreen';
import AboutScreen from './components/AboutScreen';

type Screen = 'chatbot' | 'translator' | 'about';

export default function App() {
  const [activeScreen, setActiveScreen] = useState<Screen>('chatbot');

  return (
    <div className="flex h-screen bg-[#1a1d29]">
      {/* Sidebar */}
      <aside className="w-64 bg-[#232730] flex flex-col border-r border-[#2d3139]">
        {/* Logo */}
        <div className="p-6 border-b border-[#2d3139]">
          <h1 className="text-[#14a44d] text-2xl tracking-tight">Mehman</h1>
          <p className="text-[#9ca3af] text-sm mt-1">Navigate Pakistan with AI</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <button
            onClick={() => setActiveScreen('chatbot')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${
              activeScreen === 'chatbot'
                ? 'bg-[#2d3139] text-white border-l-3 border-l-[#14a44d]'
                : 'text-[#9ca3af] hover:bg-[#2d3139] hover:text-white'
            }`}
          >
            <MessageSquare size={20} />
            <span>Chatbot</span>
          </button>

          <button
            onClick={() => setActiveScreen('translator')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${
              activeScreen === 'translator'
                ? 'bg-[#2d3139] text-white border-l-3 border-l-[#14a44d]'
                : 'text-[#9ca3af] hover:bg-[#2d3139] hover:text-white'
            }`}
          >
            <Languages size={20} />
            <span>Translator</span>
          </button>

          <button
            onClick={() => setActiveScreen('about')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${
              activeScreen === 'about'
                ? 'bg-[#2d3139] text-white border-l-3 border-l-[#14a44d]'
                : 'text-[#9ca3af] hover:bg-[#2d3139] hover:text-white'
            }`}
          >
            <Info size={20} />
            <span>About & Safety</span>
          </button>
        </nav>

        {/* Footer Links */}
        <div className="p-4 border-t border-[#2d3139] space-y-3">
          <a
            href="https://console.groq.com/keys"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-sm text-[#9ca3af] hover:text-[#14a44d] transition-colors"
          >
            Get a Groq API key
          </a>
          <a
            href="https://github.com/yahya-shahid/mehman"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-sm text-[#9ca3af] hover:text-[#14a44d] transition-colors"
          >
            View the source code
          </a>
          <button className="w-full px-4 py-2 rounded-lg border border-[#2d3139] text-[#9ca3af] hover:border-[#14a44d] hover:text-[#14a44d] transition-all text-sm">
            Clear chat history
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto p-8">
          {activeScreen === 'chatbot' && <ChatbotScreen />}
          {activeScreen === 'translator' && <TranslatorScreen />}
          {activeScreen === 'about' && <AboutScreen />}
        </div>
      </main>
    </div>
  );
}

import React, { useState, useRef } from 'react';
import { Send, Bot, User, StopCircle } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function ChatbotScreen() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "**🙏 Introduction**\nAssalam-o-Alaikum! Welcome to Mehman. I'm here to help you navigate Pakistan. Ask me about places to visit, local customs, transportation, food, or anything else you need to know!",
      timestamp: '10:30 AM'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * 🎨 Built-in Structural Layout Parser Helper
   * Scans raw model strings line-by-line and maps Markdown characters to stylized Tailwind nodes
   */
  const renderFormattedText = (rawText: string) => {
    if (!rawText) return null;
    
    return rawText.split('\n').map((line, index) => {
      const trimmedLine = line.trim();
      
      // 1. Parse Block Headings (e.g., "**🙏 Introduction**" or "**🍛 The Food**")
      if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**')) {
        const headerText = trimmedLine.replace(/\*\*/g, '');
        return (
          <h3 key={index} className="text-lg font-bold text-[#14a44d] mt-4 mb-2 first:mt-0">
            {headerText}
          </h3>
        );
      }
      
      // 2. Parse List Bullet Points (e.g., "- Try local street food")
      if (trimmedLine.startsWith('-') || trimmedLine.startsWith('*')) {
        const bulletContent = trimmedLine.replace(/^[-*]\s*/, '');
        return (
          <div key={index} className="flex items-start gap-2 ml-4 mb-1 text-[#e5e7eb]">
            <span className="text-[#14a44d] select-none">•</span>
            <p className="flex-1 leading-relaxed">{renderInlineBold(bulletContent)}</p>
          </div>
        );
      }
      
      // 3. Parse Standard Continuous Text Rows
      return trimmedLine ? (
        <p key={index} className="leading-relaxed text-[#e5e7eb] mb-2">
          {renderInlineBold(line)}
        </p>
      ) : (
        <div key={index} className="h-2" /> // Spacing for empty row layout breaks
      );
    });
  };

  /** Helper method to process inline bold phrases (e.g., "Always use **Aap** instead of Tu") */
  const renderInlineBold = (textSegment: string) => {
    if (!textSegment.includes('**')) return textSegment;
    
    const tokenParts = textSegment.split('**');
    return tokenParts.map((part, i) => 
      i % 2 === 1 ? <strong key={i} className="font-bold text-[#14a44d]">{part}</strong> : part
    );
  };

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userText = input;
    setInput('');
    setIsTyping(true);

    const userTimestamp = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    const userMessageId = Date.now().toString();

    const updatedMessages: Message[] = [
      ...messages,
      {
        id: userMessageId,
        role: 'user',
        content: userText,
        timestamp: userTimestamp
      }
    ];

    const botMessageId = (Date.now() + 1).toString();
    setMessages([
      ...updatedMessages,
      {
        id: botMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
      }
    ]);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, history: [] }),
        signal: controller.signal
      });

      if (!response.body) throw new Error("No network body payload exposed.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let streamBuffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        streamBuffer += decoder.decode(value, { stream: true });
        const textLines = streamBuffer.split('\n');
        streamBuffer = textLines.pop() || '';

        for (const rawLine of textLines) {
          const line = rawLine.trim();
          if (line.startsWith('data: ')) {
            try {
              const dataObject = JSON.parse(line.substring(6));
              if (dataObject.token) {
                setMessages((currentList) =>
                  currentList.map((msg) =>
                    msg.id === botMessageId
                      ? { ...msg, content: msg.content + dataObject.token }
                      : msg
                  )
                );
              }
            } catch (jsonError) {
              // Ignore partial layout row segment fractions safely
            }
          }
        }
      }
    } catch (networkError: any) {
      if (networkError.name !== 'AbortError') {
        setMessages((currentList) =>
          currentList.map((msg) =>
            msg.id === botMessageId
              ? { ...msg, content: "⚠️ Connection breakdown with API backend on port 8000." }
              : msg
          )
        );
      }
    } finally {
      setIsTyping(false);
      abortControllerRef.current = null;
    }
  };

  const handleStopStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header Layout Component */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-[#14a44d] flex items-center justify-center">
            <Bot size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-white text-3xl font-semibold">Mehman</h1>
            <p className="text-[#9ca3af]">A hybrid-cloud RAG platform powered by Groq & Llama 3.3</p>
          </div>
        </div>
        <div className="px-4 py-2 rounded-full bg-[#2d3139] border border-[#14a44d]">
          <span className="text-[#14a44d] text-sm font-medium">Travel focus: Pakistan</span>
        </div>
      </div>

      {/* Dynamic Chat Messages Stream Layout */}
      <div className="flex-1 bg-[#232730] rounded-xl p-6 mb-6 overflow-y-auto space-y-4 min-h-[400px]">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-[#14a44d] flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-white" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-2xl p-4 ${
                message.role === 'user'
                  ? 'bg-[#14a44d] text-white'
                  : 'bg-[#2d3139] text-white border border-[#3d414e]'
              }`}
            >
              {/* FIX: Hand text string variables over to our clean parser helper */}
              <div className="whitespace-pre-wrap">
                {message.role === 'assistant' 
                  ? renderFormattedText(message.content) 
                  : <p className="leading-relaxed">{message.content}</p>
                }
                {isTyping && message.role === 'assistant' && !message.content && "..."}
              </div>
              <span className="text-xs opacity-60 mt-2 block">{message.timestamp}</span>
            </div>
            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-[#2d3139] flex items-center justify-center flex-shrink-0">
                <User size={16} className="text-white" />
              </div>
            )}
          </div>
        ))}
        
        {isTyping && messages[messages.length - 1].content === "" && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-[#14a44d] flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-[#2d3139] border border-[#3d414e] rounded-2xl p-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-[#9ca3af] animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-[#9ca3af] animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-[#9ca3af] animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Message Form Client Layout */}
      <div className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder={isTyping ? "Please wait for Mehman to finish cooking text..." : "How can I help you navigate Pakistan today?"}
          disabled={isTyping}
          className="flex-1 bg-[#232730] text-white px-6 py-4 rounded-xl border border-[#2d3139] focus:border-[#14a44d] focus:outline-none transition-colors placeholder:text-[#6b7280] disabled:opacity-50"
        />
        {!isTyping ? (
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="px-6 py-4 bg-[#14a44d] text-white rounded-xl hover:bg-[#12923e] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={20} />
          </button>
        ) : (
          <button
            onClick={handleStopStream}
            className="px-6 py-4 bg-[#ef4444] text-white rounded-xl hover:bg-[#dc2626] transition-colors flex items-center gap-2"
          >
            <StopCircle size={20} />
          </button>
        )}
      </div>
    </div>
  );
}
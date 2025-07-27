import React, { useState, useRef, useEffect } from "react";
import {
  MessageCircle,
  Send,
  Bot,
  User,
  X,
  Minimize2,
  Maximize2,
  Sparkles,
  Loader2,
  RotateCcw,
  Zap,
} from "lucide-react";
import { GlassCard } from "./ui/glass-card";
import { Button } from "./ui/button";
import { cn } from "../lib/utils";

// API Integration Functions
const chatbotAPI = {
  sendMessage: async (
    message: string,
    conversationId: string | null = null,
    podcastContext: any = null
  ) => {
    try {
      const response = await fetch("/api/chatbot/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          conversationId,
          podcastContext,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        response: data.response,
        conversationId: data.conversationId,
        suggestions: data.suggestions || [],
      };
    } catch (error) {
      console.error("Chatbot API Error:", error);
      return {
        success: false,
        error: (error as Error).message,
        response:
          "I'm sorry, I'm having trouble connecting right now. Please try again later.",
      };
    }
  },

  getHistory: async (conversationId: string) => {
    try {
      const response = await fetch(`/api/chatbot/history/${conversationId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        messages: data.messages,
      };
    } catch (error) {
      console.error("History API Error:", error);
      return {
        success: false,
        error: (error as Error).message,
        messages: [],
      };
    }
  },

  clearConversation: async (conversationId: string) => {
    try {
      const response = await fetch(`/api/chatbot/clear/${conversationId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      return {
        success: response.ok,
        message: response.ok
          ? "Conversation cleared"
          : "Failed to clear conversation",
      };
    } catch (error) {
      console.error("Clear API Error:", error);
      return {
        success: false,
        error: (error as Error).message,
      };
    }
  },
};

// Message Interface
interface Message {
  id: number;
  content: string;
  isBot: boolean;
  timestamp: string;
}

// Enhanced Message Component
const ChatMessage = ({ message, isBot }: { message: Message; isBot: boolean }) => (
  <div
    className={cn(
      "flex gap-4 mb-6 animate-fade-in-up",
      isBot ? "" : "flex-row-reverse"
    )}
  >
    <div
      className={cn(
        "w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg",
        isBot
          ? "bg-gradient-primary text-primary-foreground shadow-glow"
          : "bg-gradient-accent text-white shadow-accent-glow"
      )}
    >
      {isBot ? (
        <Sparkles className="w-5 h-5" />
      ) : (
        <User className="w-5 h-5" />
      )}
    </div>
    <div className={cn("max-w-[75%] flex flex-col", isBot ? "" : "items-end")}>
      <div
        className={cn(
          "relative px-4 py-3 rounded-2xl shadow-lg transition-all duration-200 hover:shadow-xl",
          isBot
            ? "bg-gradient-glass backdrop-blur-sm border border-white/10 text-foreground rounded-tl-md"
            : "bg-gradient-primary text-primary-foreground shadow-glow rounded-tr-md"
        )}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">
          {message.content}
        </p>
        {/* Message tail */}
        <div
          className={cn(
            "absolute w-3 h-3 rotate-45",
            isBot
              ? "bg-gradient-glass border-l border-t border-white/10 -left-1.5 top-4"
              : "bg-gradient-primary -right-1.5 top-4"
          )}
        />
      </div>
      <div className="text-xs text-muted-foreground mt-2 px-2 font-medium">
        {new Date(message.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })}
      </div>
    </div>
  </div>
);

// Enhanced Typing Indicator
const TypingIndicator = () => (
  <div className="flex gap-4 mb-6 animate-fade-in">
    <div className="w-10 h-10 rounded-2xl bg-gradient-primary text-primary-foreground flex items-center justify-center shadow-glow">
      <Sparkles className="w-5 h-5" />
    </div>
    <div className="bg-gradient-glass backdrop-blur-sm border border-white/10 rounded-2xl rounded-tl-md px-4 py-3 shadow-lg relative">
      <div className="flex gap-1 items-center">
        <div className="w-2 h-2 bg-primary rounded-full animate-typing-dots"></div>
        <div className="w-2 h-2 bg-primary rounded-full animate-typing-dots" style={{animationDelay: '0.2s'}}></div>
        <div className="w-2 h-2 bg-primary rounded-full animate-typing-dots" style={{animationDelay: '0.4s'}}></div>
      </div>
      <div className="absolute w-3 h-3 bg-gradient-glass border-l border-t border-white/10 rotate-45 -left-1.5 top-4" />
    </div>
  </div>
);

// Enhanced Suggestion Pills
const SuggestionPills = ({ 
  suggestions, 
  onSuggestionClick 
}: { 
  suggestions: string[]; 
  onSuggestionClick: (suggestion: string) => void;
}) => {
  const [isVisible, setIsVisible] = useState(true);

  if (!suggestions || suggestions.length === 0 || !isVisible) return null;

  const handleSuggestionClick = (suggestion: string) => {
    onSuggestionClick(suggestion);
    // Auto-hide after clicking a suggestion
    setIsVisible(false);
  };

  return (
    <div className="p-4 border-t border-white/10 bg-gradient-glass backdrop-blur-sm relative">
      {/* Close button */}
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 h-6 w-6 p-0 text-foreground/60 hover:text-foreground hover:bg-white/10"
        onClick={() => setIsVisible(false)}
      >
        <X className="w-3 h-3" />
      </Button>

      <div className="flex items-center gap-2 mb-3">
        <Zap className="w-4 h-4 text-accent" />
        <span className="text-xs font-semibold text-foreground/80">
          Quick questions
        </span>
      </div>
      
      <div className="flex flex-wrap gap-2 pr-8">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            className="text-xs h-8 border-white/20 bg-white/5 hover:bg-gradient-accent hover:border-accent/50 hover:text-white transition-all duration-200 hover:scale-105 backdrop-blur-sm"
            onClick={() => handleSuggestionClick(suggestion)}
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
};


// Main Chatbot Component
const PodcastChatbot = ({ podcastContext = null }: { podcastContext?: any }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content:
        "Hi! I'm your AI assistant. I can help you understand and explore the podcast content you've analyzed. What would you like to know?",
      isBot: true,
      timestamp: new Date().toISOString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState([
    "What are the key points discussed?",
    "Can you summarize the main topics?",
    "What are the most important quotes?",
    "What questions were asked?",
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when chatbot opens
  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, isMinimized]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputMessage]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      content: inputMessage.trim(),
      isBot: false,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    try {
      const result = await chatbotAPI.sendMessage(
        currentMessage,
        conversationId,
        podcastContext
      );

      const botMessage: Message = {
        id: Date.now() + 1,
        content: result.response,
        isBot: true,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);

      if (result.conversationId) {
        setConversationId(result.conversationId);
      }

      if (result.suggestions) {
        setSuggestions(result.suggestions);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        content:
          "I apologize, but I'm having trouble processing your request right now. Please try again.",
        isBot: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  const clearConversation = async () => {
    if (conversationId) {
      await chatbotAPI.clearConversation(conversationId);
    }
    setMessages([
      {
        id: 1,
        content:
          "Hi! I'm your AI assistant. I can help you understand and explore the podcast content you've analyzed. What would you like to know?",
        isBot: true,
        timestamp: new Date().toISOString(),
      },
    ]);
    setConversationId(null);
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <div className="fixed bottom-6 right-6 z-50 animate-scale-in">
          <Button
            onClick={() => setIsOpen(true)}
            className="w-16 h-16 rounded-full bg-gradient-primary hover:scale-110 shadow-glow hover:shadow-xl transition-all duration-300 group relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-20 transition-opacity duration-300 animate-pulse-glow" />
            <MessageCircle className="w-7 h-7 group-hover:rotate-12 transition-transform duration-300" />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-accent rounded-full flex items-center justify-center animate-float">
              <Sparkles className="w-3 h-3 text-white" />
            </div>
          </Button>
        </div>
      )}

      {/* Chatbot Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 animate-slide-in-right">
          <GlassCard
            className={cn(
              "transition-all duration-500 ease-out shadow-2xl border-white/20",
              isMinimized 
                ? "w-80 h-20" 
                : "w-[420px] h-[680px] md:w-[450px] md:h-[720px]",
              "flex flex-col backdrop-blur-2xl"
            )}
          >
            {/* Enhanced Header */}
            <div className="flex items-center justify-between p-5 border-b border-white/10 bg-gradient-glass backdrop-blur-sm">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-10 h-10 rounded-2xl bg-gradient-primary flex items-center justify-center shadow-glow">
                    <Sparkles className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-gradient-accent rounded-full border-2 border-white animate-pulse" />
                </div>
                <div>
                  <h3 className="font-bold text-foreground text-lg">
                    AI Assistant
                  </h3>
                  <p className="text-xs text-muted-foreground font-medium">
                    Ready to help with your podcast
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="w-9 h-9 rounded-xl hover:bg-white/10 transition-colors duration-200"
                >
                  {isMinimized ? (
                    <Maximize2 className="w-4 h-4" />
                  ) : (
                    <Minimize2 className="w-4 h-4" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="w-9 h-9 rounded-xl hover:bg-white/10 transition-colors duration-200"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {!isMinimized && (
              <>
                {/* Enhanced Messages Area */}
                <div className="flex-1 overflow-y-auto p-5 space-y-1 chatbot-scrollbar">
                  {messages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      message={message}
                      isBot={message.isBot}
                    />
                  ))}
                  {isLoading && <TypingIndicator />}
                  <div ref={messagesEndRef} />
                </div>

                {/* Enhanced Suggestions */}
                <SuggestionPills
                  suggestions={suggestions}
                  onSuggestionClick={handleSuggestionClick}
                />

                {/* Enhanced Input Area */}
                <div className="p-5 border-t border-white/10 bg-gradient-glass backdrop-blur-sm">
                  <div className="flex gap-3 items-end">
                    <div className="flex-1 relative">
                      <textarea
                        ref={inputRef}
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about the podcast content..."
                        className="w-full bg-white/5 border border-white/20 rounded-2xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 backdrop-blur-sm transition-all duration-200 min-h-[44px] max-h-[120px] placeholder:text-muted-foreground/70"
                        disabled={isLoading}
                        rows={1}
                      />
                    </div>
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                      className="h-11 w-11 rounded-2xl bg-gradient-primary hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-glow transition-all duration-200"
                    >
                      {isLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </Button>
                  </div>
                  <div className="flex justify-between items-center mt-3">
                    <span className="text-xs text-muted-foreground/70 font-medium">
                      Press Enter to send • Shift+Enter for new line
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearConversation}
                      className="text-xs h-7 px-3 rounded-lg hover:bg-white/10 transition-colors duration-200"
                    >
                      <RotateCcw className="w-3 h-3 mr-1" />
                      Clear
                    </Button>
                  </div>
                </div>
              </>
            )}
          </GlassCard>
        </div>
      )}

      {/* Custom Scrollbar Styles */}
      <style>{`
        .chatbot-scrollbar::-webkit-scrollbar {
          width: 6px;
        }

        .chatbot-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }

        .chatbot-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 10px;
        }

        .chatbot-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </>
  );
};

export default PodcastChatbot;
"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, Sparkles, BookOpen, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import { chatApi } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function TutorChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "¡Hola! Soy tu tutor StudyPilot. He analizado tus materiales y estoy listo para resolver cualquier duda. ¿De qué quieres hablar hoy?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al final cuando hay mensajes nuevos
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const history = messages.slice(-5).map(m => ({ role: m.role, content: m.content }));
      const data = await chatApi.sendMessage(input, history);
      
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Lo siento, he tenido un problema al procesar tu consulta. ¿Puedes repetirla?" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] w-full max-w-3xl mx-auto glass-card overflow-hidden shadow-2xl border-primary/20">
      {/* Header */}
      <div className="p-4 border-b border-border/60 bg-primary/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-brand-gradient flex items-center justify-center shadow-lg shadow-primary/20">
            <Bot className="text-white w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground flex items-center gap-1.5">
              Tutor IA StudyPilot
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            </h3>
            <p className="text-[10px] text-muted-foreground flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Basado en tus materiales
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
           <button className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground" title="Limpiar chat" onClick={() => setMessages([messages[0]])}>
             <MessageSquare className="w-4 h-4" />
           </button>
        </div>
      </div>

      {/* Messages Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-border"
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={cn(
              "flex gap-3 animate-fade-in-up",
              msg.role === "user" ? "flex-row-reverse" : "flex-row"
            )}
          >
            <div className={cn(
              "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
              msg.role === "user" ? "bg-secondary border-border" : "bg-primary/10 border-primary/20"
            )}>
              {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-primary" />}
            </div>
            
            <div className={cn(
              "max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed",
              msg.role === "user" 
                ? "bg-primary text-white rounded-tr-none shadow-md" 
                : "bg-muted/50 border border-border/40 text-foreground rounded-tl-none"
            )}>
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 animate-pulse">
            <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
            </div>
            <div className="bg-muted/50 border border-border/40 p-4 rounded-2xl rounded-tl-none w-24 flex gap-1 items-center justify-center">
              <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce" />
              <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-card/40 border-t border-border/60">
        <div className="relative flex items-center">
          <input
            type="text"
            placeholder="Pregunta algo sobre tus apuntes..."
            className="w-full bg-muted/50 border border-border rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/60 transition-all"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-lg bg-primary text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[10px] text-center mt-2 text-muted-foreground flex items-center justify-center gap-1">
          <BookOpen className="w-3 h-3" />
          El tutor usa RAG para buscar en tus documentos
        </p>
      </div>
    </div>
  );
}

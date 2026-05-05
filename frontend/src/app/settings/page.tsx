"use client";

import { useState } from "react";
import { User, Paintbrush, Check, X, Loader2, Moon, Sun } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const { userName, setUserName } = useAuthStore();
  const [isEditingUser, setIsEditingUser] = useState(false);
  const [newUserName, setNewUserName] = useState(userName || "");
  const [loading, setLoading] = useState(false);
  
  // Theme state (local for now)
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  const handleSaveUser = async () => {
    setLoading(true);
    // Simulamos guardado en backend
    await new Promise((r) => setTimeout(r, 800));
    setUserName(newUserName);
    setIsEditingUser(false);
    setLoading(false);
  };

  const toggleTheme = () => {
    setTheme(t => t === "dark" ? "light" : "dark");
    // Aquí se podría integrar con next-themes o similar
    document.documentElement.classList.toggle("light-mode");
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8 animate-fade-in-up">
      <div className="space-y-1">
        <h1 className="text-3xl font-display font-bold text-gradient">
          Ajustes
        </h1>
        <p className="text-sm text-muted-foreground">
          Gestiona tus preferencias de cuenta y personaliza tu experiencia.
        </p>
      </div>

      <div className="space-y-6">
        {/* Perfil de Usuario */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-primary/10 text-primary border border-primary/20">
                <User className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Perfil de Usuario</p>
                <p className="text-xs text-muted-foreground mt-0.5">Actualiza tu nombre de visualización</p>
              </div>
            </div>
            {!isEditingUser && (
              <button 
                onClick={() => setIsEditingUser(true)}
                className="btn-secondary text-xs px-4 py-2"
              >
                Editar
              </button>
            )}
          </div>

          {isEditingUser && (
            <div className="mt-4 p-4 rounded-xl bg-muted/30 border border-border flex items-end gap-3 animate-in fade-in slide-in-from-top-2">
              <div className="flex-1 space-y-1.5">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                  Nombre de Usuario
                </label>
                <input
                  type="text"
                  value={newUserName}
                  onChange={(e) => setNewUserName(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="Tu nombre..."
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setIsEditingUser(false)}
                  className="p-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
                <button
                  onClick={handleSaveUser}
                  disabled={loading || !newUserName.trim()}
                  className="p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Check className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Apariencia */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <Paintbrush className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Apariencia</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Cambiar entre modo {theme === "dark" ? "claro" : "oscuro"}
                </p>
              </div>
            </div>
            <button 
              onClick={toggleTheme}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border bg-muted/20 hover:bg-muted transition-all"
            >
              {theme === "dark" ? (
                <>
                  <Sun className="w-4 h-4" />
                  <span className="text-xs font-medium">Modo Claro</span>
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4" />
                  <span className="text-xs font-medium">Modo Oscuro</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

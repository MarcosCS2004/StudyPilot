import type { Metadata } from "next";
import { User, Bell, Paintbrush } from "lucide-react";

export const metadata: Metadata = {
  title: "Ajustes",
  description: "Configura tu cuenta y preferencias del tutor IA.",
};

export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8 animate-fade-in-up">
      <div className="space-y-1">
        <h1 className="text-3xl font-display font-bold text-gradient">
          Ajustes
        </h1>
        <p className="text-sm text-muted-foreground">
          Gestiona tus preferencias, cuenta y notificaciones.
        </p>
      </div>

      <div className="glass-card p-6 space-y-4">
        {/* Placeholder items para ajustes */}
        <div className="flex items-center justify-between p-4 rounded-xl border border-border/50 bg-muted/20 hover:border-primary/30 transition-colors">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-primary/10 text-primary border border-primary/20">
              <User className="w-5 h-5" />
            </div>
            <div>
              <p className="font-semibold text-foreground">Perfil de Usuario</p>
              <p className="text-xs text-muted-foreground mt-0.5">Actualiza tu información personal e email</p>
            </div>
          </div>
          <button className="btn-secondary text-xs px-4 py-2">Editar</button>
        </div>

        <div className="flex items-center justify-between p-4 rounded-xl border border-border/50 bg-muted/20 hover:border-primary/30 transition-colors">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <p className="font-semibold text-foreground">Notificaciones</p>
              <p className="text-xs text-muted-foreground mt-0.5">Avisos de rachas, repasos y feedback</p>
            </div>
          </div>
          <button className="btn-secondary text-xs px-4 py-2">Configurar</button>
        </div>
        
        <div className="flex items-center justify-between p-4 rounded-xl border border-border/50 bg-muted/20 hover:border-primary/30 transition-colors">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Paintbrush className="w-5 h-5" />
            </div>
            <div>
              <p className="font-semibold text-foreground">Apariencia</p>
              <p className="text-xs text-muted-foreground mt-0.5">Personaliza el tema y el diseño visual</p>
            </div>
          </div>
          <button className="btn-secondary text-xs px-4 py-2">Cambiar</button>
        </div>
      </div>
    </div>
  );
}

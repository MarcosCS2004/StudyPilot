"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap, Loader2, Mail, Lock, User } from "lucide-react";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nombre, setNombre] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const login = useAuthStore((state) => state.login);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/auth/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, nombre }),
        }
      );

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Error al registrarse");
      }

      const data = await res.json();
      login(data.access_token, data.user_name);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Error al registrarse");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl" />

      <div className="w-full max-w-md glass-card p-8 space-y-6 relative z-10 animate-fade-in-up">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-brand-gradient flex items-center justify-center mx-auto mb-4">
            <Zap className="w-6 h-6 text-white" fill="currentColor" />
          </div>
          <h1 className="text-2xl font-display font-bold text-gradient">
            Únete a StudyPilot
          </h1>
          <p className="text-sm text-muted-foreground">
            Crea tu cuenta para empezar a estudiar con IA.
          </p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground/80 uppercase tracking-wider">
              Nombre Completo
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                required
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                className="w-full bg-muted/50 border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                placeholder="Tu nombre"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground/80 uppercase tracking-wider">
              Correo Electrónico
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-muted/50 border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                placeholder="alumno@universidad.edu"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground/80 uppercase tracking-wider">
              Contraseña
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-muted/50 border border-border rounded-xl py-2.5 pl-10 pr-4 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs text-center font-medium">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full justify-center mt-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              "Crear mi Cuenta"
            )}
          </button>
        </form>

        <div className="text-center text-sm text-muted-foreground">
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" className="text-primary hover:underline font-semibold">
            Inicia Sesión
          </Link>
        </div>
      </div>
    </div>
  );
}

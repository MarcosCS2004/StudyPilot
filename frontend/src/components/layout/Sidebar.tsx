"use client";

/**
 * Sidebar.tsx – StudyPilot navigation sidebar
 * Collapsible on mobile, persistent on desktop
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  Brain,
  Upload,
  Microscope,
  Settings,
  ChevronLeft,
  Menu,
  Flame,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, id: "nav-dashboard" },
  { href: "/study", label: "Estudiar", icon: Brain, id: "nav-study" },
  { href: "/upload", label: "Materiales", icon: Upload, id: "nav-upload" },
  { href: "/exam-autopsy", label: "Autopsia Examen", icon: Microscope, id: "nav-autopsy" },
  { href: "/settings", label: "Ajustes", icon: Settings, id: "nav-settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 w-10 h-10 rounded-xl glass-card flex items-center justify-center"
        onClick={() => setMobileOpen((o) => !o)}
        aria-label="Toggle navigation"
        id="btn-sidebar-toggle"
      >
        <Menu className="w-5 h-5 text-foreground" />
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 h-full z-40 flex flex-col transition-all duration-300",
          "border-r border-border bg-card/80 backdrop-blur-xl",
          collapsed ? "w-16" : "w-64",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-4 py-5 border-b border-border shrink-0">
          {!collapsed && (
            <Link href="/" className="flex items-center gap-2" id="nav-logo">
              <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" fill="currentColor" />
              </div>
              <span className="font-display font-bold text-lg text-gradient">
                StudyPilot
              </span>
            </Link>
          )}
          {collapsed && (
            <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center mx-auto">
              <Zap className="w-4 h-4 text-white" fill="currentColor" />
            </div>
          )}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="hidden lg:flex w-7 h-7 rounded-md items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            id="btn-collapse-sidebar"
          >
            <ChevronLeft
              className={cn("w-4 h-4 transition-transform duration-300", collapsed && "rotate-180")}
            />
          </button>
        </div>

        {/* Streak mini widget */}
        {!collapsed && (
          <div className="mx-3 mt-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center gap-2">
            <Flame className="w-5 h-5 text-amber-400 shrink-0" fill="currentColor" />
            <div>
              <p className="text-xs font-bold text-amber-400">Racha activa</p>
              <p className="text-[10px] text-muted-foreground">
                ¡No la rompas hoy!
              </p>
            </div>
          </div>
        )}

        {/* Nav items */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ href, label, icon: Icon, id }) => {
            const active = pathname === href || (href !== "/" && pathname.startsWith(href));
            return (
              <Link
                key={href}
                id={id}
                href={href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                  active
                    ? "bg-primary/15 text-primary border border-primary/25"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <Icon className={cn("w-5 h-5 shrink-0", active && "text-primary")} />
                {!collapsed && <span>{label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Bottom user area */}
        {!collapsed && (
          <div className="px-3 py-4 border-t border-border shrink-0">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-muted/50">
              <div className="w-8 h-8 rounded-full bg-brand-gradient flex items-center justify-center text-xs font-bold text-white">
                O
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-foreground truncate">
                  Oscar
                </p>
                <p className="text-[10px] text-muted-foreground">
                  Plan Pro
                </p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}

"use client"

import { cn } from "@/lib/utils"
import { Sidebar } from "./sidebar"

interface AppShellProps {
  children: React.ReactNode
  className?: string
}

export function AppShell({ children, className }: AppShellProps) {
  return (
    <div className="relative min-h-screen w-full bg-background">
      <Sidebar />
      <main 
        className={cn(
          "flex min-h-screen flex-col pl-64 transition-all duration-300 ease-in-out",
          className
        )}
      >
        <div className="container max-w-7xl mx-auto p-8 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
          {children}
        </div>
      </main>
    </div>
  )
}

"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Activity, FlaskConical, Gem } from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  {
    name: "Macro Radar",
    href: "/macro-radar",
    icon: Activity,
  },
  {
    name: "Metals",
    href: "/metals",
    icon: Gem,
  },
  {
    name: "Theses",
    href: "/theses",
    icon: FlaskConical,
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-card/95 backdrop-blur-sm">
      <div className="flex h-20 items-center px-6">
        <Link 
          href="/" 
          className="font-display text-2xl font-bold tracking-tight text-foreground transition-opacity hover:opacity-80"
        >
          Meridian
        </Link>
      </div>
      
      <nav className="flex flex-col gap-2 px-4 py-4">
        <div className="px-2 mb-2">
          <p className="text-xs font-medium text-muted-foreground/70 uppercase tracking-wider">
            Markets
          </p>
        </div>
        
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href)
          const Icon = item.icon
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-in-out",
                isActive 
                  ? "bg-primary/10 text-primary shadow-sm ring-1 ring-primary/20" 
                  : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
              )}
            >
              <Icon 
                className={cn(
                  "h-4 w-4 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )} 
              />
              {item.name}
            </Link>
          )
        })}
      </nav>
      
      <div className="absolute bottom-8 left-0 w-full px-6">
        <div className="rounded-lg border border-border bg-background/50 p-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <p className="text-xs font-medium text-muted-foreground">System Operational</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

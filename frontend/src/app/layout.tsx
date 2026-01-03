import type { Metadata } from "next";
import { Fraunces, Space_Grotesk } from "next/font/google";

import "@/styles/globals.css";
import Link from "next/link";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-sans",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "Meridian",
  description: "Macro intelligence dashboard",
};

const navItems = [
  { label: "Macro Radar", href: "/macro-radar" },
  { label: "Metals", href: "/metals" },
  { label: "Theses", href: "/theses" },
];

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${fraunces.variable}`}>
        <div className="shell">
          <header className="topbar">
            <Link className="brand" href="/">
              Meridian
            </Link>
            <nav className="nav">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href}>
                  {item.label}
                </Link>
              ))}
            </nav>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import Link from "next/link";
import { CircleHelp, Home, Languages, Landmark } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "YojanaGPT",
  description: "Find Indian government schemes that may fit your profile."
};

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/schemes", label: "Schemes", icon: Landmark },
  { href: "/chat", label: "Help", icon: CircleHelp }
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <Link href="/" className="flex items-center gap-3" aria-label="YojanaGPT home">
              <span className="grid size-10 place-items-center rounded-full border border-saffron/30 bg-saffron/10 text-lg font-bold text-saffron">Y</span>
              <span className="text-2xl font-extrabold tracking-tight">
                <span className="text-saffron">Yojana</span>
                <span className="text-primary">GPT</span>
              </span>
            </Link>

            <nav className="hidden items-center gap-1 md:flex">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="inline-flex h-10 items-center gap-2 rounded-md px-4 text-sm font-semibold text-muted-foreground transition hover:bg-muted hover:text-primary"
                  >
                    <Icon aria-hidden="true" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <button className="hidden h-10 items-center gap-2 rounded-md border border-border bg-background px-3 text-sm font-semibold text-foreground sm:inline-flex">
              <Languages aria-hidden="true" />
              English
            </button>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}

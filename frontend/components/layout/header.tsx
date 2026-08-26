import Link from "next/link";
import { Trophy } from "lucide-react";

import { PROJECT_REPORT_URL } from "@/lib/site-config";

const navigation = [
  { href: "/", label: "Overview" },
  { href: "/groups", label: "Groups" },
  { href: "/teams", label: "Teams" },
  { href: "/bracket", label: "Bracket" },
  { href: "/matches", label: "Matches" },
  { href: "/compare", label: "Compare" },
];

export function Header() {
  return (
    <header className="sticky top-0 z-20 border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <Link href="/" className="flex items-center gap-2 font-bold tracking-tight">
          <span className="grid size-9 place-items-center rounded-xl bg-primary text-primary-foreground">
            <Trophy className="size-5" />
          </span>
          WC26 Predictor
        </Link>
        <nav aria-label="Main navigation" className="flex gap-1 overflow-x-auto">
          {navigation.map((item) => (
            <Link key={item.href} href={item.href} className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition hover:bg-accent hover:text-foreground">
              {item.label}
            </Link>
          ))}
          {PROJECT_REPORT_URL && (
            <a
              href={PROJECT_REPORT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition hover:bg-accent hover:text-foreground"
            >
              Project Report
            </a>
          )}
        </nav>
      </div>
    </header>
  );
}

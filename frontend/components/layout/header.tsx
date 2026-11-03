"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { cn } from "@/lib/utils";

const ROUTES = [
  { path: "", key: "result" },
  { path: "/groups", key: "groups" },
  { path: "/bracket", key: "bracket" },
  { path: "/matches", key: "matches" },
  { path: "/teams", key: "teams" },
  { path: "/method", key: "method" },
] as const;

export function Header({ lang, nav }: { lang: Locale; nav: Dictionary["nav"] }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const rest = pathname.replace(/^\/(en|es)(?=\/|$)/, "");
  const other: Locale = lang === "en" ? "es" : "en";

  const links = ROUTES.map((route) => {
    const active = route.path === "" ? rest === "" : rest.startsWith(route.path);
    return (
      <Link
        key={route.key}
        href={`/${lang}${route.path}`}
        onClick={() => setOpen(false)}
        aria-current={active ? "page" : undefined}
        className={cn("py-3 transition-colors md:py-0", active ? "font-semibold text-ink" : "text-muted hover:text-ink")}
      >
        {nav[route.key]}
      </Link>
    );
  });

  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex min-h-14 max-w-[1240px] items-center gap-10 px-4 text-sm sm:px-10">
        <Link href={`/${lang}`} className="font-bold tracking-tight">
          WC26 Forecast
        </Link>
        <nav aria-label="Main" className="hidden gap-7 md:flex">
          {links}
        </nav>
        <Link
          href={`/${other}${rest}`}
          hrefLang={other}
          aria-label={nav.switchLanguage}
          title={nav.switchLanguage}
          className="ml-auto border px-2.5 py-1 font-mono text-xs text-ink-2 transition-colors hover:border-ink hover:text-ink"
        >
          {nav.switchLanguageShort}
        </Link>
        <button
          type="button"
          aria-label={open ? nav.closeMenu : nav.openMenu}
          aria-expanded={open}
          aria-controls="mobile-nav"
          onClick={() => setOpen((value) => !value)}
          className="-ml-6 -mr-2.5 grid size-11 place-items-center md:hidden"
        >
          <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 8h16M4 16h16" />}
          </svg>
        </button>
      </div>
      {open && (
        <nav id="mobile-nav" aria-label="Main" className="flex flex-col border-t px-4 text-[15px] md:hidden">
          {links}
        </nav>
      )}
    </header>
  );
}

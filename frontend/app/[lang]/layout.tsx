import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, Inter_Tight } from "next/font/google";
import { notFound } from "next/navigation";

import { Header } from "@/components/layout/header";
import { getDictionary } from "@/lib/i18n";
import { LOCALES, hasLocale } from "@/lib/i18n/config";
import { cn } from "@/lib/utils";

import "../globals.css";

const interTight = Inter_Tight({ subsets: ["latin"], variable: "--font-inter-tight" });
const plexMono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-plex-mono" });

export const dynamicParams = false;

export function generateStaticParams() {
  return LOCALES.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: LayoutProps<"/[lang]">): Promise<Metadata> {
  const { lang } = await params;
  if (!hasLocale(lang)) return {};
  const t = getDictionary(lang).meta;

  return {
    title: { default: t.title, template: `%s · ${t.siteName}` },
    description: t.description,
    alternates: { languages: { en: "/en", es: "/es" } },
    openGraph: { title: t.title, description: t.description, type: "website", locale: lang === "es" ? "es_ES" : "en_GB" },
    twitter: { card: "summary", title: t.title, description: t.description },
  };
}

export const viewport: Viewport = { themeColor: "#ffffff" };

export default async function RootLayout({ children, params }: LayoutProps<"/[lang]">) {
  const { lang } = await params;
  if (!hasLocale(lang)) notFound();
  const t = getDictionary(lang);

  return (
    <html lang={lang} className={cn(interTight.variable, plexMono.variable)}>
      <body className="flex min-h-screen flex-col">
        <Header lang={lang} nav={t.nav} />
        <main className="flex-1 pb-16">{children}</main>
      </body>
    </html>
  );
}

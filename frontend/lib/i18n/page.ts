import "server-only";

import { notFound } from "next/navigation";

import { getDictionary } from "./index";
import { hasLocale } from "./config";
import { formatter } from "./format";
import { teamName } from "./teams";

/** Resolve the locale of a page from its params, with its dictionary and formatters. */
export async function pageContext(params: Promise<{ lang: string }>) {
  const { lang } = await params;
  if (!hasLocale(lang)) notFound();
  return { lang, t: getDictionary(lang), fmt: formatter(lang), team: (name: string) => teamName(lang, name) };
}

export async function pageTitle(params: Promise<{ lang: string }>, key: keyof ReturnType<typeof getDictionary>["meta"]["pages"]) {
  const { lang } = await params;
  return { title: hasLocale(lang) ? getDictionary(lang).meta.pages[key] : undefined };
}

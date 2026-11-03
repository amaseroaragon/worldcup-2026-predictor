import { NextResponse, type NextRequest } from "next/server";

import { DEFAULT_LOCALE, LOCALES, type Locale } from "@/lib/i18n/config";

/** Pick the first supported language from Accept-Language (by q-weight), else the default. */
function preferredLocale(request: NextRequest): Locale {
  const header = request.headers.get("accept-language") ?? "";
  const ranked = header
    .split(",")
    .map((part) => {
      const [tag, q] = part.trim().split(";q=");
      return { lang: tag.toLowerCase().split("-")[0], q: q ? Number(q) : 1 };
    })
    .filter((item) => item.lang)
    .toSorted((a, b) => b.q - a.q);
  return (ranked.find((item) => (LOCALES as readonly string[]).includes(item.lang))?.lang as Locale) ?? DEFAULT_LOCALE;
}

/** Every page lives under /en or /es: send unprefixed paths to the visitor's language. */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasLocale = LOCALES.some((locale) => pathname === `/${locale}` || pathname.startsWith(`/${locale}/`));
  if (hasLocale) return;

  const url = request.nextUrl.clone();
  url.pathname = `/${preferredLocale(request)}${pathname === "/" ? "" : pathname}`;
  return NextResponse.redirect(url);
}

export const config = {
  // Skip Next internals and any path with a file extension (PDFs, JSON, icons).
  matcher: ["/((?!_next|.*\\..*).*)"],
};

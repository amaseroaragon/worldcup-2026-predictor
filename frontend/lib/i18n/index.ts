import "server-only";

import type { Locale } from "./config";
import en from "./dictionaries/en";
import es from "./dictionaries/es";

const DICTIONARIES = { en, es };

export function getDictionary(lang: Locale) {
  return DICTIONARIES[lang];
}

export type { Dictionary } from "./dictionaries/en";

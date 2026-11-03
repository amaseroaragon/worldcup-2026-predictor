# Frontend

Static Next.js site in English and Spanish: the World Cup 2026 forecast next to what actually happened.

```bash
npm install
npm run dev      # http://localhost:3000 (redirects to /en or /es)
npm run lint
npm run build
```

- `app/[lang]/`: pages for the result, groups, bracket, matches, teams, team profiles and method, pre-rendered for `en` and `es`.
- `proxy.ts`: sends unprefixed paths to the visitor's language (`Accept-Language`, default English).
- `lib/i18n/`: dictionaries (`dictionaries/en.ts` defines the shape, `es.ts` must match it), Spanish team names and locale-aware number and date formatting.
- `components/viz/`: charts in plain HTML/CSS (odds dot, stage track, hairline bar, outcome bar).
- `lib/data/`: loaders for `public/data/*.json`. The Python scripts write these files; don't edit them by hand.
- `lib/model-validation.ts`: backtest numbers, copied from `data/backtest/`.

To add a string, add it to `en.ts` first; TypeScript then flags `es.ts` until it is translated. Text passed to client components (`nav`, `matchesUi`, `bracketUi`, …) must be plain strings, not functions.

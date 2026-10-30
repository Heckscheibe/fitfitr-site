# fitfitr-site

The public website for [FitFitr](https://fitfitr.app), an iOS app for editing `.fit` activity files.
It is a small static site served by GitHub Pages from `main`, folder `/`, at `https://fitfitr.app`.
English and German, plain HTML and one CSS file, no build step, no frameworks. No cookies and no requests to any other host until a visitor accepts the analytics
banner (`assets/consent.js`, Google Analytics for Firebase).

This issue (#318 in the app repository) ships the privacy policy, the support page and a minimal landing
page. The full landing page and the how-to guides follow in #812.

## URL map

| Page | English | Deutsch |
|---|---|---|
| Start page: forwards to the visitor's language, falls back to a language chooser | `/` | `/` |
| Landing | `/en/` | `/de/` |
| Privacy policy | `/en/privacy/` | `/de/datenschutz/` |
| Support | `/en/support/` | `/de/support/` |
| Legal notice | `/en/legal-notice/` | `/de/impressum/` |
| Not found | `/404.html` | (bilingual) |
| Guides, reserved for #812 | `/en/guides/` | `/de/anleitungen/` |

`/` forwards each visitor to `/de/` or `/en/` with `assets/lang-redirect.js`, which reads
`navigator.languages` once and sends the first German or English entry (English when none matches,
or when JavaScript is off, via a `<noscript>` meta refresh). It uses `location.replace()` so Back does
not loop, drops any query string and hash, and stores and sends nothing. The page body (wordmark and
two language buttons) only shows if both mechanisms fail.

Each page is `<dir>/index.html`. Links are root-relative, so the site must be served from the domain
root (`python3 -m http.server` from the repository root does that).

## Layout

```
index.html, 404.html        language redirect with chooser fallback, bilingual not-found page
en/, de/                    one folder per language
assets/site.css             all styling, light and dark token sets as CSS custom properties
assets/theme.js             light/dark switch, loaded synchronously in <head>
assets/consent.js           consent banner and opt-in Google Analytics; inert while MEASUREMENT_ID is the placeholder
robots.txt, sitemap.xml, llms.txt   crawler rules, the page list with hreflang, and a plain summary for AI assistants
assets/lang-redirect.js     language redirect of the start page, loaded only by index.html
assets/icon.png             app icon, 512 px
scripts/check.py            link, anchor, hreflang and external-resource checks
scripts/render_events.py    renders the event tables of the privacy policy
scripts/set_policy_date.py  sets the date at the top of both privacy pages
CNAME, .nojekyll            custom domain, no Jekyll processing
```

The light/dark switch stores only the string `light` or `dark` in `localStorage` under the key
`fitfitr-theme`. Without JavaScript the page follows the device's `prefers-color-scheme` and
everything is still readable.

## Checks

```
python3 scripts/check.py
```

Standard library only. It fails (exit code 1) on a broken internal link or `#anchor`, a missing or
non-reciprocal `hreflang` partner, any `http://` URL, an off-site script, stylesheet, font, icon or
image, an inline script, a page without `lang`, title, description, viewport or exactly one `h1`, and
a wrong `CNAME`, and a start page that does not load `lang-redirect.js` before the stylesheet or lacks
its `<noscript>` meta refresh to `/en/`. It prints every remaining `[bracketed placeholder]` as a warning.

## Privacy policy event tables

The tables under "Every event the app can send" are generated from the app's `PRIVACY.md`, so the
policy and the app cannot drift apart:

```
python3 scripts/render_events.py --source /path/to/PRIVACY.md
python3 scripts/render_events.py --source /path/to/PRIVACY.md --check
```

The script rewrites the block between `<!-- events:start -->` and `<!-- events:end -->` in both
privacy pages and refuses to run unless it finds exactly 32 events. `--check` writes nothing and
exits 1 when a page is out of date.

## Voice

The page talks about **editing and sharing**, in active, direct sentences. Use this for every new page
and for the guides in #812.

- **Lead with what the reader does.** Imperative verbs: edit, remove, cut, merge, share. German uses the
  informal imperative ("Bearbeite", "Teile").
- **FitFitr is an editor, not an automatic repair tool.** The reader decides what to remove, replace or
  cut. Do not write that the app "fixes" or "repairs" a file, and do not promise anything happens by itself.
- **The output verb is "share".** Not "send on" or "forward". Say where a file can go: Files, the share
  sheet, Strava.
- **Short sentences, one idea each.** The headline is two short sentences, for example "Edit your .fit
  files. Share them anywhere." / "Bearbeite deine .fit-Dateien. Teile sie, wo du willst."
- **It is not a training log.** Never describe it as tracking, recording or syncing.

## Open placeholders

These are deliberately left in square brackets. They are unresolved decisions, not typos.

The responsible party (Nicolas Hiller and his postal address) and the policy date (12 October 2026) are
filled in. When the policy text changes, run `python3 scripts/set_policy_date.py` as the last step
before merging to `main`. The site has no build step, so the date cannot follow a deploy by itself.

- The hosting sentence in "This website" (GitHub Pages and server logs), pending legal review.
- The rights paragraph in "Your choices and rights", pending legal review.
- The landing page shows a plain "Coming soon to the App Store" label where Apple's official badge
  and the store URL go once the app is listed (see the `TODO` comment in `en/index.html` and
  `de/index.html`).

## What #812 changes

#812 adds guides under `/en/guides/` and `/de/anleitungen/` and replaces the two landing pages
(`/en/`, `/de/`) at the same URLs. It never edits the privacy policy or the support page, and the
header and footer stay identical on every page.

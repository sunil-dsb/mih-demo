# mih-demo

Design work for the MIH Pros app: four boards of phone screens, and the design system behind them.

## Screen boards

Open any board in a browser. The Version 1 to 4 switch at the top of each board moves between them.

| File | What it shows |
|---|---|
| `screens/version-1.html` | Service pro flow: log in, role, home, create an estimate, sent (10 screens) |
| `screens/version-2.html` | Client concept style: the customer quote flow and the pro screens (14 screens) |
| `screens/version-3.html` | The current app's create-estimate flow, as received (7 screens) |
| `screens/version-4.html` | Version 3 with a navy top bar, larger text and cleaner icons (7 screens) |

A picture of every screen is in `screenshots/`, one folder per version.

To run the checks (needs Python, Playwright and Chrome):

```
python build/verify_page.py screens/version-1.html bright
python build/verify_v2.py
```

The photos, names, phone numbers and prices in the screens are placeholders. Photo credits are in `screens/assets/jobs/CREDITS.md`.

## Design system (v4.2)

This document was written before the latest Version 1 text sizes, so the two do not match yet.

Open `index.html` in a browser (internet is needed only for the fonts). The switch at the top previews the app at 150% and 200% phone text size.

| Path | What it is |
|---|---|
| `index.html` | The design system: principles, colour, contrast proof, type, spacing, iOS/Android rules, all components, two sample screens, what happened to each v3 component, research |
| `components.css` | Component styles, using only the tokens |
| `tokens/tokens.json` | All tokens for developers (colours, type scale with growth caps, spacing, radius, sizes) |
| `tokens/tokens.css` | The same tokens as CSS variables (`--ts` = phone text-size setting) |
| `tokens/tokens.js` | Data the page reads (generated, do not edit) |
| `build/palette.py` | Colour ramps in OKLCH, each shade pinned to a contrast target |
| `build/build_tokens.py` | Builds all token files and checks every colour pair; exit code 1 if any pair fails |
| `build/verify_page.py` | Renders the page in Chrome at 100/150/200% text, 1280 and 390 wide, and checks: axe (WCAG AAA), every rendered text's real contrast, 48px tap targets (tiles included), text spilling out of or clipped by any box, overlapping text, tab labels on a true 360 phone, and damaged characters in the files. Screenshots go to `audit/shots/` |
| `audit/contrast-report.txt` | Latest colour check |
| `audit/audit_existing*.{py,txt}` | The same check on the old v3 system, both its themes |

Change a colour or token only in `build/build_tokens.py`, then run:

```
python build/build_tokens.py
python build/verify_page.py
```

Both must end with PASS / exit code 0.

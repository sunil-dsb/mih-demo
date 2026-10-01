"""MIH Pros design system v4.1: build tokens and prove every pair is accessible.

  python build_tokens.py
    -> ../tokens/tokens.json   (all primitives + semantics + type/space/radius/size)
    -> ../tokens/tokens.css    (CSS custom properties, used by ../index.html)
    -> ../tokens/tokens.js     (data for ../index.html; generated, do not edit)
    -> ../audit/contrast-report.txt
  Exits with code 1 if any checked pair misses its threshold.

Thresholds (WCAG 2.2 + our sunlight rule):
  text     7:1    1.4.6 AAA, normal-size text, on EVERY surface it can sit on
  ui-sun   4.5:1  control edges and meaningful icons (WCAG 1.4.11 asks 3:1; we ask more for sun)
  ui       3:1    1.4.11: status dots, the rating star, progress fill vs track
"""
import json, os, sys
from palette import FAMILIES, STEPS, shade, ratio

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- primitives
FAMILIES['ink'] = (264, 0.02, 'Neutrals tinted toward the navy: text, icons, lines, surfaces')
FAMILIES.pop('orange', None)  # v4.0 orange read as brown at AAA; replaced by amber with dark text
FAMILIES['amber'] = (62.6, 0.19, 'Urgent and needs-attention (hue of #FF9500)')
TINT_CAP = {50: 0.02, 100: 0.04, 200: 0.07, 300: 0.10}
prim = {'white': '#FFFFFF',
        'navy': '#14213D',          # client brand: primary button, headers, inverse surfaces
        'navy-pressed': '#2A3A5E'}  # lighter on press: darker than navy would be invisible
for fam, (H, C, _) in FAMILIES.items():
    for step, t in STEPS.items():
        cap = TINT_CAP.get(step, 1) * (0.2 if fam == 'ink' else 1)
        prim[f'{fam}-{step}'] = shade(H, min(C, cap), t)[0]
prim['ink-50'] = '#F2F4F7'     # card grey chosen with the client (1.10:1 vs white); pinned
prim['amber-400'] = '#FF9500'  # the Urgent fill chosen with the client; carries near-black text

# ---------------------------------------------------------------- semantics
S = {
 # surfaces
 'bg-page': 'white', 'bg-card': 'ink-50', 'bg-card-pressed': 'ink-100',
 'bg-input': 'white', 'bg-selected': 'blue-50', 'bg-inverse': 'navy',
 'bg-changed': 'amber-100',
 # text
 'text-primary': 'ink-950', 'text-secondary': 'ink-800', 'text-placeholder': 'ink-700',
 'text-brand': 'navy', 'text-link': 'blue-800', 'text-on-color': 'white', 'text-on-urgent': 'ink-950',
 'text-success': 'green-800', 'text-warning': 'amber-800',
 'text-danger': 'red-800', 'text-info': 'blue-800',
 # actions
 'action-primary': 'navy', 'action-primary-pressed': 'navy-pressed',
 'action-secondary-border': 'navy', 'action-secondary-text': 'navy',
 'action-secondary-pressed': 'ink-100',
 'action-tonal': 'ink-100', 'action-tonal-text': 'navy', 'action-tonal-pressed': 'ink-200',
 'action-destructive': 'red-700', 'action-destructive-pressed': 'red-800',
 'action-disabled': 'ink-100', 'text-disabled': 'ink-600',
 # lines
 'border-divider': 'ink-200', 'border-tile': 'ink-200', 'border-input': 'ink-500', 'border-control': 'ink-600',
 'border-selected': 'blue-700', 'border-focus': 'blue-700', 'border-error': 'red-700',
 # icons
 'icon-default': 'ink-800', 'icon-muted': 'ink-600', 'icon-brand': 'blue-700',
 'icon-success': 'green-700', 'icon-warning': 'amber-600', 'icon-danger': 'red-700',
 'icon-rating': 'amber-500',
 # progress + navigation
 'progress-fill': 'blue-700', 'progress-track': 'ink-200',
 'tab-active': 'navy', 'tab-inactive': 'ink-700',
 # status, three loudness levels (v3's recipe, made AAA):
 #   calm      grey pill + coloured dot + the word (everyday job states)
 #   attention tint + hairline + icon + coloured text (needs someone to act)
 #   priority  solid fill (Urgent = amber with dark text, Emergency = red with white text)
 'status-calm-bg': 'ink-100',
 'dot-waiting': 'amber-500', 'dot-active': 'blue-700', 'dot-done': 'green-700',
 'dot-stopped': 'ink-600', 'dot-problem': 'red-700',
 'status-warning-soft': 'amber-50', 'status-warning-border': 'amber-300',
 'status-danger-soft': 'red-50', 'status-danger-border': 'red-300',
 'status-success-soft': 'green-50', 'status-info-soft': 'blue-50',
 'status-urgent-solid': 'amber-400', 'status-emergency-solid': 'red-700',
}
hexof = lambda token: prim[S.get(token, token)] if S.get(token, token) in prim else S[token]

# ---------------------------------------------------------------- checks
TEXT, SUN, UI = 7.0, 4.5, 3.0
checks = []
def chk(fg, bg, need, use): checks.append((fg, bg, need, use))

for surface in ('bg-page', 'bg-card', 'bg-selected', 'bg-changed'):
    for t in ('text-primary', 'text-secondary', 'text-brand', 'text-link',
              'text-success', 'text-warning', 'text-danger'):
        chk(t, surface, TEXT, f'{t} on {surface}')
chk('text-placeholder', 'bg-input', TEXT, 'Input placeholder (inputs are always white)')
chk('text-primary', 'bg-card-pressed', TEXT, 'Row text while pressed')
chk('text-on-color', 'action-primary', TEXT, 'Primary button label')
chk('text-on-color', 'action-primary-pressed', TEXT, 'Primary button label, pressed')
chk('action-secondary-text', 'bg-page', TEXT, 'Secondary button label')
chk('action-secondary-text', 'action-secondary-pressed', TEXT, 'Secondary button label, pressed')
chk('text-on-color', 'action-destructive', TEXT, 'Destructive button label')
chk('text-on-color', 'action-destructive-pressed', TEXT, 'Destructive button label, pressed')
chk('text-on-color', 'bg-inverse', TEXT, 'Text on navy header / toast / my chat bubble')
chk('tab-active', 'bg-page', TEXT, 'Active tab label')
chk('tab-inactive', 'bg-page', TEXT, 'Inactive tab label')
chk('text-primary', 'status-calm-bg', TEXT, 'Calm status badge word')
chk('text-secondary', 'status-calm-bg', TEXT, 'Cancelled badge word (quieter)')
for d in ('waiting', 'active', 'done', 'stopped', 'problem'):
    chk(f'dot-{d}', 'status-calm-bg', UI, f'{d} dot on calm badge (the word carries meaning)')
chk('text-on-urgent', 'status-urgent-solid', TEXT, 'Urgent badge / header (dark text on amber)')
chk('text-on-color', 'status-emergency-solid', TEXT, 'Emergency badge (white on red)')
for s, t, i in (('warning', 'text-warning', 'icon-warning'), ('danger', 'text-danger', 'icon-danger'),
                ('success', 'text-success', 'icon-success'), ('info', 'text-info', 'icon-brand')):
    chk(t, f'status-{s}-soft', TEXT, f'{s} alert title')
    chk('text-primary', f'status-{s}-soft', TEXT, f'{s} alert body')
    chk(i, f'status-{s}-soft', SUN, f'{s} alert icon')
for surface in ('bg-page', 'bg-card'):
    if surface == 'bg-page': chk('border-input', surface, SUN, 'Input box edge (inputs sit on white only)')
    for b in ('border-selected', 'border-focus', 'border-error', 'border-control',
              'action-secondary-border', 'action-primary', 'action-destructive'):
        chk(b, surface, SUN, f'{b} edge on {surface}')
    for i in ('icon-default', 'icon-muted', 'icon-brand', 'icon-success',
              'icon-warning', 'icon-danger'):
        chk(i, surface, SUN, f'{i} on {surface}')
    chk('icon-rating', surface, UI, f'Rating star on {surface} (always next to the number)')
chk('progress-fill', 'progress-track', UI, 'Progress bar fill vs track')
chk('progress-fill', 'bg-page', SUN, 'Progress bar fill vs page')
chk('border-selected', 'bg-selected', SUN, 'Selected tile outline on its tint')
chk('border-control', 'bg-selected', SUN, 'Radio/checkbox edge on a selected tile')
chk('border-control', 'bg-card', SUN, 'Radio/checkbox edge on a grey card')
chk('action-tonal-text', 'action-tonal', TEXT, 'Tonal (grey) button label')
chk('action-tonal-text', 'action-tonal-pressed', TEXT, 'Tonal button label, pressed')

lines, fails = [], 0
lines.append(f"{'Ratio':>8}  {'Need':>6}  Result  Pair")
for fg, bg, need, use in checks:
    r = ratio(hexof(fg), hexof(bg))
    ok = r >= need
    fails += not ok
    lines.append(f"{r:7.2f}:1 {need:5.1f}:1  {'PASS' if ok else 'FAIL'}    {use}  ({hexof(fg)} on {hexof(bg)})")
lines.append(f"\n{len(checks) - fails} of {len(checks)} pairs pass. Exempt by design: border-divider and "
             "border-tile (decorative; the label, radio or icon identifies the control), "
             "text-disabled (WCAG exempts disabled controls), bg-changed (a tint that supports the 'Changed' tag).")
os.makedirs(os.path.join(ROOT, 'audit'), exist_ok=True)
open(os.path.join(ROOT, 'audit', 'contrast-report.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

# ---------------------------------------------------------------- type scale
BASE, RATIO = 16, 1.15   # client asked for smaller type (2026-09-30); x1.15 keeps headings modern
TYPE = [  # token, step n, weight, line-height ratio, tracking(em), max text-scale, use
 ('small',   -1, 500, 1.4,  0,      2.0, 'Timestamps, badge words (600), tab labels (600), helper lines. Never paragraphs.'),
 ('body',     0, 400, 1.5,  0,      2.0, 'All reading text, input values, list-row detail, chat.'),
 ('label',    0, 600, 1.5,  0,      2.0, 'Input labels, list-row titles, button labels (700 on buttons).'),
 ('title',    1, 700, 1.35, -0.005, 2.0, 'Card titles, the top-bar title, group headers.'),
 ('h3',       2, 700, 1.3,  -0.01,  1.8, 'Section titles, bottom-sheet titles.'),
 ('h2',       3, 700, 1.25, -0.015, 1.6, 'Wizard questions, prices inside cards.'),
 ('h1',       4, 700, 1.2,  -0.02,  1.5, 'One screen title per screen.'),
 ('display',  5, 700, 1.15, -0.025, 1.5, 'The one big number: the estimate total, "You receive".'),
]
type_tokens = {}
for name, n, w, lh, tr, cap, use in TYPE:
    exact = BASE * RATIO ** n
    size = round(exact)
    type_tokens[name] = {'size': size, 'exact': round(exact, 2), 'multiplier': f'{BASE} x {RATIO}^{n}',
                         'lineHeight': lh, 'lineHeightPx': round(size * lh, 1), 'weight': w,
                         'letterSpacing': f'{tr}em', 'maxScale': cap, 'use': use}

SPACE = [4, 8, 12, 16, 20, 24, 32, 40, 48, 64]
RADIUS = {'sm': 8, 'md': 12, 'lg': 16, 'xl': 24, 'pill': 999}
SIZE = {'tap-min': 48, 'button-lg': 56, 'button-md': 48, 'input': 56, 'checkbox': 24,
        'avatar-sm': 32, 'avatar-md': 40, 'avatar-lg': 56, 'icon-sm': 20, 'icon-md': 24,
        'icon-lg': 28, 'icon-tile': 40, 'tabbar': 64, 'topbar': 56, 'topbar-android': 64}

tokens = {
 'name': 'MIH Pros', 'version': '4.2',
 'font': {'family': 'Inter', 'fallback': ['SF Pro Text (iOS)', 'Roboto (Android)'],
          'weights': [400, 500, 600, 700, 800], 'numbers': 'tabular-nums for money, times, counts'},
 'appearance': 'light only (iOS UIUserInterfaceStyle=Light; Android Theme.Light + forceDarkAllowed=false)',
 'color': {'primitive': prim, 'semantic': {k: '{' + v + '}' for k, v in S.items()}},
 'type': {'base': BASE, 'ratio': RATIO, 'scale': type_tokens,
          'componentCaps': {'tab-label': 1.0, 'unread-count': 1.0, 'topbar-title': 1.5, 'icon': 1.5},
          'exceptions': 'Tab labels and unread counts are 14 (five tabs share a 360 phone); everything else is 15 or larger.'},
 'space': {f'space-{v}': v for v in SPACE}, 'radius': RADIUS, 'size': SIZE,
}
os.makedirs(os.path.join(ROOT, 'tokens'), exist_ok=True)
json.dump(tokens, open(os.path.join(ROOT, 'tokens', 'tokens.json'), 'w'), indent=1)

# CSS: --ts is the phone's text-size setting (1 = default, 2 = 200%). Each size is capped at
# its maxScale so big headings and the price never outgrow a 360-wide screen.
css = [':root {', '  --ts: 1;']
css += [f'  --{k}: {v};' for k, v in prim.items()]
css += [f'  --{k}: var(--{v});' for k, v in S.items()]
for k, t in type_tokens.items():
    css += [f'  --type-{k}-size: calc({t["size"]}px * min(var(--ts), {t["maxScale"]}));',
            f'  --type-{k}-lh: {t["lineHeight"]};',
            f'  --type-{k}-weight: {t["weight"]};', f'  --type-{k}-tracking: {t["letterSpacing"]};']
css += [f'  --space-{v}: {v}px;' for v in SPACE]
css += [f'  --radius-{k}: {v}px;' for k, v in RADIUS.items()]
css += [f'  --size-{k}: {v}px;' for k, v in SIZE.items()]
css += ['}']
open(os.path.join(ROOT, 'tokens', 'tokens.css'), 'w').write('\n'.join(css) + '\n')

results = [{'fg': fg, 'bg': bg, 'fgHex': hexof(fg), 'bgHex': hexof(bg), 'need': need, 'use': use,
            'ratio': round(ratio(hexof(fg), hexof(bg)), 2)} for fg, bg, need, use in checks]
js = {'tokens': tokens, 'semanticHex': {k: hexof(k) for k in S}, 'checks': results,
      'families': {f: FAMILIES[f][2] for f in ('blue', 'ink', 'green', 'amber', 'red')},
      'vsWhite': {k: round(ratio(v, '#FFFFFF'), 2) for k, v in prim.items()}}
open(os.path.join(ROOT, 'tokens', 'tokens.js'), 'w').write('window.MIH = ' + json.dumps(js) + ';\n')

print(f'\nType scale (base {BASE} x {RATIO}^n):')
for k, t in type_tokens.items():
    print(f"  {k:8} {t['multiplier']:13} = {t['exact']:6} -> {t['size']}/{t['lineHeightPx']}  w{t['weight']}  max x{t['maxScale']}")
sys.exit(1 if fails else 0)

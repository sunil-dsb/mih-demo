"""Contrast audit of the existing MIH Pros design system (tokens.json v3).
Checks every text/icon/border pair the system actually uses against WCAG 2.2:
  text  -> AAA 7:1 (1.4.6); large text (>=24px, or >=18.66px bold) AAA 4.5:1
  non-text (icons, borders, focus, controls) -> 3:1 (1.4.11; no AAA level exists)
Usage: python audit_existing.py <path-to-tokens.json> [theme]"""
import json, sys, re

def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

tok = json.load(open(sys.argv[1]))
theme = sys.argv[2] if len(sys.argv) > 2 else 'light'
raw = {t['name']: t['value'] for t in tok['color']['tokens']}

def res(name):
    v = raw[name]
    if isinstance(v, dict): v = v.get(theme, v.get('light'))
    m = re.fullmatch(r'\{(.+)\}', v)
    return res(m.group(1)) if m else v

# (foreground, background, kind, where it is used)
P = [
 ('text-primary','bg-page','text','Body text, headings'),
 ('text-secondary','bg-page','text','Addresses, dates, helper text'),
 ('text-placeholder','bg-surface','text','Input placeholder'),
 ('text-link','bg-page','text','Links, tertiary buttons'),
 ('text-primary','bg-subtle','text','Text on grey tiles'),
 ('text-primary','bg-selected','text','Selected chip/tile label'),
 ('text-on-action','action-primary','text','Primary button label'),
 ('text-on-action','action-primary-pressed','text','Primary button pressed'),
 ('text-on-action','action-destructive','text','Destructive button label'),
 ('action-secondary-text','action-secondary','text','Secondary button label'),
 ('action-destructive-text','action-secondary','text','Destructive-secondary label'),
 ('text-inverse','bg-inverse','text','Toast text'),
 ('text-link-inverse','bg-inverse','text','Toast action'),
 ('status-brand-text','status-brand-bg','text','"New" badge'),
 ('status-success-text','status-success-bg','text','Success badge'),
 ('status-info-text','status-info-bg','text','Info badge'),
 ('status-warning-text','status-warning-bg','text','Warning badge/alert'),
 ('status-danger-text','status-danger-bg','text','Danger badge/alert'),
 ('border-input','bg-surface','ui','Input outline'),
 ('border-error','bg-surface','ui','Input error outline'),
 ('border-selected','bg-surface','ui','Selected tile outline'),
 ('border-focus','bg-page','ui','Focus ring'),
 ('border-default','bg-page','ui','Card border / divider'),
 ('border-control','bg-page','ui','Chip outline (resting)'),
 ('action-secondary','bg-page','ui','Secondary button shape vs page'),
 ('action-primary','bg-page','ui','Primary button shape vs page'),
 ('icon-default','bg-page','ui','Default icons'),
 ('icon-muted','bg-page','ui','Chevrons, secondary icons'),
 ('icon-brand','bg-page','ui','Pin, verified check'),
 ('icon-rating','bg-page','ui','Rating star'),
 ('status-success-icon','bg-page','ui','Success icon/dot (calm recipe)'),
 ('status-info-icon','bg-page','ui','Info icon/dot (calm recipe)'),
 ('status-warning-icon','status-warning-bg','ui','Warning icon in alert'),
 ('status-danger-icon','status-danger-bg','ui','Danger icon in alert'),
 ('action-primary','bg-muted','ui','Progress bar fill vs track'),
]
fails = 0
print(f'Theme: {theme}\n')
print(f"{'Pair':58} {'Ratio':>7}  {'Need':>5}  Result   Used for")
for fg, bg, kind, use in P:
    r = ratio(res(fg), res(bg))
    need = 7.0 if kind == 'text' else 3.0
    ok = r >= need
    note = ''
    if kind == 'text' and not ok and r >= 4.5: note = ' (AAA only if large text)'
    fails += not ok
    print(f"{fg+' on '+bg:58} {r:6.2f}:1 {need:4.1f}:1  {'PASS' if ok else 'FAIL'}   {use}{note}")
print(f'\n{fails} of {len(P)} pairs fail.')

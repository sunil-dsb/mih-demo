"""Generate MIH Pros colour ramps in OKLCH, with each shade pinned to a
contrast-vs-white target (WCAG 2.x relative luminance). Rich chroma is kept
as high as the sRGB gamut allows at that lightness.
Run: python palette.py  -> prints ramps and writes palette.json"""
import json, math, os

def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lum_hex(h):
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
def ratio(a, b):
    x, y = sorted((lum_hex(a), lum_hex(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)

def oklch_to_linrgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
def in_gamut(rgb): return all(-1e-4 <= c <= 1 + 1e-4 for c in rgb)
def enc(c):
    c = min(max(c, 0), 1)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
def to_hex(rgb): return '#' + ''.join(f'{round(enc(c) * 255):02X}' for c in rgb)

def shade(H, Cmax, target):
    """Find the OKLCH colour with hue H, the most chroma <= Cmax that fits sRGB,
    whose contrast against white equals `target`."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        L = (lo + hi) / 2
        C = Cmax
        while C > 0 and not in_gamut(oklch_to_linrgb(L, C, H)): C -= 0.002
        hx = to_hex(oklch_to_linrgb(L, max(C, 0), H))
        if ratio(hx, '#FFFFFF') > target: lo = L
        else: hi = L
    return hx, round(L, 3), round(max(C, 0), 3)

# contrast vs white for each step. 700+ always carries white text at AAA (>=7:1)
# and is AAA as text on white; 500 is the lightest step that works as an
# icon/border in sun (>=4.5:1, over WCAG's 3:1).
STEPS = {50: 1.10, 100: 1.22, 200: 1.45, 300: 1.8, 400: 2.7,
         500: 4.6, 600: 6.0, 700: 7.6, 800: 10.5, 900: 14.5, 950: 17.5}
# light tints stay soft (no neon); chroma cap per step, as a share of the family max
TINT_CAP = {50: 0.02, 100: 0.04, 200: 0.07, 300: 0.10}
FAMILIES = {                 # hue, max chroma, role
    'blue':   (262, 0.21, 'Brand and action: buttons, links, selected, progress'),
    'ink':    (262, 0.02, 'Neutrals tinted toward the brand hue: text, borders, surfaces'),
    'green':  (150, 0.17, 'Success, money received, completed'),
    'orange': (48, 0.19, 'Urgent, attention, needs a decision'),
    'red':    (27, 0.21, 'Emergency, errors, declined, destructive'),
}
if __name__ == '__main__':
    out = {}
    for fam, (H, C, role) in FAMILIES.items():
        out[fam] = {'role': role, 'hue': H, 'shades': {}}
        for step, t in STEPS.items():
            cap = TINT_CAP.get(step, 1) * (0.2 if fam == 'ink' else 1)  # neutrals: barely-cool tints
            hx, L, c = shade(H, min(C, cap), t)
            out[fam]['shades'][step] = {'hex': hx, 'oklch': f'oklch({L} {c} {H})',
                                        'vsWhite': round(ratio(hx, '#FFFFFF'), 2)}
        print(fam.ljust(7), '  '.join(f"{s}:{v['hex']}({v['vsWhite']})" for s, v in out[fam]['shades'].items()))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'palette.json'), 'w'), indent=1)

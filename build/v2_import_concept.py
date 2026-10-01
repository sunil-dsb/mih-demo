"""Version 2: turn each machine-generated concept screen into a clean static file, then apply the shared fixes
(contrast, tiny text, one size/weight set, one button colour, tap sizes, placeholders, slimmer header).
The untouched originals are kept in screens/v2/original/."""
import os, re, glob, shutil, colorsys, collections
os.chdir(r'C:\Users\admin\Documents\RB\mih-pros-design-system\screens\v2')
os.makedirs('original', exist_ok=True)
for f in glob.glob('*.html'):
    if not os.path.exists('original/' + f): shutil.copy(f, 'original/' + f)

def L(c):
    c = [x / 255 for x in c]; c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def ratio(a, b):
    x, y = sorted([L(a), L(b)], reverse=True); return (x + 0.05) / (y + 0.05)
def darken_to(rgb, target, on=(255, 255, 255)):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb])
    while ratio([round(v * 255) for v in colorsys.hls_to_rgb(h, l, s)], on) < target: l -= 0.004
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))
BLUE = darken_to((21, 101, 192), 7.05, (234, 242, 252))   # the concept's blue, same hue; 7:1 as text on the light blue page, more with white on it
ORANGE_TEXT = darken_to((154, 52, 18), 7.05, (255, 241, 230))   # orange words on the pale orange tint
ORANGE_BG = darken_to((194, 65, 12), 5.6)                       # the urgent screen: white LARGE text needs 4.5:1; 5.6 leaves margin
RED = darken_to((185, 28, 28), 7.05, (253, 236, 236))
NAVY = (20, 33, 61)
hexs = lambda c: '#%02X%02X%02X' % c
rgbs = lambda c: 'rgb(%d, %d, %d)' % c
print('orange text', hexs(ORANGE_TEXT), 'orange bg', hexs(ORANGE_BG), round(ratio(ORANGE_BG, (255, 255, 255)), 2)); print('blue', hexs(BLUE), round(ratio(BLUE, (255, 255, 255)), 2), '· red', hexs(RED), round(ratio(RED, (255, 255, 255)), 2))

SIZE = {9: 14, 10: 14, 12: 14, 13: 14, 14: 14, 15: 16, 16: 16, 17: 18, 18: 18, 19: 20, 20: 20, 21: 20, 22: 24, 26: 24, 28: 32, 30: 32, 32: 32, 34: 32,
        36: 32, 40: 40, 52: 48, 56: 48, 120: 72}
def weight(new, old):
    if new >= 24: return 800
    if new >= 18: return 700
    return 700 if old >= 700 else 500

TEXT = [('[Saved address], Tempe, AZ', '1420 E Elm St, Tempe, AZ'), ('[DATE]', 'Today'), ('[CUSTOMER NAME]', 'Linda Park')]
stats = collections.Counter()
# per-screen fixes, applied after the shared ones
POST = {
 '01-who-are-you.html': [('gap: 14px; color: rgb(59, 74, 96);"><div style="position: absolute;', 'gap: 14px; color: rgb(20, 33, 61);"><div style="position: absolute;')],
 '04-ai-fills-title-trade.html': [('[Frame from', 'rgb(59, 74, 96)', 'rgb(20, 33, 61)')],
 # estimate: fit the screen without scrolling
 '10-customer-estimate.html': [('padding: 16px 20px 28px; display: flex; flex-direction: column; gap: 14px;', 'padding: 12px 20px 12px; display: flex; flex-direction: column; gap: 10px;'),
   ('border-radius: 22px; padding: 20px; display: flex; flex-direction: column; gap: 4px;', 'border-radius: 22px; padding: 16px 20px; display: flex; flex-direction: column; gap: 2px;'),
   ('border-radius: 22px; padding: 18px 20px; display: flex; flex-direction: column; gap: 12px;', 'border-radius: 22px; padding: 14px 20px; display: flex; flex-direction: column; gap: 8px;'),
   ('border-radius: 22px; padding: 16px 20px; display: flex; flex-direction: column; gap: 10px;', 'border-radius: 22px; padding: 12px 20px 4px; display: flex; flex-direction: column; gap: 0px;'),
   ('height: 56px; border-radius: 28px; border: 3px solid', 'height: 52px; border-radius: 28px; border: 3px solid'),
   ('font-size: 48px; font-weight: 800; color: rgb(20, 33, 61); letter-spacing: -1.5px;', 'font-size: 40px; font-weight: 800; color: rgb(20, 33, 61); letter-spacing: -1px;')],
 # urgent request: header words large enough for the 4.5:1 large-text rule; fits without scrolling
 '11-pro-new-job-request.html': [('font-size: 18px; font-weight: 700; letter-spacing: 2px; margin-top: 8px;', 'font-size: 20px; font-weight: 700; letter-spacing: 1.5px; margin-top: 8px;'),
   ('Tempe', 'font-size: 18px', 'font-size: 20px'),
   ('padding: 60px 24px 28px;', 'padding: 60px 24px 22px;'), ('padding: 26px 20px 28px;', 'padding: 24px 20px 16px;')],
}

def fix_style(st):
    d = collections.OrderedDict()
    for part in st.split(';'):
        if ':' in part:
            k, v = part.split(':', 1); d[k.strip()] = v.strip()
    old_w = int(d['font-weight']) if d.get('font-weight', '').isdigit() else 500
    if 'font-size' in d and d['font-size'].endswith('px'):
        o = round(float(d['font-size'][:-2])); n = SIZE.get(o, o)
        d['font-size'] = f'{n}px'; d['font-weight'] = str(weight(n, old_w)); stats[f'{n}/{d["font-weight"]}'] += 1
    bgv = d.get('background', d.get('background-color', ''))
    # one primary button colour and size: the navy pill button becomes the blue one
    if 'rgb(20, 33, 61)' in bgv and d.get('height') in ('60px', '64px') and d.get('border-radius') in ('30px', '32px'):
        d['background'] = rgbs(BLUE); d['height'] = '60px'; d['border-radius'] = '30px'
    # small orange-red count badge: amber with navy text, like the tags
    if 'rgb(194, 65, 12)' in bgv and d.get('width') == '32px':
        d['background'] = 'rgb(255, 149, 0)'; d['color'] = rgbs(NAVY)
    # icon buttons in the header: 48 wide and tall
    if d.get('width') == '44px' and d.get('height', '44px') == '44px':
        d['width'] = '48px'
        if 'height' in d: d['height'] = '48px'
    # pale tints of white used for small text on blue / orange: plain white
    if d.get('color') in ('rgb(214, 228, 250)', 'rgb(220, 232, 250)', 'rgb(255, 233, 219)'): d['color'] = 'rgb(255, 255, 255)'
    # small orange tags: amber with navy text (white on orange was 3:1)
    if 'rgb(232, 119, 46)' in bgv:
        d['background'] = 'rgb(255, 149, 0)'; d['color'] = rgbs(NAVY)
    # slimmer navy header on the question screens
    if 'rgb(20, 33, 61)' in bgv and d.get('padding') == '56px 12px 14px':
        d['padding'] = '52px 12px 6px'
    out = '; '.join(f'{k}: {v}' for k, v in d.items()) + ';'
    out = out.replace('rgb(21, 101, 192)', rgbs(BLUE)).replace('rgb(11, 37, 69)', rgbs(NAVY)).replace('rgb(185, 28, 28)', rgbs(RED))
    out = out.replace('rgba(232, 119, 46, 0.35)', 'rgba(255, 149, 0, 0.35)')
    out = out.replace('rgb(154, 52, 18)', rgbs(ORANGE_TEXT)).replace('rgb(194, 65, 12)', rgbs(ORANGE_BG))
    return out

fonts_done = False
for f in sorted(glob.glob('original/*.html')):
    name = os.path.basename(f); t = open(f, encoding='utf-8').read()
    if not fonts_done:
        css = [s for s in re.findall(r'<style[^>]*>(.*?)</style>', t, re.S) if 'Plus Jakarta Sans' in s and '@font-face' in s][0]
        faces = re.findall(r'/\* ([a-z-]+) \*/\s*(@font-face\s*\{[^}]*\})', css)
        keep = [b for lang, b in faces if lang in ('latin', 'latin-ext')]
        open('fonts.css', 'w', encoding='utf-8').write('/* Plus Jakarta Sans 500-800, latin + latin-ext, embedded so the board works offline */\n' + '\n'.join(keep) + '\n')
        fonts_done = True; print('fonts.css', len(keep), 'faces', os.path.getsize('fonts.css') // 1024, 'KB')
    a = t.index('<div id="dc-root">'); b = t.index('<script', a)
    body = t[a:b].strip()
    body = re.sub(r' data-dc-tpl="\d+"', '', body); body = re.sub(r' data-sc-name="[^"]*"', '', body)
    body = re.sub(r'style="([^"]*)"', lambda m: 'style="' + fix_style(m.group(1)) + '"', body)
    body = body.replace('stroke="#1565C0"', f'stroke="{hexs(BLUE)}"').replace('fill="#1565C0"', f'fill="{hexs(BLUE)}"')
    for x, y in TEXT: body = body.replace(x, y)
    # the do-it-yourself savings: real amounts
    n = 0
    def money(m):
        global n; n += 1; return '−$45' if n == 1 else '−$25'
    body = re.sub(r'[−-]\$\[X\]', money, body)
    for item in POST.get(name, []):
        if len(item) == 3:      # (text the element starts with, old, new): change that element's own style
            txt, x, y = item
            m = re.search(r'style="([^"]*)">' + re.escape(txt), body); assert m and x in m.group(1), (name, txt, x)
            body = body[:m.start(1)] + m.group(1).replace(x, y) + body[m.end(1):]
        else:
            x, y = item; assert body.count(x) >= 1, (name, x[:70]); body = body.replace(x, y)
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    title = title.group(1).strip() if title else name
    html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{name[:-5]}</title>\n<link rel="stylesheet" href="fonts.css">\n<link rel="stylesheet" href="v2.css">\n</head>\n<body>\n{body}\n</body>\n</html>\n')
    open(name, 'w', encoding='utf-8').write(html)
    print(name, os.path.getsize(name) // 1024, 'KB')

open('v2.css', 'w', encoding='utf-8').write(f"""/* MIH Pros Version 2 (client concept): shared rules. Screen markup keeps its own inline styles. */
:root{{--v2-navy:#14213D;--v2-blue:{hexs(BLUE)};--v2-text-2:#3B4A60;--v2-amber:#FF9500;--v2-red:{hexs(RED)}}}
*{{box-sizing:border-box}}
html,body{{margin:0}}
body{{font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,system-ui,sans-serif;color:#0F1B2D;background:#F4F6FA;-webkit-font-smoothing:antialiased}}
a{{color:var(--v2-blue)}}
button{{cursor:pointer;color:inherit}}
/* tap sizes: every link, button and checkbox row is at least 48 tall */
a,button{{min-height:48px}}
a:not([style*="display"]){{display:inline-flex;align-items:center}}
label:has(input){{min-height:48px}}
input[type=checkbox]{{width:28px;height:28px;flex:none;accent-color:var(--v2-blue)}}
:focus-visible{{outline:3px solid var(--v2-blue);outline-offset:2px}}
""")
print('sizes/weights now:', dict(sorted(stats.items(), key=lambda x: float(x[0].split('/')[0]))))

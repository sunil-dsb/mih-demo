"""Can #14213D be the primary button colour? Checks every pair it would meet."""
import sys; sys.path.insert(0, '.')
from palette import ratio  # same WCAG formula as the palette generator
NAVY = '#14213D'
pairs = [
 ('White label on navy button', '#FFFFFF', NAVY, 7.0),
 ('Navy button shape vs white page', NAVY, '#FFFFFF', 3.0),
 ('Navy button vs light-grey card #F2F4F7', NAVY, '#F2F4F7', 3.0),
 ('Navy as link text on white (AAA text)', NAVY, '#FFFFFF', 7.0),
 ('Pressed state #0B1428 vs navy (needs visible change)', '#0B1428', NAVY, 1.0),
 ('Pressed state #2A3A5E (lighter) vs navy', '#2A3A5E', NAVY, 1.0),
 ('Navy link vs body text #141A23 (WCAG 1.4.1 wants 3:1 if not underlined)', NAVY, '#141A23', 3.0),
 ('Navy vs brand blue #0147C9 (can people tell them apart?)', NAVY, '#0147C9', 1.0),
 ('Focus ring navy vs navy button (ring must show on the button)', NAVY, NAVY, 3.0),
 ('White label on current brand blue #0147C9', '#FFFFFF', '#0147C9', 7.0),
]
for name, fg, bg, need in pairs:
    r = ratio(fg, bg)
    print(f'{r:6.2f}:1  need {need:>4}:1  {"PASS" if r >= need else "FAIL"}  {name}')

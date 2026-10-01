"""Render index.html in Chrome and check it the way a reviewer would.

  python build/verify_page.py            (from the mih-pros-design-system folder)

At text sizes 100%, 150% and 200% it reports:
  - script errors and icons that failed to render
  - axe-core violations (WCAG A/AA/AAA + best practice), at 1280 and 390 wide
  - any rendered app text (inside .m) below 7:1 against its real background
  - any app control smaller than 48 x 48 (tap target)
  - any app element that sticks out of its phone / specimen box
Exit code 1 if anything fails. Screenshots go to audit/shots/.
"""
import pathlib, sys, json
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'index.html')
SHOTS = ROOT / 'audit' / 'shots'
SHOTS.mkdir(parents=True, exist_ok=True)
AXE = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js'

MEASURE = r"""() => {
 const lin=c=>{c/=255;return c<=0.04045?c/12.92:((c+0.055)/1.055)**2.4};
 const parse=s=>{const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}};
 const L=c=>0.2126*lin(c.r)+0.7152*lin(c.g)+0.0722*lin(c.b);
 const ratio=(a,b)=>{const x=L(a),y=L(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)};
 const bgOf=el=>{for(let e=el;e;e=e.parentElement){const c=parse(getComputedStyle(e).backgroundColor);if(c&&c.a>0.9)return c;} return {r:255,g:255,b:255,a:1}};
 const label=el=>{const sl=el.closest('.screen-slot'); if(sl&&sl.querySelector('.cap b')) return sl.querySelector('.cap b').textContent.trim().slice(0,30); const f=el.closest('figure'); if(f&&f.querySelector('figcaption')) return f.querySelector('figcaption').textContent.trim().slice(0,30); return ((el.closest('.spec')||el.closest('.phone')||document.body).querySelector('.spec-head,.phone-cap')||{textContent:'phone'}).textContent.trim().slice(0,26);};
 const out={lowText:[],smallTargets:[],overflow:[]};
 const texts=[];
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 let n; while((n=walker.nextNode())){
  const el=n.parentElement; if(!el||!n.textContent.trim()||!el.closest('.m'))continue;
  const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none')continue;
  const rg=document.createRange(); rg.selectNodeContents(n);
  const rects=[...rg.getClientRects()].filter(r=>r.width>0.5&&r.height>0.5);
  if(!rects.length)continue;
  let vis=rects; for(let a2=el;a2&&a2!==document.body;a2=a2.parentElement){const o=getComputedStyle(a2); if(o.overflowY!=='visible'||o.overflowX!=='visible'){const cb=a2.getBoundingClientRect(); vis=vis.map(r=>({left:Math.max(r.left,cb.left),right:Math.min(r.right,cb.right),top:Math.max(r.top,cb.top),bottom:Math.min(r.bottom,cb.bottom)})).filter(r=>r.right-r.left>1&&r.bottom-r.top>1);}}
  texts.push({n,el,rects:vis});
  // 1. contrast (disabled and hidden-from-AT text excluded, as WCAG allows)
  if(!(el.closest('[aria-hidden=true]')||el.closest(':disabled')||el.closest('[aria-disabled=true]'))){
   const r=ratio(parse(cs.color),bgOf(el)); if(r<7) out.lowText.push({where:label(el),text:n.textContent.trim().slice(0,40),ratio:+r.toFixed(2)});
  }
  // 2. text must stay inside every ancestor that clips or paints a box (buttons, tiles, tags, phones)
  for(let a=el;a&&!a.classList.contains('doc');a=a.parentElement){
   const acs=getComputedStyle(a); const box=a.getBoundingClientRect();
   const paints=(parse(acs.backgroundColor)||{a:0}).a>0.05||acs.overflow!=='visible'||acs.overflowX!=='visible'||a.matches('.phone,.spec-body,.btn,.tag,.chip,.choice,.day,.slot,.ph,.role,.cat .ic,.seg button,.input');
   if(!paints)continue;
   const sx=['auto','scroll'].includes(acs.overflowX), sy=['auto','scroll'].includes(acs.overflowY);
   if(sx||sy){ /* a scroller: content may run past it along the scroll axis only */
    const b2=a.getBoundingClientRect(); let bad=false;
    for(const r of rects){ if(!sy&&(r.top<b2.top-1.5||r.bottom>b2.bottom+1.5)) bad=true; if(!sx&&(r.left<b2.left-1.5||r.right>b2.right+1.5)) bad=true; }
    if(bad) out.overflow.push({where:label(el),el:'scroller clips across its axis',text:n.textContent.trim().slice(0,24),by:0});
    break; }
   for(const r of rects){ const dx=Math.max(box.left-r.left,r.right-box.right), dy=Math.max(box.top-r.top,r.bottom-box.bottom);
    if(dx>1.5||dy>1.5){ out.overflow.push({where:label(el),el:(typeof a.className==='string'?a.className:a.tagName).slice(0,30),text:n.textContent.trim().slice(0,24),by:Math.round(Math.max(dx,dy))}); break; } }
  }
  // 3. text cut by ellipsis/clamp
  if((cs.textOverflow==='ellipsis'&&el.scrollWidth>el.clientWidth+1)||(cs.webkitLineClamp!=='none'&&el.scrollHeight>el.clientHeight+1)) out.overflow.push({where:label(el),el:'truncated',text:n.textContent.trim().slice(0,24),by:el.scrollWidth-el.clientWidth});
 }
 // 4. no two text runs may overlap
 for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){
  const A=texts[i],B=texts[j]; if(A.el.closest('.spec,.phone')!==B.el.closest('.spec,.phone'))continue;
  for(const a of A.rects)for(const b of B.rects){ const ox=Math.min(a.right,b.right)-Math.max(a.left,b.left), oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
   if(ox>2&&oy>2){ out.overflow.push({where:label(A.el),el:'overlap',text:A.n.textContent.trim().slice(0,16)+' / '+B.n.textContent.trim().slice(0,16),by:Math.round(Math.min(ox,oy))}); break; } }
 }
 // 5. tap targets: anything interactive or styled as a tile/button
 const scaleOf=el=>{const ph=el.closest('.phone'); if(!ph) return 1; const t=getComputedStyle(ph).transform; const m=t&&t!=='none'?t.match(/matrix\(([^,]+)/):null; return m?parseFloat(m[1]):1;};
 document.querySelectorAll('.m button, .m a, .m [role=radio], .m [role=tab], .m [role=switch], .m label.input, .m label.check, .m label.radio-row, .m .choice, .m .day, .m .slot, .m .ph.add, .m .cat, .m .chip').forEach(el=>{
  const b=el.getBoundingClientRect(); if(!b.width)return; const k=scaleOf(el);
  if(b.width/k<47.5||b.height/k<47.5) out.smallTargets.push({where:label(el),el:(el.getAttribute('aria-label')||el.textContent.trim()).slice(0,30),w:Math.round(b.width/k),h:Math.round(b.height/k)});
 });
 // 6. tab labels at a true 360-wide phone
 document.querySelectorAll('.m .tabbar').forEach(tb=>{
  const c=tb.cloneNode(true); const holder=document.createElement('div'); holder.className='m'; holder.style.cssText='position:absolute;left:-9999px;top:0;width:360px';
  holder.appendChild(c); document.body.appendChild(holder);
  c.querySelectorAll('.lb').forEach(l=>{ if(l.scrollWidth>l.clientWidth+0.5) out.overflow.push({where:'tab bar at 360',el:'truncated',text:l.textContent,by:l.scrollWidth-l.clientWidth}); });
  holder.remove();
 });
 return out;
}"""

fails = 0
# damaged characters (a bad escape once wrote a NUL byte into the CSS)
for f in ['index.html', 'components.css', 'tokens/tokens.css', 'tokens/tokens.js', 'screens/ui.css', 'screens/pro-estimate-flow.html', 'screens/icons.js']:
    raw = (ROOT / f).read_bytes()
    bad = [i for i, x in enumerate(raw) if x < 9 or 13 < x < 32]
    txt = raw.decode('utf-8', errors='replace')
    if bad or '�' in txt:
        fails += 1
        print(f'damaged characters in {f}: control bytes at {bad[:5]}, replacement chars {txt.count(chr(0xfffd))}')
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    THEMES = sys.argv[2:] or [None]   # optional colour options to test, e.g. navy blue
    for theme, w in [(t, w) for t in THEMES for w in (1280, 390)]:
        pg = b.new_page(viewport={'width': w, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(PAGE.as_uri()); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(400)
        if theme: pg.evaluate(f"document.documentElement.dataset.theme='{theme}'")
        icons = pg.evaluate("[document.querySelectorAll('[data-i]').length, document.querySelectorAll('[data-i] > svg').length, [...document.querySelectorAll('[data-i] > svg')].filter(s=>!s.innerHTML).length]")
        hscroll = pg.evaluate('document.documentElement.scrollWidth > window.innerWidth')
        print(f'\n=== {theme or "default"} · width {w}: script errors {errs}, icons {icons[1]}/{icons[0]} (empty {icons[2]}), page scrolls sideways: {hscroll}')
        fails += bool(errs) + (icons[0] != icons[1]) + icons[2] + hscroll
        pg.add_script_tag(url=AXE)
        for ts in ('1', '1.5', '2'):
            pg.evaluate(f"document.documentElement.style.setProperty('--ts','{ts}')"); pg.wait_for_timeout(250)
            ax = pg.evaluate("""async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag2aaa','wcag21aa','wcag22aa','best-practice']}});
                 return r.violations.map(v=>v.id+' x'+v.nodes.length+': '+v.nodes.slice(0,3).map(n=>n.target.join(' ')).join(' | '))}""")
            m = pg.evaluate(MEASURE)
            bad = len(ax) + len(m['lowText']) + len(m['overflow']) + len(m['smallTargets'])
            fails += bad
            print(f'  text {int(float(ts)*100)}%: axe {len(ax)} · text<7:1 {len(m["lowText"])} · targets<48 {len(m["smallTargets"])} · overflow {len(m["overflow"])}')
            for a in ax: print('     axe:', a[:220])
            for t in m['lowText'][:8]: print('     low text:', t)
            for t in m['smallTargets'][:12]: print('     small target:', t)
            for t in m['overflow'][:12]: print('     overflow:', t)
            if w == 1280:
                for sid in ('screens', 'components'):
                    if pg.locator('#' + sid).count(): pg.locator('#' + sid).screenshot(path=str(SHOTS / f'{sid}_ts{ts}.png'))
                if PAGE.name != 'index.html': pg.screenshot(path=str(SHOTS / f'{PAGE.stem}_ts{ts}.png'), full_page=True)
        pg.close()
    b.close()
print('\nRESULT:', 'PASS' if not fails else f'{fails} problem(s)')
sys.exit(1 if fails else 0)

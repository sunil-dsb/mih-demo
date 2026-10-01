"""Check the Version 2 screens (screens/v2/*.html), each at its own design size.
   Contrast uses the WCAG AAA rule: 7:1 for normal text, 4.5:1 for large text (24px+, or 18.66px+ bold).
   Usage: python build/verify_v2.py            (all screens)
          python build/verify_v2.py 05-where   (one screen)"""
import sys, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent / 'screens' / 'v2'
JS = r'''()=>{
 const lum=c=>{const a=c.map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2]};
 const parse=s=>{const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(',').map(parseFloat);return {rgb:p.slice(0,3),a:p.length>3?p[3]:1}};
 const over=(top,under)=>top.rgb.map((v,i)=>v*top.a+under[i]*(1-top.a));
 const bgOf=e=>{const stack=[];let n=e;while(n&&n.nodeType==1){const cs=getComputedStyle(n);if(cs.backgroundImage&&cs.backgroundImage!='none')return null;const c=parse(cs.backgroundColor);if(c&&c.a>0){stack.push(c);if(c.a>=.999)break}n=n.parentElement}
   let base=[255,255,255];for(let i=stack.length-1;i>=0;i--)base=over(stack[i],base);return base};
 const out={low:[],small:[],targets:[],clipped:[]};
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
 while(n=w.nextNode()){const t=n.textContent.trim();if(!t)continue;const e=n.parentElement;const cs=getComputedStyle(e);if(cs.display=='none'||cs.visibility=='hidden')continue;
   const r=e.getBoundingClientRect();if(!r.width)continue;if(e.closest('[disabled],[aria-disabled=true],[data-placeholder]'))continue;
   const fs=parseFloat(cs.fontSize),fw=parseInt(cs.fontWeight)||400;const large=fs>=24||(fs>=18.66&&fw>=700);
   const fg=parse(cs.color),bg=bgOf(e);if(fg&&bg){const f=over(fg,bg);const L1=lum(f),L2=lum(bg);const ratio=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
     if(ratio<(large?4.5:7))out.low.push(t.slice(0,28)+' '+ratio.toFixed(2)+(large?' (large)':''))}
   if(fs<14)out.small.push(t.slice(0,24)+' '+fs+'px');
   if(r.right>innerWidth+1||r.left<-1)out.clipped.push(t.slice(0,24)+' off-screen');
   if(e.scrollWidth>e.clientWidth+1&&cs.overflow!='visible')out.clipped.push(t.slice(0,24)+' cut off')}
 document.querySelectorAll('a,button,[role=button],input,textarea,select,label').forEach(e=>{const r=e.getBoundingClientRect();if(!r.width)return;
   if(e.matches('input[type=checkbox],input[type=radio]')&&e.closest('label'))return;
   if(e.matches('label')&&!e.querySelector('input[type=checkbox],input[type=radio]'))return;   /* a field's caption is not a tap target */
   if(r.height<47.5||r.width<47.5)out.targets.push((e.textContent.trim().slice(0,22)||e.tagName)+' '+Math.round(r.width)+'x'+Math.round(r.height))});
 out.scrollY=Math.max(0,document.documentElement.scrollHeight-innerHeight);out.scrollX=Math.max(0,document.documentElement.scrollWidth-innerWidth);
 return out}'''
only = sys.argv[1] if len(sys.argv) > 1 else None
files = sorted(f for f in ROOT.glob('*.html') if not only or only in f.name)
problems = 0
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    for f in files:
        web = '-web-' in f.name
        pg = b.new_page(viewport={'width': 1280, 'height': 820} if web else {'width': 390, 'height': 844})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:120]))
        pg.goto(f.as_uri()); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
        r = pg.evaluate(JS)
        n = len(errs) + len(r['low']) + len(r['small']) + len(r['targets']) + len(r['clipped']) + (1 if r['scrollY'] else 0) + (1 if r['scrollX'] else 0)
        problems += n
        print(f"{f.stem}: script errors {len(errs)} · low contrast {len(r['low'])} · text under 14px {len(r['small'])} · small targets {len(r['targets'])} · clipped {len(r['clipped'])} · scrolls {r['scrollY']}px")
        for k in ('low', 'small', 'targets', 'clipped'):
            for x in r[k]: print('     ', k + ':', x)
        pg.close()
    b.close()
print('RESULT:', 'PASS' if not problems else f'{problems} problem(s)')

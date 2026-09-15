# Скриншоты сайта для клиента: мобильные срезы по секциям + десктоп.
# python src/shots.py   (нужен запущенный сервер на 8765 или заменить URL на file://)
import sys, pathlib
from playwright.sync_api import sync_playwright
from PIL import Image

URL = sys.argv[1] if len(sys.argv) > 1 else "file:///E:/astroo/index.html"
OUT = pathlib.Path(r"E:\astroo\screens"); OUT.mkdir(exist_ok=True)
NAMES = ["01-hero","02-questions","03-situations","04-inside","05-doubts","06-price","07-author","08-faq","09-final","10-footer"]

def settle(page):
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    page.add_style_tag(content=".rv{transition:none!important}")
    page.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
    page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
    page.evaluate("Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))")
    page.wait_for_timeout(600)

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    # --- mobile 390, @2x
    ctx = b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = ctx.new_page(); page.goto(URL); settle(page)
    secs = page.evaluate("[...document.querySelectorAll('main > section, footer')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.top+scrollY), Math.round(r.height)]})")
    # Chromium wraps full-page captures above 16384px, so shoot each section as its own viewport instead.
    parts = []
    for i,(top,h) in enumerate(secs):
        t0 = 0 if i == 0 else top
        hh = (top + h) - t0
        page.set_viewport_size({"width":390, "height":hh})
        page.evaluate(f"window.scrollTo(0,{t0})")
        if i == 1: page.add_style_tag(content=".hdr{position:static!important}")
        page.wait_for_timeout(250)
        f = OUT/f"{NAMES[i]}.png"; page.screenshot(path=str(f)); parts.append(Image.open(f))
    full = Image.new("RGB",(780,sum(p.height for p in parts)),(247,243,236)); y=0
    for p_ in parts: full.paste(p_,(0,y)); y+=p_.height
    full.save(OUT/"mobile-full.png"); im = full
    page.set_viewport_size({"width":390, "height":844}); page.evaluate("window.scrollTo(0,0)")
    print("mobile:", im.size, "sections:", len(secs))
    # --- modal (order form) on mobile
    page.click(".hero .js-order"); page.wait_for_timeout(500)
    page.screenshot(path=str(OUT/"11-order-form.png"))
    ctx.close()
    # --- desktop 1440
    ctx = b.new_context(viewport={"width":1440,"height":900}, device_scale_factor=1.5)
    page = ctx.new_page(); page.goto(URL); settle(page)
    page.screenshot(path=str(OUT/"desktop-hero.png"))
    page.screenshot(path=str(OUT/"desktop-full.png"), full_page=True)
    print("desktop:", Image.open(OUT/"desktop-full.png").size)
    b.close()

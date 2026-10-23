"""Build a browsable local reference from the site's public HTML and assets."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).parent
SOURCE = ROOT / "original"
MIRROR = ROOT / "mirror"
MIRROR.mkdir(exist_ok=True)

asset_link = MIRROR / "cdn"
if asset_link.is_symlink():
    asset_link.unlink()
shutil.copytree(SOURCE / "cdn", asset_link, dirs_exist_ok=True)
for css in asset_link.rglob("*.css"):
    css.write_text(css.read_text().replace("//elabuelopreferido.com/cdn/shop/", "/mirror/cdn/shop/"))
app_js = asset_link / "shop/t/8/assets/app.js"
app_js.write_text(app_js.read_text()
    .replace('"products/mentada-de-madre-1-video"', '"products/mentada-de-madre-1-video.html"')
    .replace('"pages/experiencias"', '"pages/experiencias.html"'))

for source in [SOURCE / "index.html", SOURCE / "cart.html", *SOURCE.glob("pages/*.html"), *SOURCE.glob("policies/*.html"), *SOURCE.glob("collections/*.html"), *SOURCE.glob("products/*.html")]:
    if source.stat().st_size < 10_000:
        continue
    html = source.read_text()
    html = html.replace("https://elabuelopreferido.com/cdn/shop/", "/mirror/cdn/shop/")
    html = html.replace("//elabuelopreferido.com/cdn/shop/", "/mirror/cdn/shop/")
    html = html.replace('href="/#', 'href="/mirror/index.html#')
    html = html.replace('href="/?', 'href="/mirror/index.html?')
    html = html.replace('href="/cart"', 'href="https://elabuelopreferido.com/cart"')
    def local_page_link(match):
        if '.' in match.group(2):
            return f'href="https://elabuelopreferido.com/{match.group(1)}/{match.group(2)}{match.group(3) or ""}"'
        return f'href="/mirror/{match.group(1)}/{match.group(2)}.html{match.group(3) or ""}"'
    html = re.sub(r'href="/(pages|collections|products|policies)/([^"?#]+)(#[^"]*)?"', local_page_link, html)
    # Preserve the site's own interface scripts while omitting Shopify payment,
    # captcha and analytics code that cannot work from localhost.
    def keep_site_script(match):
        script = match.group(0)
        if any(token in script for token in (
            '/mirror/cdn/shop/t/8/assets/theme.js',
            '/mirror/cdn/shop/t/8/assets/app.js',
            'window.ABUELO_T=',
            "KEY='abuelo_popup_v1'",
        )):
            return script
        return ''
    html = re.sub(r'<script\b[^>]*>.*?</script\s*>', keep_site_script, html, flags=re.I | re.S)
    html = re.sub(r'<iframe\b[^>]*>.*?</iframe\s*>', '', html, flags=re.I | re.S)
    html = html.replace('</head>', '<link rel="icon" href="/mirror/cdn/shop/t/8/assets/marca-original.png"><script>window.Shopify={routes:{root:"/mirror/"}};</script></head>')
    if source == SOURCE / 'index.html':
        html = html.replace('aria-label="Ver carrito y checkout"', 'aria-label="Ver carrito"', 1)
        html = html.replace('</head>', '<link rel="stylesheet" href="/mirror/gorras-layout.css?v=10"><link rel="stylesheet" href="/mirror/gorras-quick-view.css?v=11"><link rel="stylesheet" href="/mirror/watch-presentation.css?v=1"><link rel="stylesheet" href="/mirror/closing-sticker.css"></head>')
        html = html.replace('<script src="/mirror/cdn/shop/t/8/assets/app.js', '<script src="/mirror/gorras-layout.js?v=10" defer></script><script src="/mirror/gorras-quick-view.js?v=11" defer></script><script src="/mirror/cdn/shop/t/8/assets/app.js')
        html = html.replace(
            '<div class="carousel-controls"><span class="carousel-counter" aria-live="polite">1 / 9</span></div>',
            '<button class="watch-prev watch-arrow" type="button" aria-label="Foto anterior de reloj"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg></button>'
            '<button class="watch-next watch-arrow" type="button" aria-label="Foto siguiente de reloj"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg></button>'
            '<div class="carousel-controls"><span class="carousel-counter" aria-live="off">1 / 9</span><button class="watch-toggle" type="button" aria-label="Pausar presentación">PAUSAR</button></div>',
            1,
        )
        html = html.replace('</body>', '<script src="/mirror/watch-presentation.js?v=1" defer></script></body>')
        html = html.replace('function open(thanks){', "function shopping(){var hats=document.getElementById('gorras'), rect=hats&&hats.getBoundingClientRect();return location.hash==='#gorras'||!!(rect&&rect.top<innerHeight*.8&&rect.bottom>innerHeight*.2)||!!document.getElementById('hat-quick-view')?.open||!!(document.getElementById('hat-cart-drawer')&&!document.getElementById('hat-cart-drawer').hidden)}\n  function open(thanks){\n    if(!thanks&&shopping()) return;", 1)
        html = html.replace('<section class="closing">', '<section class="closing" id="cierre">', 1)
        html = re.sub(
            r'<div class="closing-brand">.*?</div><p class="eyebrow">EL ABUELO PREFERIDO</p>',
            '<div class="closing-brand closing-brand-sticker"><img src="/mirror/abuelo-sticker.png" width="1116" height="1268" alt="El Abuelo Preferido, ilustración con puro y logotipo" loading="lazy" decoding="async"></div>',
            html,
            count=1,
            flags=re.S,
        )
    if source == SOURCE / 'cart.html':
        html = html.replace('href="/mirror/collections/gorras.html">VER GORRAS', 'href="/mirror/index.html#gorras">VER GORRAS', 1)
    if source == SOURCE / 'pages/marcas.html':
        html = re.sub(r'<main class="wrap legal">.*?</main>', (ROOT / 'brand-content.html').read_text().strip(), html, count=1, flags=re.S)
        html = html.replace('</head>', '<link rel="stylesheet" href="/mirror/brand-page.css?v=1"></head>')
    target = MIRROR / source.relative_to(SOURCE)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)

print(f"Mirror ready: {MIRROR}")

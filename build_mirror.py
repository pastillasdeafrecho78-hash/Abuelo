"""Build a browsable local reference from the site's public HTML and assets."""
from pathlib import Path
import html as html_utils
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

pages = [SOURCE / "index.html", SOURCE / "cart.html", *SOURCE.glob("pages/*.html"), *SOURCE.glob("policies/*.html"), *SOURCE.glob("collections/*.html"), *SOURCE.glob("products/*.html")]

def translated_brand_content(page_html):
    match = re.search(r'<main class="wrap legal"><h1>(.*?)</h1><p>(.*?)</p></main>', page_html, flags=re.S)
    if not match:
        raise ValueError("Translated brand page has an unexpected structure")
    heading = html_utils.escape(html_utils.unescape(re.sub(r'<[^>]+>', '', match.group(1))))
    lines = [html_utils.escape(html_utils.unescape(re.sub(r'<[^>]+>', '', part)).strip()) for part in re.split(r'<br\s*/?>', match.group(2))]
    if len(lines) < 3:
        raise ValueError("Translated brand page is missing its message")
    offer = lines[1][:1] + lines[1][1:].lower()
    return f'''<main class="brand-page">
  <section class="brand-hero" aria-labelledby="brand-title">
    <div class="brand-copy">
      <h1 id="brand-title">{heading}</h1>
      <p class="brand-lead">{lines[0]}</p>
      <p class="brand-offer">{offer}</p>
      <div class="brand-action">
        <p>{lines[2]}</p>
        <a href="https://www.instagram.com/elabuelopreferido/" target="_blank" rel="noopener noreferrer" aria-label="Instagram: El Abuelo Preferido">
          INSTAGRAM
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>
        </a>
      </div>
    </div>
  </section>
</main>'''

for language in ("", "en", "pt", "fr", "it", "de", "nl", "ja", "zh", "ko"):
  for original_page in pages:
    relative = original_page.relative_to(SOURCE)
    source = original_page if not language else SOURCE / "locales" / language / relative
    if not source.exists():
        continue
    if source.stat().st_size < 10_000:
        continue
    site_prefix = f"/{language}" if language else ""
    mirror_root = f"/mirror/{language}/" if language else "/mirror/"
    html = source.read_text()
    html = html.replace("https://elabuelopreferido.com/cdn/shop/", "/mirror/cdn/shop/")
    html = html.replace("//elabuelopreferido.com/cdn/shop/", "/mirror/cdn/shop/")
    html = html.replace(f'href="{site_prefix}/#', f'href="{mirror_root}index.html#')
    html = html.replace(f'href="{site_prefix}/?', f'href="{mirror_root}index.html?')
    html = html.replace(f'href="{site_prefix}/cart"', f'href="https://elabuelopreferido.com{site_prefix}/cart"')
    html = html.replace(f'action="{site_prefix}/cart/add"', f'action="https://elabuelopreferido.com{site_prefix}/cart/add"')
    html = html.replace(f'action="{site_prefix}/localization"', 'action=""')
    html = html.replace('class="lang-select" name="language_code" onchange="this.form.submit()"', 'class="lang-select" name="language_code"')
    fallback_links = ' '.join(
        f'<a href="/mirror/{prefix + "/" if prefix else ""}{relative.as_posix()}">{label}</a>'
        for prefix, label in (("", "Español"), ("en", "English"), ("pt", "Português"), ("fr", "Français"), ("it", "Italiano"), ("de", "Deutsch"), ("nl", "Nederlands"), ("ja", "日本語"), ("zh", "简体中文"), ("ko", "한국어"))
    )
    html = re.sub(r'<noscript><button type="submit" class="lang-submit">[^<]+</button></noscript>', f'<noscript><nav aria-label="Languages">{fallback_links}</nav></noscript>', html)
    def local_page_link(match):
        if '.' in match.group(2):
            return f'href="https://elabuelopreferido.com/{match.group(1)}/{match.group(2)}{match.group(3) or ""}"'
        return f'href="{mirror_root}{match.group(1)}/{match.group(2)}.html{match.group(3) or ""}"'
    html = re.sub(rf'href="{site_prefix}/(pages|collections|products|policies)/([^"?#]+)(#[^"]*)?"', local_page_link, html)
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
    html = html.replace('</head>', f'<link rel="icon" href="/mirror/cdn/shop/t/8/assets/marca-original.png"><link rel="stylesheet" href="/mirror/locale-fonts.css?v=3"><script>window.Shopify={{routes:{{root:"{mirror_root}"}}}};</script></head>')
    if relative == Path('index.html'):
        html = html.replace('aria-label="Ver carrito y checkout"', 'aria-label="Ver carrito"', 1)
        html = html.replace('</head>', '<link rel="stylesheet" href="/mirror/gorras-layout.css?v=10"><link rel="stylesheet" href="/mirror/gorras-quick-view.css?v=11"><link rel="stylesheet" href="/mirror/watch-presentation.css?v=1"><link rel="stylesheet" href="/mirror/closing-sticker.css"></head>')
        html = html.replace('<script src="/mirror/cdn/shop/t/8/assets/app.js', '<script src="/mirror/gorras-layout.js?v=11" defer></script><script src="/mirror/hat-ui-i18n.js?v=1" defer></script><script src="/mirror/gorras-quick-view.js?v=12" defer></script><script src="/mirror/cdn/shop/t/8/assets/app.js')
        html = html.replace(
            '<div class="carousel-controls"><span class="carousel-counter" aria-live="polite">1 / 9</span></div>',
            '<button class="watch-prev watch-arrow" type="button" aria-label="Foto anterior de reloj"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg></button>'
            '<button class="watch-next watch-arrow" type="button" aria-label="Foto siguiente de reloj"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg></button>'
            '<div class="carousel-controls"><span class="carousel-counter" aria-live="off">1 / 9</span><button class="watch-toggle" type="button" aria-label="Pausar presentación">PAUSAR</button></div>',
            1,
        )
        html = html.replace('</body>', '<script src="/mirror/watch-presentation.js?v=2" defer></script></body>')
        html = html.replace('function open(thanks){', "function shopping(){var hats=document.getElementById('gorras'), rect=hats&&hats.getBoundingClientRect();return location.hash==='#gorras'||!!(rect&&rect.top<innerHeight*.8&&rect.bottom>innerHeight*.2)||!!document.getElementById('hat-quick-view')?.open||!!(document.getElementById('hat-cart-drawer')&&!document.getElementById('hat-cart-drawer').hidden)}\n  function open(thanks){\n    if(!thanks&&shopping()) return;", 1)
        html = html.replace('<section class="closing">', '<section class="closing" id="cierre">', 1)
        html = re.sub(
            r'<div class="closing-brand">.*?</div><p class="eyebrow">EL ABUELO PREFERIDO</p>',
            '<div class="closing-brand closing-brand-sticker"><img src="/mirror/abuelo-sticker.png" width="1116" height="1268" alt="El Abuelo Preferido, ilustración con puro y logotipo" loading="lazy" decoding="async"></div>',
            html,
            count=1,
            flags=re.S,
        )
    if relative == Path('cart.html'):
        html = html.replace(f'href="{mirror_root}collections/gorras.html">VER GORRAS', f'href="{mirror_root}index.html#gorras">VER GORRAS', 1)
    if relative == Path('pages/marcas.html'):
        brand_content = translated_brand_content(html) if language else (ROOT / 'brand-content.html').read_text().strip()
        html = re.sub(r'<main class="wrap legal">.*?</main>', brand_content, html, count=1, flags=re.S)
        html = html.replace('</head>', '<link rel="stylesheet" href="/mirror/brand-page.css?v=2"></head>')
    html = html.replace('</head>', '<link rel="stylesheet" href="/mirror/mobile-carousel.css?v=1"></head>')
    html = html.replace('</body>', '<script src="/mirror/language-switcher.js?v=2" defer></script></body>')
    target = MIRROR / language / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)

print(f"Mirror ready: {MIRROR}")

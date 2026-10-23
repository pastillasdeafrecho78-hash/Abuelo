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

# Keep product/form identifiers intact: only translate rendered copy and metadata.
CJK_SHOW_NAMES = {
    'ja': ('深夜トークショー', 'ABUELOの深夜トークショー', '毒舌動画', 'カスタム毒舌動画', '動画1本'),
    'zh': ('深夜脱口秀', 'ABUELO深夜脱口秀', '毒舌视频', '定制毒舌视频', '1条视频'),
    'ko': ('심야 토크쇼', 'ABUELO 심야 토크쇼', '독설 영상', '맞춤형 독설 영상', '영상 1개'),
}

CJK_REMAINING = {
    'ja': {
        'home_title': 'El Abuelo Preferido | キャップ、体験、粋な生き方',
        'collection_title': 'キャップ — El Abuelo Preferido',
        'experience': 'タパルパ体験',
        'established': '1995年創業 EL ABUELO PREFERIDO',
        'languages': '言語',
        'sticker': '葉巻を持つEl Abuelo Preferidoのイラストとロゴ',
        'watch_controls': ('前の時計画像', '次の時計画像', '一時停止'),
        'hat_views': ('正面', '内側', '側面', '背面'),
        'green_description': 'El Abuelo PreferidoのGorra verdeを予約販売中 · 刺繍入り · 総額$899 MXN、または$200 MXNで予約 · メキシコ国内で45日以内にお届け',
    },
    'zh': {
        'home_title': 'El Abuelo Preferido | 棒球帽、体验与精彩生活',
        'collection_title': '棒球帽 — El Abuelo Preferido',
        'experience': '塔帕尔帕体验',
        'established': '创立于1995年 EL ABUELO PREFERIDO',
        'languages': '语言',
        'sticker': '手持雪茄的El Abuelo Preferido插画与标志',
        'watch_controls': ('上一张腕表图片', '下一张腕表图片', '暂停'),
        'hat_views': ('正面', '内侧', '侧面', '背面'),
        'green_description': 'El Abuelo Preferido的Gorra verde现已开启预售 · 刺绣款 · 总价$899 MXN，也可支付$200 MXN预订 · 墨西哥境内45天内送达',
    },
    'ko': {
        'home_title': 'El Abuelo Preferido | 모자, 체험, 제대로 사는 법',
        'collection_title': '모자 — El Abuelo Preferido',
        'experience': '타팔파 체험',
        'established': '1995년 설립 EL ABUELO PREFERIDO',
        'languages': '언어',
        'sticker': '시가를 든 El Abuelo Preferido 일러스트와 로고',
        'watch_controls': ('이전 시계 이미지', '다음 시계 이미지', '일시정지'),
        'hat_views': ('정면', '안쪽', '측면', '뒷면'),
        'green_description': 'El Abuelo Preferido의 Gorra verde 예약 판매 · 자수 디자인 · 총액 $899 MXN 또는 $200 MXN으로 예약 · 멕시코 내 45일 이내 배송',
    },
}

CJK_TERMS = {
    'ja': (
        ('販売者', 'このショップはメキシコのEl Abuelo Preferidoが運営しています。すべての価格はメキシコペソ（MXN）で表示し、該当する場合は付加価値税を含みます。'),
        ('配送', 'キャップはメキシコ全土へ配送します。'),
        ('交換と返品', 'キャップは未使用の場合、配達後30日以内に交換・返品できます。'),
        ('体験', '体験の予約には返金不可の30％の前金が必要です。残額はイベント前に全額お支払いください。体験への参加は21歳以上に限ります。'),
        ('プライバシー', '個人情報は注文の処理とご連絡のためにのみ使用します。個人情報を販売することはありません。'),
        ('お問い合わせ', 'Instagramの@elabuelopreferidoまでご連絡ください。'),
    ),
    'zh': (
        ('销售方', '本商店由位于墨西哥的 El Abuelo Preferido 运营。所有价格均以墨西哥比索（MXN）标示，并在适用时包含增值税。'),
        ('配送', '棒球帽可配送至墨西哥全境。'),
        ('换货与退货', '棒球帽未使用的情况下，可在送达后30天内申请换货或退货。'),
        ('体验', '预订体验需支付30%的不可退还定金。余款须在活动开始前全额付清。体验仅限21岁及以上人士参加。'),
        ('隐私', '我们仅使用你的个人信息处理订单并与你联系，不会出售你的个人信息。'),
        ('联系我们', '请通过 Instagram 联系 @elabuelopreferido。'),
    ),
    'ko': (
        ('판매자', '이 매장은 멕시코의 El Abuelo Preferido가 운영합니다. 모든 가격은 멕시코 페소(MXN)로 표시되며, 해당하는 경우 부가가치세가 포함됩니다.'),
        ('배송', '모자는 멕시코 전역으로 배송합니다.'),
        ('교환 및 반품', '사용하지 않은 모자는 배송 후 30일 이내에 교환하거나 반품할 수 있습니다.'),
        ('체험', '체험 예약에는 환불되지 않는 30%의 계약금이 필요합니다. 잔금은 행사 전에 전액 결제해야 합니다. 체험은 만 21세 이상만 참여할 수 있습니다.'),
        ('개인정보', '개인정보는 주문 처리와 연락에만 사용하며 판매하지 않습니다.'),
        ('문의', 'Instagram @elabuelopreferido로 문의해 주세요.'),
    ),
}

def translate_cjk_remaining(page_html, language, relative):
    copy = CJK_REMAINING[language]
    page_html = page_html.replace(
        '<title>El Abuelo Preferido | Gorras, experiencias y vivir como se debe</title>',
        f'<title>{copy["home_title"]}</title>',
    )
    page_html = page_html.replace(
        'content="El Abuelo Preferido | Gorras, experiencias y vivir como se debe"',
        f'content="{copy["home_title"]}"',
    )
    page_html = page_html.replace('<title>Gorras — El Abuelo Preferido</title>', f'<title>{copy["collection_title"]}</title>')
    page_html = page_html.replace('EXPERIENCIA TAPALPA', copy['experience'])
    page_html = page_html.replace('>EST 1995 EL ABUELO PREFERIDO<', f'>{copy["established"]}<')
    page_html = page_html.replace(
        'Gorra verde de El Abuelo Preferido en preventa · Edición bordada · Precio total $ 899 MXN o aparta con $200 MXN · Entrega en 45 días en México',
        copy['green_description'],
    )
    for source, target in zip(('vista frontal', 'vista interior', 'vista lateral', 'vista trasera'), copy['hat_views']):
        page_html = page_html.replace(source, target)
    if relative == Path('pages/terminos.html'):
        match = re.search(r'(<main class="wrap legal"><h1>.*?</h1>)(.*?)(</main>)', page_html, flags=re.S)
        if not match:
            raise ValueError(f'Missing terms content for {language}')
        translated = ''.join(f'<h2>{heading}</h2><p>{body}</p>' for heading, body in CJK_TERMS[language])
        page_html = page_html[:match.start(2)] + translated + page_html[match.end(2):]
    return page_html

def translate_cjk_show_names(page_html, language):
    late, late_full, mentada, mentada_full, one_video = CJK_SHOW_NAMES[language]
    descriptors = {
        'ja': ('パーソナライズ毒舌動画', '毒舌動画'),
        'zh': ('定制毒舌视频', '毒舌视频'),
        'ko': ('맞춤형 독설 영상', '독설 영상'),
    }
    summary_descriptor, option_descriptor = descriptors[language]
    late_statement = {
        'ja': 'EL ABUELO PREFERIDOの深夜トークショー',
        'zh': 'EL ABUELO PREFERIDO深夜脱口秀',
        'ko': 'EL ABUELO PREFERIDO 심야 토크쇼',
    }[language]
    substitutions = (
        ('LATE NIGHT WITH EL ABUELO PREFERIDO', late_statement),
        ('LATE NIGHT SHOW ABUELO', late_full),
        ('LATE NIGHT SHOW', late),
        (f'MENTADAS DE MADRE {summary_descriptor}', mentada_full),
        (f'MENTADAS DE MADRE {option_descriptor}', mentada_full),
        ('MENTADAS DE MADRE', mentada),
        ('Mentada de madre · 1 video', f'{mentada_full} · {one_video}'),
        ('Mentada de madre', mentada_full),
        ('MENTADAS', mentada),
        ('MENTADA', mentada),
    )

    def translate_text(match):
        value = match.group(2)
        for source, target in substitutions:
            value = value.replace(source, target)
        return match.group(1) + value

    page_html = re.sub(
        r'(<(?:a|summary|p|strong|option|span|h1|label|button|title)\b[^>]*>)([^<]+)',
        translate_text, page_html, flags=re.I,
    )
    # Search/social descriptions are copy too; the plural form values are untouched.
    metadata_phrases = {
        'ja': ('パーソナルなMentada de madre動画', 'パーソナルな毒舌動画'),
        'zh': ('专属定制 Mentada de madre 视频', '专属定制毒舌视频'),
        'ko': ('맞춤 Mentada de madre 영상', '맞춤 독설 영상'),
    }
    source, target = metadata_phrases[language]
    page_html = page_html.replace(source, target)
    return page_html.replace('Mentada de madre', mentada_full)

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
    if language in CJK_SHOW_NAMES:
        html = translate_cjk_show_names(html, language)
        html = translate_cjk_remaining(html, language, relative)
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
    languages_label = CJK_REMAINING[language]['languages'] if language in CJK_REMAINING else 'Languages'
    html = re.sub(r'<noscript><button type="submit" class="lang-submit">[^<]+</button></noscript>', f'<noscript><nav aria-label="{languages_label}">{fallback_links}</nav></noscript>', html)
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
    html = html.replace('</head>', f'<link rel="icon" href="/mirror/cdn/shop/t/8/assets/marca-original.png"><link rel="stylesheet" href="/mirror/locale-fonts.css?v=4"><script>window.Shopify={{routes:{{root:"{mirror_root}"}}}};</script></head>')
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
        if language in CJK_REMAINING:
            copy = CJK_REMAINING[language]
            html = html.replace('alt="El Abuelo Preferido, ilustración con puro y logotipo"', f'alt="{copy["sticker"]}"')
            previous, next_label, pause = copy['watch_controls']
            html = html.replace('aria-label="Foto anterior de reloj"', f'aria-label="{previous}"')
            html = html.replace('aria-label="Foto siguiente de reloj"', f'aria-label="{next_label}"')
            html = html.replace('aria-label="Pausar presentación">PAUSAR</button>', f'aria-label="{pause}">{pause}</button>')
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

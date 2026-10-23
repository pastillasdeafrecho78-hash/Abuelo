"""Complete the two green-cap translations blocked by Shopify's rate limiter."""
from pathlib import Path
from lxml import html
from difflib import SequenceMatcher

ROOT = Path(__file__).parent / "original"
es_reference = html.document_fromstring((ROOT / "products/gorra-azul.html").read_text())

for language in ("ja", "zh"):
    target = ROOT / "locales" / language / "products/gorra-verde.html"
    if target.exists() and target.stat().st_size > 10_000:
        continue
    es_green = html.document_fromstring((ROOT / "products/gorra-verde.html").read_text())
    reference = html.document_fromstring((ROOT / "locales" / language / "products/gorra-azul.html").read_text())
    spanish_nodes = list(es_reference.iter())
    translated_nodes = list(reference.iter())
    green_nodes = list(es_green.iter())
    if [node.tag for node in spanish_nodes] != [node.tag for node in green_nodes]:
        raise ValueError("Spanish product templates differ")
    aligned = SequenceMatcher(None, [node.tag for node in spanish_nodes], [node.tag for node in translated_nodes], autojunk=False)
    for block in aligned.get_matching_blocks():
      for offset in range(block.size):
        spanish = spanish_nodes[block.a + offset]
        translated = translated_nodes[block.b + offset]
        green = green_nodes[block.a + offset]
        if green.tag in ("script", "style"):
            if green.text == spanish.text and translated.text:
                green.text = translated.text
            continue
        if green.text == spanish.text and translated.text is not None:
            green.text = translated.text
        if green.tail == spanish.tail and translated.tail is not None:
            green.tail = translated.tail
        for attribute in ("alt", "aria-label", "placeholder", "title"):
            if green.get(attribute) == spanish.get(attribute) and translated.get(attribute) is not None:
                green.set(attribute, translated.get(attribute))
        for attribute in ("href", "action", "value"):
            value = green.get(attribute)
            if value and value.startswith("/") and not value.startswith("//"):
                green.set(attribute, f"/{language}{value}")

    root = es_green.getroottree().getroot()
    root.set("lang", language)
    for option in root.xpath('//select[@name="language_code"]/option'):
        option.attrib.pop("selected", None)
        if option.get("value") == ("zh-CN" if language == "zh" else "ja"):
            option.set("selected", "")
    canonical = root.xpath('//link[@rel="canonical"]')
    if canonical:
        canonical[0].set("href", f"https://elabuelopreferido.com/{language}/products/gorra-verde")
    page = html.tostring(root, encoding="unicode", doctype="<!doctype html>")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page)
    print(f"Completed {language}: products/gorra-verde.html")

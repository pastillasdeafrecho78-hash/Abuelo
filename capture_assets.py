from pathlib import Path
from urllib.parse import urljoin, urlsplit
from lxml import html
import subprocess
import time

ROOT = Path(__file__).parent / "original"
ORIGIN = "https://elabuelopreferido.com/"
HEADERS = [
    "-A", "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "-H", "Accept-Language: es-MX,es;q=0.9",
]

urls = {}
for page in ROOT.rglob("*.html"):
    if page.stat().st_size < 10_000:
        continue
    tree = html.parse(str(page))
    for element in tree.xpath("//*[@src or @href or @poster]"):
        for attribute in ("src", "href", "poster"):
            raw = element.get(attribute)
            if not raw:
                continue
            url = urljoin(ORIGIN, raw)
            parsed = urlsplit(url)
            if parsed.hostname == "elabuelopreferido.com" and parsed.path.startswith("/cdn/shop/"):
                urls[parsed.path] = url

for index, (path, url) in enumerate(sorted(urls.items()), 1):
    target = ROOT / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 100:
        continue
    for attempt in range(3):
        result = subprocess.run(
            ["curl", "-L", "-sS", "--max-time", "25", *HEADERS,
             "-o", str(target), "-w", "%{http_code}", url],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and result.stdout == "200" and target.stat().st_size > 100:
            print(f"{index}/{len(urls)} OK {path} {target.stat().st_size}", flush=True)
            break
        print(f"{index}/{len(urls)} {result.stdout or result.stderr.strip()} {path}", flush=True)
        time.sleep(1 + attempt)
    time.sleep(0.15)

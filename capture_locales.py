"""Capture Shopify's published translations for the static proposal."""
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).parent
SOURCE = ROOT / "original"
LANGUAGES = ("en", "pt", "fr", "it", "de", "nl", "ja", "zh", "ko")
PAGES = [Path("index.html"), Path("cart.html"), *sorted(p.relative_to(SOURCE) for p in (SOURCE / "pages").glob("*.html")),
         *sorted(p.relative_to(SOURCE) for p in (SOURCE / "policies").glob("*.html")),
         *sorted(p.relative_to(SOURCE) for p in (SOURCE / "collections").glob("*.html")),
         *sorted(p.relative_to(SOURCE) for p in (SOURCE / "products").glob("*.html"))]

missing = []
for language in LANGUAGES:
    for page in PAGES:
        target = SOURCE / "locales" / language / page
        if target.exists() and target.stat().st_size > 10_000:
            continue
        route = "" if page == Path("index.html") else "/" + str(page.with_suffix(""))
        url = f"https://elabuelopreferido.com/{language}{route}"
        target.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(5):
            result = subprocess.run([
                "curl", "-LsS", "--max-time", "12", "-w", "%{http_code}",
                "-A", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "-H", "Accept: text/html,application/xhtml+xml", "-H", f"Accept-Language: {language}",
                url, "-o", str(target),
            ], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout == "200" and target.exists() and target.stat().st_size > 10_000:
                target.write_text("\n".join(line.rstrip() for line in target.read_text().splitlines()) + "\n")
                print(f"{language}: {page}", flush=True)
                break
            target.unlink(missing_ok=True)
            time.sleep(1 + attempt)
        else:
            missing.append(url)
            print(f"MISSING: {url}", flush=True)
        time.sleep(0.4)

if missing:
    raise SystemExit("Could not capture:\n" + "\n".join(missing))

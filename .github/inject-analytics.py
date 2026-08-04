from pathlib import Path
import re

TAG_ID = "G-0VD5J6LFVD"
SNIPPET = f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={TAG_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{TAG_ID}');
</script>"""

site = Path("_site")
updated = 0
skipped = 0

for path in site.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    if TAG_ID in text:
        continue
    new_text, count = re.subn(
        r"(<head\b[^>]*>)",
        lambda match: match.group(1) + "\n" + SNIPPET,
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count:
        path.write_text(new_text, encoding="utf-8")
        updated += 1
    else:
        skipped += 1

print(f"Google Analytics added to {updated} HTML files; {skipped} files had no <head> tag.")
if updated == 0:
    raise SystemExit("No HTML files were updated.")

from pathlib import Path
from urllib.parse import urljoin, urlparse
import json
import re

BASE = "https://hamam16000-glitch.github.io/daily-calculator-hub-new/"
SITE = Path("_site")

pattern = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S
)

changed_files = 0
changed_urls = 0

def absolute_url(value, page_url):
    parsed = urlparse(value)

    if parsed.scheme in ("http", "https"):
        return value

    if parsed.scheme:
        return value

    result = urljoin(page_url, value)

    if result.endswith("/index.html"):
        result = result[:-10]

    return result

def fix_breadcrumb(data, page_url):
    global changed_urls
    changed = False

    if isinstance(data, dict):
        if data.get("@type") == "BreadcrumbList":
            elements = data.get("itemListElement", [])

            if isinstance(elements, list):
                for element in elements:
                    if not isinstance(element, dict):
                        continue

                    item = element.get("item")

                    if isinstance(item, str):
                        fixed = absolute_url(item, page_url)
                        if fixed != item:
                            element["item"] = fixed
                            changed = True
                            changed_urls += 1

                    elif isinstance(item, dict) and isinstance(item.get("@id"), str):
                        old = item["@id"]
                        fixed = absolute_url(old, page_url)
                        if fixed != old:
                            item["@id"] = fixed
                            changed = True
                            changed_urls += 1

        for value in data.values():
            if fix_breadcrumb(value, page_url):
                changed = True

    elif isinstance(data, list):
        for value in data:
            if fix_breadcrumb(value, page_url):
                changed = True

    return changed

for html_file in SITE.rglob("*.html"):
    relative = html_file.relative_to(SITE).as_posix()

    if relative == "index.html":
        page_url = BASE
    else:
        page_url = urljoin(BASE, relative)

    html = html_file.read_text(encoding="utf-8", errors="ignore")
    file_changed = False

    def replace_script(match):
        nonlocal_marker = {"changed": False}

        try:
            data = json.loads(match.group(2).strip())
        except Exception:
            return match.group(0)

        if not fix_breadcrumb(data, page_url):
            return match.group(0)

        nonlocal_marker["changed"] = True
        return (
            match.group(1)
            + "\n"
            + json.dumps(data, ensure_ascii=False, indent=2)
            + "\n"
            + match.group(3)
        )

    new_html = pattern.sub(replace_script, html)

    if new_html != html:
        html_file.write_text(new_html, encoding="utf-8")
        changed_files += 1

print(f"Fixed {changed_urls} breadcrumb URLs in {changed_files} HTML files.")

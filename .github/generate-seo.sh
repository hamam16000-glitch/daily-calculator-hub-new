#!/usr/bin/env bash
set -euo pipefail

BASE="https://hamam16000-glitch.github.io/daily-calculator-hub-new"

{
  printf '%s\n' '<?xml version="1.0" encoding="UTF-8"?>'
  printf '%s\n' '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  find _site -type f -name '*.html' | sort | while IFS= read -r file; do
    rel="${file#_site/}"
    if [ "$rel" = "index.html" ]; then
      url="$BASE/"
    else
      url="$BASE/$rel"
    fi
    printf '  <url><loc>%s</loc></url>\n' "$url"
  done
  printf '%s\n' '</urlset>'
} > _site/sitemap.xml

printf 'User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n' "$BASE" > _site/robots.txt

echo "SEO files generated."

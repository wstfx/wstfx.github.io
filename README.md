# Zebang Wu — personal portfolio

A static portfolio organized around research, engineering, products, and a personal timeline.

## Build and preview

```sh
python3 tools/build_site.py
python3 tools/check_site.py
python3 -m http.server 8091 --bind 127.0.0.1
```

Open <http://127.0.0.1:8091/>. Generated HTML is committed for GitHub Pages.

Edit project copy, tags, and the timeline in `content/portfolio-v2.json`. Shared layouts live in `tools/build_site.py`; the visual system and interactions live in `assets/css/portfolio.css` and `assets/js/portfolio.js`.

See `tools/BUILD.txt` for editing notes. Work in progress is on `website-rebuild`; `main` remains the published version until the redesign is ready.

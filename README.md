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

See `tools/BUILD.txt` for editing notes. The first layout prototype is preserved on `website-rebuild` at `11bfdac`. The next exploration is on `website-story`: a continuous homepage narrative, the author’s geometric fox, and related project paths. `main` remains the published version until the redesign is ready.

The homepage narrative lives in `content/home-story.html`, with its reading stage in `assets/css/story.css` and `assets/js/story.js`. It follows a thematic Notice → Test → Build → Return route; the About page remains the chronological record. The fox is reconstructed on a 30/60-degree triangular lattice from the author’s supplied logo. Normal scrolling, direct project navigation, keyboard links, and reduced-motion preferences are supported.

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

See `tools/BUILD.txt` for editing notes. The first layout prototype is preserved on `website-rebuild` at `11bfdac`. The narrative prototype is preserved on `website-story` at `9080200`. The companion prototype is preserved on `website-companion` at `d68692d`. The current exploration is on `website-visual-system`: an agile orange fox in filled and contour forms, headline-led illustrations, and locally hosted Garet / Best Swashed typography. `main` remains the published version until the redesign is ready.

The homepage narrative lives in `content/home-story.html`, with its reading stage in `assets/css/story.css` and `assets/js/story.js`. It follows a thematic Notice → Test → Build → Return route; the About page remains the chronological record. The original mark remains in the site identity. The story uses a new expressive geometric mascot inspired by it, with five poses and five illustrated worlds. Normal scrolling, direct project navigation, keyboard links, and reduced-motion preferences are supported.

Editable vector art lives in `assets/art/fox-mascot.svg`, `story-world.svg`, and `tail-punctuation.svg`. The builder inlines it for part-level animation. Ambient motion pauses in inactive scenes, offscreen, and in hidden tabs; the reader’s pause preference is remembered. CSS and JavaScript URLs carry content hashes to prevent stale styles after an update.

Review `visual-system.html` for the mascot, downloadable SVG poses, palette, type scale, and motion principles. The ten standalone assets follow `assets/art/fox-{filled,line}-{stand,sit,inspect,leap,return}.svg`; they share a 400 × 300 artboard. `fox-line-art.svg` is the combined contour pose source.

`assets/css/type-system.css` defines seven semantic text sizes and the two local font families. Source notes are in `assets/fonts/manifest.txt`; the supplied font notices are preserved. The unused desktop font formats and poster images remain local and are ignored by Git.

Scene motion follows the headline’s action: listening, comparison, crossing a threshold, and returning feedback. SVG tokens provide their own motion paths; all labels stay still. The fox retains separate head, tail, and eye pivots, so future poses can use the same animation rules.

Illustration production now starts from `illustration-briefs.html`: five project-connected scene prompts, composition alternatives, official cleanup-tool references, and a layer/motion handoff. The source is `content/illustration-briefs.json`; `illustration-prompts.txt` is generated for download. Approve one concept before replacing the current artwork.

Display text uses Garet Heavy, and Display/Title line-height is 1.4. The prologue's minimum height is capped for tall CSS viewports (including zoomed-out browsers). Story motion waits for font readiness, with a 1.2-second maximum wait; reading and links remain available. The motion control stays hidden and disabled until initialization. Run `node tools/check_story_startup.cjs` for delayed/failed-font and early-navigation coverage.

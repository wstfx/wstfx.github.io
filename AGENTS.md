# Portfolio maintenance guide

This file is the persistent handoff for future agents working on Zebang Wu's
portfolio. Keep it accurate when architecture, release steps or owner preferences
change. It records confirmed repository/session knowledge, not unverifiable facts
from an assistant's memory. Detailed asset provenance is in `tools/BUILD.txt`.

## Repository and release history

- This repository is `https://github.com/wstfx/wstfx.github.io`.
- Live website: `https://wstfx.github.io/`. The GitHub repository URL shows source,
  not the portfolio UI.
- `main` is published through GitHub Pages. Generated HTML is committed; there is
  no frontend package install or server-side build requirement.
- The owner approved publishing this redesign and subsequent website updates to
  this repository in this chat. Follow the current task's scope and permissions.
- Preserve `archive/legacy-site-2026-10-12` at `ec23787`: the complete previous
  published website. Do not rewrite, delete or repurpose it.
- Keep the historical design branches, including `website-art-direction-v2`,
  `website-rebuild`, `website-story`, `website-companion`, `website-visual-system`,
  `website-fox-artwork`, and `website-chapter-scenes`.
- Redesign release merge: `baecf01`; invitation links/footer: `31c1478`.
  Use Git history to recover older work rather than copying the old site over main.

## Source map: edit inputs, then regenerate

| Change | Source |
| --- | --- |
| Project facts, summaries, tags, timeline | `content/portfolio-v2.json` |
| Shared HTML, navigation, footer, CV, page composition | `tools/build_site.py` |
| Home narrative | `content/home-story.html` |
| Case-study narrative | `content/<project>-body.html` |
| About introduction and portrait captions | `content/about-intro.html`, `content/about-portraits.json` |
| About layout, carousel, year navigation | `assets/css/about.css`, `assets/js/about.js` |
| CV printing | `assets/css/cv.css` |
| Shared styles/interactions | `assets/css/portfolio.css`, `assets/js/portfolio.js` |
| Typography | `assets/css/type-system.css`, font provenance under `assets/fonts/` |
| Homepage reading stage and motion | `assets/css/story.css`, `assets/js/story.js` |
| Access questions and invitation link | `assets/js/privacy-gate.js`, `assets/css/privacy-gate.css` |
| Fire house illustration | `tools/build_fire_art.py` → `assets/art/fire-sim-house.svg` |

Do not make durable content changes only in generated HTML. Shared SVG artwork is
often inlined into both Work cards and detail pages; rebuild both consumers. Use
`asset(...)` for changed CSS/JS references so content hashes invalidate caches.

## Build and validate

Run commands from this repository root:

```sh
python3 tools/build_site.py
python3 tools/check_site.py
git diff --check
```

For a scoped content/art edit, use e.g.:

```sh
python3 tools/build_fire_art.py
python3 tools/build_site.py --only work/fire-sim.html work.html
```

Changes to shared templates or the access gate need a full build so every page
references the latest asset version. Rebuilding without input changes should
leave generated output unchanged.

Run the checks relevant to changed behavior:

```sh
node tools/check_privacy_gate.cjs
node tools/check_story_startup.cjs
node tools/check_test_journey.cjs
node tools/check_dhh_motion.cjs
node --check assets/js/privacy-gate.js
```

Use `python3 -m http.server 8091 --bind 127.0.0.1` for local preview. Verify actual
rendering for layout changes, including desktop and narrow screens. A passing
link checker alone does not prove visual quality or interaction correctness.

`tools/check_site.py` checks local links, filename case, anchors, image alt text,
and Yuanti font coverage/hashes. After adding Chinese text, run the font check;
regenerate subsets with `tools/prepare_yuanti_fonts.py` only if required and the
original font is available. Preserve font notices; conversion does not establish
a new font license.

## Access gate: friendly matching, not strong authentication

- The owner wants friends to get through with informal answers such as `Zebang`
  and `Westlake`, plus common nicknames, Chinese variants and school abbreviations.
- Normalize case, whitespace, punctuation, full-width text and Latin diacritics.
  Longer Latin aliases allow one insertion, deletion, substitution or adjacent
  letter swap. Short aliases and Chinese names must match an explicit alias;
  do not accept arbitrary substrings, empty values, or unrelated answers.
- Match ordinary aliases without Web Crypto. Older versions already included
  hashes for `Zebang` and `Westlake`; a reported rejection does not establish a
  missing alias. Check webview API availability, the actual submit handler, fresh
  browser state and cached JS before claiming a root cause.
- Access uses `zebang-portfolio-access-v1` in localStorage and expires in 30 days.
  Storage may throw or be blocked: allow the current page to open after a valid
  answer even if remembering it fails. Do not promise cross-page persistence in
  that case. Fresh-profile tests must not accidentally reuse existing access.
- Invitations use `#invite=<43-character random base64url code>` on any generated
  page. The published code contains only its SHA-256 digest. Validate the token
  exactly, remove it via `history.replaceState`, preserve path/query and ordinary
  section anchors, and fall back to questions on invalid tokens or crypto failure.
- The owner's invitation URL is kept outside this repository at
  `../website-planning/portfolio-invitation-link.txt`. Never commit or print that
  URL in public documentation, test fixtures or logs. Tests may read the local
  file optionally, or use an isolated test token without changing production.
- Changing the invitation digest prevents future use of the previous link;
  it does not revoke access already remembered in browsers. Anyone who has the
  link can forward it. All content is still served as static public files.
- Preserve the existing invitation when adjusting question matching unless the
  owner asks to rotate it. No server, analytics or transmission of answers is
  needed for this feature.

## Design, content and interaction lessons

- The owner prefers a warm, thoughtful portfolio with an agile fox identity,
  elegant motion and authentic work evidence. Avoid generic portfolio filler,
  invented credentials, invented outcomes or images presented as real evidence.
- Current footer: “May good things reach people with grace and quiet agility.”
  This replaced “A curious mind. A fox at heart.” at the owner's request.
- Home follows Notice → Test → Build → Return; About carries chronology.
  Only Work projects and Westlake/Cornell get detail pages. Other experience URLs
  redirect to their corresponding About timeline anchors; keep old links usable.
- Keep claim scope precise: a prototype, conceptual illustration, team study,
  planned experiment and validated result are different things. Publication
  authorship/status must come from confirmed sources, not elapsed time.
- Use native SVG/CSS for the established vector system. Keep static placement
  transforms on wrappers separate from animated inner groups. Preserve original
  source artwork. Avoid changing the visual system during unrelated fixes.
- Fire architecture is generated from a shared orthographic projection; do not
  nudge individual vertices. Its flame uses asymmetric layered gradients and
  independently moving tongues, approved by the owner on 2026-10-12.
- Keep animations pausable, honor reduced motion, and pause offscreen/in hidden
  tabs. Homepage font readiness has a 1.2-second cap; reading/navigation must work
  before motion is ready. Do not add page-wide loading delays.
- About has five portraits, dates/places in JSON, and 7-second autoplay. Manual
  navigation pauses until Play; hover/focus, offscreen and hidden tabs pause too.
  Preserve native image proportions, mobile swipes and keyboard operation.
- Original HEIC portraits stay local/ignored. Published WebP copies omit embedded
  EXIF/GPS. Paris's November 2024 date was owner-confirmed; three 2025 photos have
  conflicting EXIF/GPS clock times, so show dates only. Do not invent exact times.
- CV printing uses A4 and compact styles after the typography stylesheet; show
  the real email in print, keep entries together but allow sections to split.

## Publishing and verification

1. Inspect `git status`, current branch and diffs; preserve unrelated local work.
2. Fetch origin before integration, review unexpected upstream changes, and avoid
   force pushes. Stage only the task's intended files.
3. Build and run relevant checks; commit source plus generated output. Check that
   the private invitation URL and ignored originals are absent from the commit.
4. When publishing is authorized, push the intended branch to the verified origin.
   Do not bundle unrelated development branch exports into a release push.
5. Confirm GitHub's `pages build and deployment` run succeeded for the new commit.
   Compare live `https://wstfx.github.io/` and any changed assets/pages to local
   files; a successful Git push alone does not confirm Pages has updated.
6. For UI changes, inspect the live result and provide its link. Report whether
   changes are local, pushed or verified live accurately.

Private application materials, collection notes, raw photos and the invitation
URL belong outside the published repository. Documentation in this repository
is public. Keep these instructions focused on maintenance, without adding
unnecessary approval rituals or storing private conversation transcripts.

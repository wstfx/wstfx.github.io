"""Build the portfolio from content/portfolio-v2.json. Python standard library only."""
import json
import hashlib
import math
import re
from pathlib import Path
from html import escape as esc
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'content/portfolio-v2.json').read_text())
PROJECTS = DATA['projects']
BY_ID = {p['id']: p for p in PROJECTS}
STORY_THREADS = {
    'dhh': ('notice', 'Notice · Start with someone'),
    'dhh-review': ('notice', 'Notice · Start with someone'),
    'feasypaste': ('notice', 'Notice · Start with someone'),
    'active-learning': ('test', 'Test · Give curiosity something to push against'),
    'reconstruction': ('test', 'Test · Give curiosity something to push against'),
    'crystal': ('test', 'Test · Give curiosity something to push against'),
    'materials-creep': ('test', 'Test · Give curiosity something to push against'),
    'involve': ('build', 'Build · Let the world push back'),
    'dongfeng': ('build', 'Build · Let the world push back'),
    'asr': ('build', 'Build · Let the world push back'),
    'igem': ('build', 'Build · Let the world push back'),
    'ai-coding-course': ('return', 'Return · Bring it back to people'),
    'fire-sim': ('return', 'Return · Bring it back to people'),
    'navix': ('return', 'Return · Bring it back to people'),
    'vr': ('return', 'Return · Bring it back to people'),
    'roadlaw': ('return', 'Return · Bring it back to people'),
}
RELATED_NEXT = {
    'fire-sim': 'reconstruction', 'involve': 'ai-coding-course',
    'dongfeng': 'involve', 'reconstruction': 'active-learning',
    'active-learning': 'reconstruction', 'dhh': 'dhh-review',
    'dhh-review': 'dhh', 'navix': 'involve', 'vr': 'fire-sim',
    'ai-coding-course': 'vr', 'feasypaste': 'roadlaw', 'roadlaw': 'involve',
    'igem': 'feasypaste', 'crystal': 'materials-creep', 'materials-creep': 'fire-sim',
    'asr': 'dongfeng', 'evisa': 'feasypaste', 'westlake': 'cornell',
    'cornell': 'vr', 'culture': 'student-union', 'student-union': 'ambassador',
    'ambassador': 'culture', 'writing': 'website', 'website': 'involve',
}


def e(value):
    return esc(str(value), quote=True)


def tags(values, limit=None):
    return '<div class="tags">' + ''.join(f'<span class="tag">{e(v)}</span>' for v in values[:limit]) + '</div>'


def eyebrow(text):
    return f'<p class="eyebrow">{e(text)}</p>'


def asset(path):
    """Changed assets receive fresh URLs; unchanged builds keep the same URLs."""
    version = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:10]
    return f'{path}?v={version}'


def page(path, title, body, active, prefix=''):
    story_assets = f'<link rel="stylesheet" href="{asset("assets/css/story.css")}"><script defer src="{asset("assets/js/story.js")}"></script>' if path == 'index.html' else ''
    if path == 'visual-system.html':
        story_assets = f'<link rel="stylesheet" href="{asset("assets/css/visual-system.css")}">'
    if path == 'illustration-briefs.html':
        story_assets = f'<link rel="stylesheet" href="{asset("assets/css/illustration-briefs.css")}"><script defer src="{asset("assets/js/illustration-briefs.js")}"></script>'
    links = [('Home', 'index.html'), ('Work', 'work.html'), ('About', 'about.html'), ('Writing', 'writing.html'), ('CV', 'cv.html')]
    nav = ''.join(f'<a href="{prefix}{href}"' + (' aria-current="page"' if label == active else '') + f'>{label}</a>' for label, href in links)
    html = f'''<!doctype html>
<html lang="en" class="privacy-locked">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#234d3b">
<meta name="description" content="Zebang Wu — research, engineering, interactive products, and the things I’m curious about.">
<title>{e(title)} · Zebang Wu</title>
<link rel="icon" type="image/svg+xml" href="{prefix}assets/art/geometric-mark.svg">
<link rel="stylesheet" href="{prefix}assets/css/privacy-gate.css">
<link rel="stylesheet" href="{prefix}{asset('assets/css/portfolio.css')}">
<script defer src="{prefix}assets/js/privacy-gate.js"></script>
<script defer src="{prefix}{asset('assets/js/portfolio.js')}"></script>
{story_assets}
<link rel="preload" href="{prefix}assets/garet/Garet-Heavy.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{prefix}assets/garet/Garet-Book.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{prefix}assets/best_swashed/BestSwashed_PERSONAL_USE_ONLY.otf" as="font" type="font/otf" crossorigin>
<link rel="stylesheet" href="{prefix}{asset('assets/css/type-system.css')}">
</head>
<body id="top" class="{'story-page' if path == 'index.html' else 'collection-page'}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{prefix}index.html" aria-label="Zebang Wu, home"><img src="{prefix}assets/art/geometric-mark.svg" width="34" height="36" alt=""><span class="brand-name">Zebang Wu<small>ENGINEERING & A LITTLE CURIOSITY</small></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav">Menu +</button>
<nav class="main-nav" id="main-nav" aria-label="Main navigation">{nav}</nav>
</div></header>
<main class="wrap" id="main" tabindex="-1">{body}</main>
<footer class="site-footer"><div class="wrap"><div class="footer-top"><div>{eyebrow('Always curious about the next question.')}<h2>Let’s make something meaningful.</h2><p>Research, projects, and good conversations.</p></div><div class="footer-contact"><a class="text-link" href="mailto:wuzebang@westlake.edu.cn">wuzebang@westlake.edu.cn ↗</a><button class="copy-email" type="button" aria-label="Copy email address" title="Copy email address">⧉</button></div></div><div class="footer-bottom"><span>© 2026 Zebang Wu · 吴泽邦</span><span>A curious mind. A fox at heart.</span><a href="#top">Back to top ↑</a></div></div></footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<dialog class="lightbox" id="image-viewer" aria-label="Expanded project image"><div class="lightbox-head"><span>From the project archive</span><button type="button" id="close-viewer">Close ×</button></div><img id="viewer-image" alt=""><p id="viewer-caption"></p></dialog>
<noscript><div class="noscript-note"><h1>A small introduction.</h1><p>This portfolio’s existing access gate requires JavaScript. Please enable JavaScript to continue.</p><a href="mailto:wuzebang@westlake.edu.cn">Contact Zebang</a></div></noscript>
</body></html>'''
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)


def artwork(project_id, number='01'):
    label = 'An idea, in outline'
    if project_id == 'involve':
        art = '<div class="orbit-diagram"><span>Design</span><i>→</i><span>Teach</span><i>→</i><span>Assess</span></div>'
        label = 'A teaching workflow · concept diagram'
    elif project_id == 'dongfeng':
        art = '<svg class="path-art" viewBox="0 0 430 210" fill="none" aria-hidden="true"><path d="M0 168H116Q170 168 170 112V94Q170 45 225 45H440" stroke="#aec09d" stroke-width="53"/><path d="M0 168H116Q170 168 170 112V94Q170 45 225 45H440" stroke="#e9efdf" stroke-width="36"/><path d="M0 168H116Q170 168 170 112V94Q170 45 225 45H440" stroke="#879b7b" stroke-width="1.5" stroke-dasharray="8 9"/><rect x="196" y="30" width="36" height="28" rx="7" fill="#d5753d"/><circle cx="213" cy="44" r="39" stroke="#c7744280"/><circle cx="213" cy="44" r="61" stroke="#c7744233"/><path d="M57 71L66 53L76 71M331 147L340 129L350 147" stroke="#6a8663" stroke-width="2"/></svg>'
        label = 'Model → simulator → evaluation'
    elif project_id == 'reconstruction':
        cells = ''.join(f'<i style="--v:{.22 + .72 * abs(math.sin(i * .26 + (i // 12) * .32)):.3f}"></i>' for i in range(84))
        art = '<div class="field-art">' + cells + '</div>'
        label = 'Sparse observations / wider questions'
    elif project_id == 'feasypaste':
        art = '<div class="type-transfer"><span>∑</span><b>→</b><span>∑</span></div>'; label = 'Keep the meaning. Keep the formatting.'
    elif project_id == 'fire-sim':
        art = '<div class="thermal-art"><span></span></div>'; label = 'Heat / time / material response'
    elif project_id == 'navix':
        art = '<div class="care-art">❋</div>'; label = 'Technology, with care'
    elif project_id in ['dhh', 'dhh-review']:
        art = '<div class="quote-art">“ ”</div>'; label = 'Start by listening'
    elif project_id == 'vr':
        art = '<div class="vr-art"><span>t</span>↔<span>t′</span></div>'; label = 'A different frame of reference'
    else:
        symbols = {'active-learning': 'ƒ(x)', 'crystal': '◇', 'materials-creep': 'σ', 'asr': '∿', 'roadlaw': '↗', 'igem': '✳', 'evisa': '↗', 'ai-coding-course': '{ }', 'student-union': '∴', 'culture': 'Aa', 'ambassador': '↔', 'westlake': 'W', 'cornell': 'C', 'writing': '…', 'website': 'Zw'}
        art = f'<div class="symbol-art">{e(symbols.get(project_id, "✳"))}</div>'
    return f'<span class="cover-index">{number} /</span>{art}<span class="cover-caption">{label}</span>'


def card(p, index=1):
    id_ = p['id']
    return f'''<article class="project-card" data-category="{e(p['category'])}">
<a class="card-cover cover-{id_}" href="work/{id_}.html" aria-label="Explore {e(p['title'])}"><div aria-hidden="true">{artwork(id_, f'{index:02d}')}</div></a>
<div class="card-body"><div class="card-meta"><span>{e(p['category'])}</span><span>{e(p['period'])}</span></div><h3><a href="work/{id_}.html">{e(p['title'])}</a></h3><p>{e(p['summary'])}</p><div class="card-bottom">{tags(p['tags'], 2)}<a class="round-arrow" href="work/{id_}.html" aria-label="Read {e(p['title'])}">↗</a></div></div></article>'''


def section_head(kicker, title, link='', label=''):
    return f'<div class="section-head"><div>{eyebrow(kicker)}<h2>{title}</h2></div>' + (f'<a class="text-link" href="{link}">{label} ↗</a>' if link else '') + '</div>'


home = (ROOT / 'content/home-story.html').read_text()
world = (ROOT / 'assets/art/story-world.svg').read_text()
mascot = (ROOT / 'assets/art/fox-mascot.svg').read_text()
_, _, fox_width, fox_height = map(float, re.search(r'viewBox="([^"]+)"', mascot).group(1).split())
mascot = re.sub(r'<svg\b', f'<svg x="{-fox_width / 2:g}" y="{-fox_height / 2:g}" width="{fox_width:g}" height="{fox_height:g}"', mascot, count=1)
world = world.rsplit('</svg>', 1)[0] + '<g class="travelling-fox" transform="translate(300 330) scale(1)"><g class="fox-breathe">' + mascot + '</g></g></svg>'
tail = (ROOT / 'assets/art/tail-punctuation.svg').read_text()
opening_art = (ROOT / 'assets/art/fox-workbench.svg').read_text()
# Keep the supplied vector in its own coordinate system: motion pivots are
# measured against its original Illustrator artboard, not the story diagram.
opening_art = re.sub(r'<\?xml[^>]*\?>\s*', '', opening_art)
opening_art = re.sub(r'<metadata\b.*?</metadata>', '', opening_art, flags=re.S)
opening_art = re.sub(r'(?m)^[ \t]+$', '', opening_art)
home = home.replace('<!-- STORY_SCENE -->', world).replace('<!-- OPENING_ART -->', opening_art).replace('<!-- TAIL_PUNCTUATION -->', tail)
page('index.html','Home',home,'Home')

# A reviewable visual standard with reusable filled and contour assets.
visual = '<section class="visual-intro"><a class="breadcrumb" href="index.html">← Back to the story</a>'+eyebrow('Zebang Wu / Visual language / 2026')+'<h1>A little wild.<br><em>Carefully drawn.</em></h1><p class="lede">An orange fox, a clear line, and room for curiosity. A shared language for character, illustration, typography, and motion.</p></section>'
visual += '<nav class="visual-index" aria-label="Visual reference sections"><a href="#source">The supplied scene ↘</a><a href="#references">Vector references ↘</a><a href="#pose-concepts">New pose concepts ↘</a></nav>'
visual += '<section class="visual-section" id="source">'+eyebrow('01 / The supplied illustration')+'<h2>A question becomes<br><em>a road to explore.</em></h2><div class="visual-master"><figure><img src="assets/art/fox-workbench.svg" width="1298" height="1212" alt="The source fox rests a paw on a workbench; paper unfolds into a road carrying a small orange car"><figcaption>FoxHomepage_0 · supplied artwork · now on the homepage</figcaption></figure><div><h3>The character to carry forward.</h3><p>Long legs, an attentive gaze, a cream chest, and a broad, sweeping tail. Orange planes carry the fox; sage and forest green give its surroundings a quieter voice.</p><p>The paper road makes the opening invitation concrete: follow a question and see where it leads. The workbench and small car connect making with exploration.</p><div class="visual-downloads"><a href="assets/IllustratorWorkspace/FoxHomepage_0.svg" download>Original SVG ↓</a><a href="assets/IllustratorWorkspace/FoxHomepage_0.ai" download>Illustrator source ↓</a><a href="assets/art/fox-workbench.svg" download>Web SVG ↓</a></div><p class="visual-production-note">The web derivative retains every source path. Tail, eye, paper curl, car, and individual leaves have restrained motion; connected anatomy stays intact.</p></div></div></section>'
visual += '<section class="visual-section" id="references">'+eyebrow('02 / Reusable vector references')+'<h2>One silhouette.<br><em>Two voices.</em></h2><p>Extracted directly from the supplied drawing. These are reusable treatments of its original reaching pose, with shared proportions and a transparent artboard.</p><div class="visual-duet">'
for name, label in [('reaching','Color · the storyteller'),('contour','Contour · a quieter presence')]:
    src=f'assets/art/fox-reference-{name}.svg'
    visual+=f'<figure class="visual-specimen"><img src="{src}" width="600" height="500" alt="{label} fox, derived from the supplied illustration"><figcaption><span>{label}</span><a href="{src}" download>SVG ↓</a></figcaption></figure>'
visual+='</div><div class="visual-reference-details">'
for name,label in [('reaching-left','Facing left · mirrored source'),('detail','Character detail · ears, eye & muzzle')]:
    src=f'assets/art/fox-reference-{name}.svg'
    visual+=f'<figure class="visual-pose"><img src="{src}" width="600" height="500" alt="{label}" loading="lazy"><figcaption><span>{label}</span><a href="{src}" download>SVG ↓</a></figcaption></figure>'
visual+='</div><div class="visual-note"><p>Use color when the fox is the focus. Use the contour in margins and transitions, with fewer internal lines at small sizes. Keep the long-legged proportions and leave room around the tail.</p></div></section>'
visual+='<section class="visual-section" id="pose-concepts">'+eyebrow('03 / New pose concepts · for review')+'<h2>The same fox.<br><em>More things to say.</em></h2><p>Four proposed poses, generated from the supplied reference: listen, investigate, leap, and turn back. This sheet explores character consistency; these are raster concepts awaiting selection and vector cleanup.</p><figure class="visual-concept-sheet"><img src="assets/art/fox-pose-concepts-v1.png" width="1298" height="1212" alt="Four orange fox pose concepts: seated listening, investigating with a lifted paw, leaping, and seated looking back" loading="lazy"><figcaption><span>01 Listen · 02 Investigate · 03 Move · 04 Return</span><a href="assets/art/fox-pose-concepts-v1.png" download>Concept sheet ↓</a></figcaption></figure><div class="visual-rules"><article><h3>Keep the character.</h3><p>Small tapered head, tall triangular ears, forest-green legs, cream chest, and the same generous tail. A new pose should still feel like this fox.</p></article><article><h3>Choose the gesture.</h3><p>Listening for the human question; inspecting for research; movement for a working system; turning back for what someone learns from it.</p></article><article><h3>Prepare for motion.</h3><p>Choose the still image first, then clean its shapes and separate only the parts that need to move. The concept sheet is not an animation rig.</p></article></div><p class="visual-production-note">The opening scene uses the supplied artwork. The four later chapter scenes still use the previous illustration studies while their replacements are developed. <a href="content/fox-art-direction.json" download>Source notes & generation prompt ↓</a></p></section>'
visual+='<section class="visual-section">'+eyebrow('04 / The palette')+'<h2>Warm movement.<br><em>Quiet surroundings.</em></h2><div class="visual-palette">'
for name,color,light in [('Forest','#193d30',True),('Paper','#f7f5ed',False),('Fox orange','#f47b20',False),('Burnt orange','#d84b12',True),('Apricot','#ffaf6a',False),('Sage','#b7c4a5',False)]:
    visual+=f'<div class="palette-chip" style="background:{color};'+('color:#fff8ee' if light else '')+f'"><strong>{name}</strong><code>{color}</code></div>'
visual+='</div></section><section class="visual-section">'+eyebrow('05 / Seven typographic roles')+'<h2>Garet, with a little<br><em>Best Swashed.</em></h2><p>Garet Heavy gives Display its weight and a compact 1.15 line-height. Best Swashed keeps 1.4 for its tall forms, in muted green. Supporting labels stay legible; body copy gets a steady rhythm.</p>'
for role,cls,sample in [('Display','display','Follow a question.'),('Title','title','<span class="type-accent">See where it leads.</span>'),('Subheading','subhead','A question becomes a comparison.'),('Lead','lead','An invitation to follow the question.'),('Body','body','Good interfaces make complex things approachable.'),('Supporting','small','Context, captions, roles, and dates.'),('Label','label','Notice / Test / Build / Return')]:
    visual+=f'<div class="type-demo"><span>{role}</span><p class="sample-{cls}">{sample}</p></div>'
visual+='<p class="visual-font-note">The supplied font files are retained with their source notes. Best Swashed is marked “personal use only”; commercial use requires the corresponding license.</p></section>'
visual+='<section class="visual-section">'+eyebrow('06 / Illustration and motion')+'<h2>Make the idea<br><em>visible.</em></h2><div class="visual-rules"><article><h3>Start with the headline.</h3><p>Listening begins with a person. A question meets resistance. A useful thing reaches someone, and a response comes back. Every scene expresses the chapter’s central action.</p></article><article><h3>Let motion explain.</h3><p>A token follows an idea, a boundary responds, and a feedback path returns. Character gestures stay smaller than the scene’s main action.</p></article><article><h3>Leave room to read.</h3><p>Use one principal motion at a time. Keep labels still, respect reduced-motion preferences, and pause scenes when they are out of view.</p></article></div><p><a class="text-link" href="illustration-briefs.html">Open the next illustration briefs & cleanup workflow ↗</a></p><a class="button outline" href="index.html">See the language in the story ↗</a></section>'
page('visual-system.html','Visual system',visual,'')

# Art direction is reviewable before any replacement illustration is produced.
BRIEFS = json.loads((ROOT / 'content/illustration-briefs.json').read_text())
briefs = '<section class="brief-intro"><a class="breadcrumb" href="visual-system.html">← Visual standard</a>'+eyebrow('Illustration workshop / concept → clean shapes → motion')+'<h1>First the idea.<br><em>Then the movement.</em></h1><p class="lede">Choose the art before we animate it. Five concrete scenes, grounded in the work, with ready-to-copy generation prompts and a practical cleanup workflow.</p><p class="brief-meta">Art-direction briefs · not project screenshots · 2 October 2026</p></section>'
briefs += '<nav class="brief-nav" aria-label="Illustration brief sections"><a href="#workflow">Workflow</a><a href="#tools">Cleanup tools</a>'+''.join(f'<a href="#{e(s["id"])}">{e(s["chapter"])}</a>' for s in BRIEFS['scenes'])+'</nav>'
briefs += '<div class="brief-callout"><strong>First scene received · 3 October 2026</strong><p>Your FoxHomepage_0 artwork is now the homepage’s opening scene. <a href="visual-system.html#source">See the supplied source, reusable vector references, and new pose concepts ↗</a>. The briefs below remain the direction for developing the following chapters.</p></div>'
briefs += '<section class="brief-section" id="workflow">'+eyebrow('01 / One image first')+'<h2>A scene you can understand<br><em>before reading its caption.</em></h2><p>Start with the listening scene. It tests the fox’s character, human body language, and clarity together. Generate separate alternatives, choose one, and use it as the reference for the rest.</p><div class="brief-steps">'
for i,step in enumerate(BRIEFS['workflow'],1):
    briefs += f'<article><b>0{i}</b><h3>{e(step["step"])}</h3><p>{e(step["description"])}</p></article>'
briefs += '</div><div class="brief-callout"><strong>Your first handoff can be simple.</strong><p>Send the chosen image and what you like about it. A layered file is welcome, but not a prerequisite. I can assess whether vector tracing or transparent image layers will preserve it better, then organize the parts needed for animation.</p></div><details class="brief-details"><summary>The shared visual direction</summary><p>'+e(BRIEFS['style']['character'])+'</p><p>'+e(BRIEFS['style']['geometry'])+'</p><p>'+e(BRIEFS['style']['composition'])+'</p><p>'+e(BRIEFS['style']['typography'])+'</p></details></section>'
briefs += '<section class="brief-section" id="tools">'+eyebrow('02 / Cleanup, with a clear job for each tool')+'<h2>Clean edges.<br><em>Useful layers.</em></h2><p>For flat geometric art, my starting recommendation is Vectorizer.AI, followed by grouping and cleanup in a vector editor. If a selected image relies on subtle shaded planes, keep transparent raster layers instead of forcing it into vectors.</p><div class="brief-table-wrap"><table class="brief-table"><thead><tr><th scope="col">Tool</th><th scope="col">Where it helps</th><th scope="col">What remains to do</th></tr></thead><tbody>'
for name,url,job,boundary in [
    ('Vectorizer.AI','https://vectorizer.ai/','Turn the approved flat-color image into editable SVG paths; reduce the palette and inspect curve quality.','An SVG is not a character rig. Group head, tail, body, and props deliberately after conversion.'),
    ('Recraft','https://www.recraft.ai/ai-image-vectorizer','A browser alternative for converting selected raster artwork to editable SVG.','Check that vectorization preserves the chosen silhouette. Shapes still need meaningful animation groups.'),
    ('Qwen-Image-Layered','https://huggingface.co/spaces/Qwen/Qwen-Image-Layered','Try decomposing a composite image into transparent raster layers, particularly when objects overlap.','Experimental production route: layer contents are not explicitly controlled by the prompt. A whole fox may remain one layer; output is not vector artwork.'),
    ('Illustrator','https://helpx.adobe.com/ca/illustrator/desktop/manage-objects/traces-mockups-symbols/edit-image-trace-results.html','If already available: Image Trace, Expand, Ungroup, and Simplify, then organize the moving parts.','This final cleanup and grouping is deliberate editing, not automatic understanding of the scene.'),
    ('Inkscape','https://inkscape.org/learn/tutorials/','A free vector editor for tracing, simplifying paths, and organizing named SVG groups.','A useful alternative to Illustrator; it still needs judgment about silhouette, overlap, and pivots.')
]:
    briefs+=f'<tr><th scope="row"><a href="{url}">{name} ↗</a></th><td>{job}</td><td>{boundary}</td></tr>'
briefs+='</tbody></table></div><p class="brief-meta">Sources: each tool name links to its official tool or documentation. <a href="https://vectorizer.ai/pricing">Vectorizer.AI export plans</a> · <a href="https://github.com/QwenLM/Qwen-Image-Layered">Qwen layer behavior and limitations</a> · <a href="https://www.recraft.ai/vector-editor">Recraft vector editor</a>. Reviewed 2 October 2026; no artwork has been uploaded to these services.</p></section>'
for s in BRIEFS['scenes']:
    sid=e(s['id'])
    briefs+=f'<section class="brief-section" id="{sid}">{eyebrow(s["chapter"])}<h2>{e(s["heading"])}</h2><p class="lede">{e(s["concept"])}</p><p>{e(s["intent"])}</p><div class="brief-plan"><div><h3>What the viewer sees</h3><ul>'+''.join(f'<li>{e(x)}</li>' for x in s['recognizableElements'])+'</ul></div><div><h3>Grounded in the work</h3>'+''.join(f'<p><a href="work/{e(a["projectId"])}.html">{e(a["name"])} ↗</a><br>{e(a["why"])}</p>' for a in s['anchors'])+'</div></div>'
    briefs+=f'<div class="brief-prompt"><label for="prompt-{sid}">READY-TO-COPY PROMPT · ATTACH YOUR FOX REFERENCE</label><textarea id="prompt-{sid}" readonly spellcheck="false">{e(s["prompt"])}</textarea><button class="button outline brief-copy" type="button" data-copy-prompt="prompt-{sid}" hidden>Copy this prompt ↗</button><p class="brief-copy-status" role="status" aria-live="polite"></p></div>'
    briefs+='<details class="brief-details"><summary>Three compositions to explore</summary><ol>'+''.join(f'<li><strong>{e(v["name"])}</strong> — {e(v["direction"])}</li>' for v in s['variants'])+'</ol></details><div class="brief-plan"><div><h3>Movement after approval</h3><ul>'+''.join(f'<li><strong>{e(m["part"].replace("-"," "))}</strong> — {e(m["action"])}</li>' for m in s['motionTargets'])+'</ul></div><div><h3>Keep out of the image</h3><ul>'+''.join(f'<li>{e(x)}</li>' for x in s['avoid'])+'</ul></div></div><details class="brief-details"><summary>Layer handoff for production</summary><p>These are the desired final groups, not layers the image generator is expected to create automatically.</p><div class="brief-layer-list">'+''.join(f'<code>{e(x)}</code>' for x in s['layers'])+'</div><p>Preserve the full form behind overlaps, keep a shared canvas, and include a flattened reference for comparison.</p></details></section>'
briefs += '<section class="brief-section"><h2>Pick for the still.<br><em>Animate for the meaning.</em></h2><p>'+e(BRIEFS['approval']['readabilityTest'])+'</p><ul>'+''.join(f'<li>{e(x)}</li>' for x in BRIEFS['approval']['checks'])+'</ul><a class="button outline" href="illustration-prompts.txt" download>Download all five prompts ↓</a></section>'
page('illustration-briefs.html','Illustration workshop',briefs,'')
(ROOT/'illustration-prompts.txt').write_text(BRIEFS['title']+'\n\n'+BRIEFS['purpose']+'\n\n'+'\n\n'.join(s['chapter']+' / '+s['heading']+'\n\n'+s['prompt'] for s in BRIEFS['scenes']))

work_projects = [p for p in PROJECTS if p.get('placement') == 'Work']
work = '<section class="page-top">'+eyebrow('Projects / Research / Practice')+'<h1>Things I’ve worked on.<br><em>Questions I’m still asking.</em></h1><p class="lede">A collection of research, systems, and useful little tools. Some are long investigations; others began with a small everyday frustration.</p><a class="text-link collection-story-link" href="index.html#notice">Follow the thread through the work ↗</a></section>'
work += '<div class="toolbar"><div class="filter-tabs" role="group" aria-label="Filter work by category">'+''.join(f'<button type="button" data-filter="{c}" aria-pressed="{str(c=="All").lower()}">{c}</button>' for c in ['All','Research','Engineering','Product'])+'</div><label class="search-box"><span aria-hidden="true">⌕</span><span class="sr-only">Search projects</span><input type="search" id="project-search" placeholder="Find a project or interest…" autocomplete="off"></label></div>'
work += f'<div class="result-meta"><span id="result-count" role="status" aria-live="polite">{len(work_projects)} experiences</span><span>Explore at your own pace ↘</span></div><div class="project-grid work-grid" id="work-grid">'+''.join(card(p,i+1) for i,p in enumerate(work_projects))+'</div><div class="empty-state" id="no-results" hidden><h2>No matching projects.</h2><p>Try another topic, or explore the whole collection.</p><button type="button" id="reset-filters">Clear filters</button></div>'
page('work.html','Work',work,'Work')

about = '''<section class="section about-intro" id="background"><div class="about-text">'''+eyebrow('A person, before a portfolio.')+'''<h1>Hi, I’m Zebang.<br><em>You can call me Zeb.</em></h1><p class="lede">An engineering student with a soft spot for good questions, thoughtful interfaces, and foxes.</p><p>I study Electronic Information Engineering at Westlake University and spent Fall 2025 at Cornell. My interests have grown through labs, student organizations, software projects, and conversations with people whose experiences differ from my own.</p><p>I like moving between understanding a system and making something with it. Outside the work, there are books, music, bike rides, and the occasional new plush toy.</p></div><figure class="portrait"><img src="images/Selfie1.jpg" width="600" height="700" alt="Zebang at Notre Dame in France"><figcaption>A little away from the desk. / France</figcaption></figure></section>'''
about += '<section class="section">' + section_head('A timeline, with a few detours.','How I got here.')
groups = OrderedDict()
for item in DATA['timeline']:
    groups.setdefault(item['year'], []).append(item)
about += '<nav class="year-nav" aria-label="Timeline years">' + ''.join(f'<a href="#year-{i}">{e(year)}</a>' for i,year in enumerate(groups)) + '</nav><div class="timeline">'
for i,(year,items) in enumerate(groups.items()):
    about += f'<section class="timeline-year" id="year-{i}"><h3>{e(year)}</h3><div class="timeline-items">'
    for item in items:
        href = item.get('href','')
        if href == 'about.html#background': href = '#background'
        title = f'<a href="{e(href)}">{e(item["title"])} ↗</a>' if href else e(item['title'])
        about += f'<article class="timeline-item"><span class="period">{e(item["period"])}</span><h4>{title}</h4><p>{e(item["body"])}</p>{tags(item["tags"])}</article>'
    about += '</div></section>'
about += '</div></section><section class="section">' + section_head('The other tabs in my head.','Outside the work.') + '<div class="personal-grid">'
for i,item in enumerate(DATA['interests']):
    about += f'<article class="personal-card"><span class="small-symbol" aria-hidden="true">{["✳","Aa","↗"][i]}</span><h3>{e(item["title"])}</h3><p>{e(item["body"])}</p></article>'
about += '</div></section>'
page('about.html','About',about,'About')

# Real assets from the earlier website; no invented application screenshots.
gallery = {
 'active-learning': [('ActiveLearning1.PNG','Research notes from the active-learning project.'),('ActiveLearning2.PNG','An archived diagram from the active-learning experiments.')],
 'westlake': [('Westlake1.jpeg','Westlake University.'),('Westlake2.jpg','A view of the Westlake campus.')],
 'cornell': [('Cornell1.jpeg','Cornell University during my exchange.'),('Cornell2.png','A moment from Cornell.')]
}
for index,p in enumerate(PROJECTS):
    id_ = p['id']
    body = f'<div class="case-top"><a class="breadcrumb" href="../{ "work.html" if p.get("placement")=="Work" else "about.html"}">← {"All work" if p.get("placement")=="Work" else "About me"}</a></div><section class="case-heading">{eyebrow(p["category"])}<h1>{e(p["title"])}</h1><p class="lede">{e(p["summary"])}</p>{tags(p["tags"])}</section>'
    body += f'<div class="case-meta"><div><span>My role</span>{e(p["role"])}</div><div><span>{"Period" if re.search(r"20[0-9]{2}",p["period"]) else "Context"}</span>{e(p["period"])}</div><div><span>Status</span>{e(p["status"])}</div></div>'
    if id_ in STORY_THREADS:
        chapter, label = STORY_THREADS[id_]
        body += f'<a class="case-story-thread" href="../index.html#{chapter}"><img src="../assets/art/geometric-mark.svg" width="30" height="30" alt=""><span><small>PART OF THE STORY</small>{e(label)}</span><span aria-hidden="true">↗</span></a>'
    body += '<div class="case-layout"><nav class="case-nav" aria-label="On this page">'+eyebrow('On this page')+''.join(f'<a href="#section-{i}">{e(s["title"])}</a>' for i,s in enumerate(p['sections']))+'</nav><div class="case-copy">'
    if p.get('subtitle'):
        body += '<aside class="case-callout">'+eyebrow('The idea')+f'<p>{e(p["subtitle"])}</p></aside>'
    if p.get('metrics'):
        body += '<div class="evidence-grid">' + ''.join(f'<div class="evidence-box"><strong>{e(m["value"])}</strong><span>{e(m["label"])}</span></div>' for m in p['metrics']) + '</div>'
    if id_ in ['involve','navix','fire-sim','igem']:
        media_labels = {'involve': 'The original classroom interface', 'navix': 'Product journeys & interactions', 'fire-sim': 'The simulation in motion', 'igem': 'The wiki, in detail'}
        body += '<figure class="media-reserved"><div class="media-outline"><span class="media-icon" aria-hidden="true">↗</span><span class="eyebrow">Screenshots & film</span><strong>'+media_labels[id_]+'</strong><span class="media-pending">Original project visuals to be added.</span></div><figcaption>A space for original captures from the project.</figcaption></figure>'
    for i,s in enumerate(p['sections']):
        body += f'<section class="case-section" id="section-{i}"><h2>{e(s["title"])}</h2><p>{e(s["body"])}</p></section>'
    if id_ in gallery:
        body += '<div class="case-gallery">'
        for image,caption in gallery[id_]:
            src='../images/Educational/'+image
            body += f'<figure><button class="image-button" type="button" data-lightbox="{src}" data-alt="{e(caption)}" data-caption="{e(caption)}" aria-label="Enlarge: {e(caption)}"><img loading="lazy" src="{src}" alt="{e(caption)}" width="600" height="400"></button><figcaption>{e(caption)} Click to enlarge.</figcaption></figure>'
        body += '</div>'
    if id_=='feasypaste':
        body += '<a class="button outline" href="https://chromewebstore.google.com/detail/feasypaste-feishu-convert/ehdmffeifoiagjgnkaajpdmhicdfajhb">View the extension <span>↗</span></a>'
    if id_=='involve': body += '<a class="text-link" href="ai-coding-course.html">The course I taught with InVolve ↗</a>'
    if id_=='dhh': body += '<a class="text-link" href="dhh-review.html">Related work: AI and accessibility ↗</a>'
    nxt=BY_ID[RELATED_NEXT[id_]]
    body += '</div></div>'+f'<nav class="case-next" aria-label="More projects"><a class="text-link" href="../work.html">Back to the collection</a><a href="{nxt["id"]}.html">{eyebrow("Keep exploring →")}<h3>{e(nxt["title"])}</h3></a></nav>'
    page(f'work/{id_}.html',p['title'],body,'Work' if p.get('placement')=='Work' else 'About','../')

writing = '<section class="page-top">'+eyebrow('Ideas with a little room to breathe.')+'<h1>Notes from<br><em>the in-between.</em></h1><p class="lede">Thoughts on learning, technology, and the human side of making things.</p></section>'
writing += '''<a class="article-card" href="sharing/abandon.html"><div class="article-art" aria-hidden="true">…</div><div><p class="eyebrow">01 / An exchange with AI · English & 中文</p><h2>Abandon</h2><p>A conversation prompted by leaving a machine behind. On memory, unfinished work, and what continuity might mean for an AI agent.</p><span class="text-link">Read the conversation ↗</span></div></a><section class="section"><div class="note-card"><p class="eyebrow">An open notebook</p><h3>Some questions stay with me.</h3><p>How do people learn unfamiliar tools? What makes a technical system useful? What do we carry from one place to the next?</p></div></section>'''
page('writing.html','Writing',writing,'Writing')
article_body = (ROOT/'content/abandon-body.html').read_text()
article = '<section class="page-top"><a class="breadcrumb" href="../writing.html">← All writing</a>'+eyebrow('An exchange with AI')+'<h1>Abandon</h1><p class="lede">On continuity, purpose, and what remains.</p></section><div class="article-body"><aside class="case-callout"><p>The opening passage is my question. The response that follows was generated by an AI assistant; it is preserved here as a conversation, not presented as my own essay.</p></aside>'+article_body+'</div>'
page('sharing/abandon.html','Abandon',article,'Writing','../')

cv = '<section class="page-top">'+eyebrow('A concise reference · September 2026')+'<h1>The short version.</h1><p class="lede">Education, research, and professional experience. Follow a project link for the longer story.</p></section><div class="cv-layout"><aside class="cv-aside"><h2>Zebang Wu</h2><p>吴泽邦<br>Hangzhou, China<br>Electronic Information Engineering</p><a class="text-link" href="mailto:wuzebang@westlake.edu.cn">Email ↗</a><br><button class="button outline cv-print" type="button">Print / Save as PDF ↗</button></aside><div>'
cv += '<section class="cv-section"><h2>Education</h2><article class="cv-entry"><div class="cv-entry-top"><h3>Westlake University</h3><span class="period">Expected May 2027</span></div><p>B.S. in Electronic Information Engineering</p><p>GPA 4.06/4.3 · TOEFL iBT 107/120</p></article><article class="cv-entry"><div class="cv-entry-top"><h3>Cornell University</h3><span class="period">Aug–Dec 2025</span></div><p>Exchange student · Electrical & Computer Engineering</p></article></section>'
for title,ids in [('Professional experience',['navix','dongfeng']),('Research',['reconstruction','active-learning','vr','dhh','dhh-review']),('Leadership',['student-union'])]:
    cv+=f'<section class="cv-section"><h2>{title}</h2>'
    for id_ in ids:
        p=BY_ID[id_]
        cv+=f'<article class="cv-entry"><div class="cv-entry-top"><h3><a href="work/{id_}.html">{e(p["title"])} ↗</a></h3><span class="period">{e(p["period"])}</span></div><p>{e(p["role"])}</p><p>{e(p["summary"])}</p></article>'
    cv+='</section>'
cv+='<section class="cv-section"><h2>Tools & languages</h2><p>Python · C++ · TypeScript · PyTorch · ONNX Runtime · MATLAB</p><p>CARLA · Vue · Git · Linux · Unity · Abaqus · LaTeX</p><p>Mandarin Chinese (native) · English (fluent)</p></section></div></div>'
page('cv.html','CV',cv,'CV')

# Keep old entry points usable while their content now has a clear home.
for old,new in [('Educational.html','about.html'),('Professional.html','work.html'),('Amateurs.html','about.html#outside'),('Resume.html','cv.html'),('Sharing.html','writing.html')]:
    if old=='Amateurs.html': new='about.html'
    (ROOT/old).write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0;url={new}"><title>Page moved · Zebang Wu</title><p>This page has moved to <a href="{new}">{new}</a>.</p></html>')
print(f'Generated five main pages, the visual standard and illustration workshop, {len(PROJECTS)} detail pages, the existing conversation, and five legacy redirects.')

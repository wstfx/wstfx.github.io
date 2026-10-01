"""Build the portfolio from content/portfolio-v2.json. Python standard library only."""
import json
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


def page(path, title, body, active, prefix=''):
    story_assets = '<link rel="stylesheet" href="assets/css/story.css"><script defer src="assets/js/story.js"></script>' if path == 'index.html' else ''
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
<link rel="stylesheet" href="{prefix}assets/css/portfolio.css">
<script defer src="{prefix}assets/js/privacy-gate.js"></script>
<script defer src="{prefix}assets/js/portfolio.js"></script>
{story_assets}
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
page('index.html','Home',home,'Home')

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
print(f'Generated five main pages, {len(PROJECTS)} detail pages, the existing conversation, and five legacy redirects.')

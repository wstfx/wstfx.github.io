"""Render the bilingual illustration brief without coupling it to portfolio copy."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def e(value):
    return escape(str(value), quote=True)


def pair(value):
    return '<div class="direction-pair">' + ''.join(
        f'<p lang="{lang}">{e(value[key])}</p>'
        for key, lang in [('zh', 'zh-CN'), ('en', 'en')]
    ) + '</div>'


def bilingual_list(values, ordered=False):
    tag = 'ol' if ordered else 'ul'
    return f'<{tag} class="direction-list">' + ''.join(
        '<li>' + pair(value) + '</li>' for value in values
    ) + f'</{tag}>'


def prompts(identity, value):
    out = '<details class="brief-details direction-prompts"><summary>完整设计稿 / Full copyable brief</summary><div class="direction-prompt-grid">'
    for key, lang, label in [('zh', 'zh-CN', '中文设计稿'), ('en', 'en', 'English brief')]:
        field = f'direction-{identity}-{key}'
        out += f'<div class="brief-prompt"><label for="{field}">{label}</label><textarea id="{field}" lang="{lang}" readonly spellcheck="false">{e(value[key])}</textarea><button class="button outline brief-copy" type="button" data-copy-prompt="{field}" hidden>复制 / Copy ↗</button><p class="brief-copy-status" role="status" aria-live="polite"></p></div>'
    return out + '</div></details>'


def layers(items):
    return '<div class="direction-layers">' + ''.join(
        f'<article><code>{e(item["id"])}</code><span class="direction-layer-state">{"可动 / Motion" if item["movable"] else "静态 / Still"}</span>{pair(item["description"])}</article>'
        for item in items
    ) + '</div>'


def render_direction():
    data = json.loads((ROOT / 'content/illustration-direction-v2.json').read_text())
    out = '<section class="brief-intro"><a class="breadcrumb" href="index.html">← 回到首页 / Back to the story</a><p class="eyebrow">ART DIRECTION V2 · 中文 / ENGLISH</p><h1>One fox.<br><em>Different moments.</em></h1><p class="lede" lang="zh-CN">让同一只狐狸，经历不同的时刻。</p>' + pair(data['premise']) + '</section>'
    out += '<div class="brief-callout">' + pair(data['status']) + '</div>'
    out += '<nav class="brief-nav" aria-label="Illustration direction sections"><a href="#identity">统一角色 / Identity</a>' + ''.join(f'<a href="#{e(s["id"])}">{e(s["chapter"])} · {e(s["id"].title())}</a>' for s in data['chapterBriefs']) + '<a href="#line-art">结尾线稿 / Line art</a><a href="#handoff">交付与协作 / Handoff</a></nav>'
    out += '<section class="brief-section"><h2>先看节奏，再画细节。</h2><p class="direction-english-title">Change the rhythm before adding detail.</p><div class="direction-overview">'
    for s in data['chapterBriefs']:
        out += f'<a href="#{e(s["id"])}"><span class="eyebrow">{e(s["chapter"])} / {e(s["heading"])}</span><strong lang="zh-CN">{e(s["title"]["zh"])}</strong><span lang="en">{e(s["title"]["en"])}</span></a>'
    out += '</div></section>'
    out += '<section class="brief-section" id="identity"><p class="eyebrow">CHARACTER / VISUAL GRAMMAR</p><h2>统一的是身份。</h2><p class="direction-english-title">Consistency in character, freedom in viewpoint.</p>' + bilingual_list(data['sharedRules'], True)
    out += '<div class="direction-palette">' + ''.join(f'<div><span style="background:{e(p["hex"])}"></span><code>{e(p["hex"])}</code>{pair(p["role"])}</div>' for p in data['palette']) + '</div>'
    out += '<details class="brief-details"><summary>母版与画布 / Source and canvas</summary>'
    for source in data['sourceReferences']:
        out += f'<p><a href="{e(source["path"])}">{e(Path(source["path"]).name)} ↗</a></p>' + pair(source['role'])
    out += ''.join(pair(v) for v in data['format'].values()) + '</details></section>'
    for s in data['chapterBriefs']:
        out += f'<section class="brief-section direction-chapter" id="{e(s["id"])}"><p class="eyebrow">{e(s["chapter"])} / {e(s["heading"])}</p><h2 lang="zh-CN">{e(s["title"]["zh"])}</h2><p class="direction-english-title" lang="en">{e(s["title"]["en"])}</p>'
        out += pair(s['story']) + '<h3>机位与动势 / Viewpoint and action</h3>' + pair(s['framing'])
        out += '<details class="brief-details"><summary>构图层次与项目联系 / Composition and project anchors</summary>'
        for key, title in [('foreground', '前景 / Foreground'), ('midground', '中景 / Middle distance'), ('background', '背景与装饰 / Background and decoration')]:
            out += f'<h3>{title}</h3>' + pair(s['composition'][key])
        out += '<ul>' + ''.join(f'<li>{e(x)}</li>' for x in s['projectAnchors']) + '</ul></details>'
        out += '<details class="brief-details"><summary>SVG 分组与动态边界 / Layers and motion</summary>' + layers(s['layers'])
        for m in s['motion']:
            out += f'<h3><code>{e(m["target"])}</code></h3>' + pair(m['direction'])
        out += '<h3>静态阅读检查 / Still-image check</h3>' + pair(s['staticRequirement']) + '</details>'
        out += prompts(s['id'], s['prompt']) + '</section>'
    coda = data['codaLineArt']
    out += '<section class="brief-section" id="line-art"><p class="eyebrow">CODA / LINE-ART BACKGROUND</p><h2>以线织狐。<br><em>以纹续篇。</em></h2><p class="direction-english-title">A fox in the thread. A story in the weave.</p><blockquote class="direction-coda-quote">Understand more.<br>Make something useful.<br><em>Find the next question.</em></blockquote>' + pair(coda['principle'])
    out += '<div class="brief-callout"><strong>线与文字共存 / Let line and type coexist</strong>' + pair(coda['typeSafeZone']) + '</div>' + bilingual_list(coda['renderRules'])
    for option in coda['concepts']:
        out += f'<article class="direction-line-option" id="{e(option["id"])}"><h3 lang="zh-CN">{e(option["title"]["zh"])}</h3><p class="direction-english-title">{e(option["title"]["en"])}</p>' + pair(option['composition']) + pair(option.get('why', option.get('tradeoff')))
        out += '<details class="brief-details"><summary>线稿分组与动态 / Contour groups and motion</summary>' + layers(option['layers']) + pair(option['motion']) + '</details>' + prompts(option['id'], option['prompt']) + '</article>'
    out += '</section><section class="brief-section" id="handoff"><p class="eyebrow">PRODUCTION / PARALLEL CONTENT WORK</p><h2>你把握主画面。<br>我把它带进网页。</h2><p class="direction-english-title">You direct the illustration. I bring it into the site.</p>' + bilingual_list(data['handoff'], True)
    out += '<div class="brief-callout"><strong>内容现在就能并行 / Content can start now</strong><p lang="zh-CN">Work 的内容与界面可以和首页插画同步开发。Work 代理负责项目内容、Work 页面与专用样式脚本；首页视觉代理负责 SVG、首页样式、动效和本设计稿。共享样式与构建脚本由一人整合，使用 --only 构建指定页面。</p><p lang="en">Work content and UI can proceed alongside homepage illustration. The Work agent owns project content and page-scoped styles and scripts; the homepage agent owns art, homepage styles, motion and this brief. One owner integrates shared CSS and build changes. Use --only to build selected pages.</p><ul>'
    for path in ['content/portfolio-v2.json', 'content/work-intro.html', 'content/about-intro.html']:
        out += f'<li><code>{path}</code></li>'
    out += '</ul><a href="content/portfolio-content-handoff.txt" download>内容代理任务说明 / Content-agent handoff ↓</a></div><details class="brief-details"><summary>交稿前检查 / Review before handoff</summary>' + bilingual_list(data['reviewChecklist']) + '</details><div class="direction-downloads"><a class="button outline" href="illustration-direction-v2.txt" download>中英文完整设计稿 / Download full brief ↓</a><a href="illustration-briefs.html">上一版工作流与工具 / Previous workflow ↗</a></div></section>'
    write_text_brief(data)
    return out


def write_text_brief(data):
    """Readable bilingual export, including composition, layer and motion notes."""
    lines = []

    def visit(value, depth=0):
        if isinstance(value, dict) and 'zh' in value and 'en' in value:
            lines.extend([value['zh'], value['en'], ''])
        elif isinstance(value, dict):
            for key, child in value.items():
                lines.append('  ' * depth + key + ':')
                visit(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                visit(child, depth)
        else:
            lines.append(str(value))

    visit(data)
    (ROOT / 'illustration-direction-v2.txt').write_text('\n'.join(lines).rstrip() + '\n')

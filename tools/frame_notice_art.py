"""Frame and non-destructively rig the supplied vectorized Notice close-up.

The untouched trace remains the authority. Native vector silhouettes define the
book/hand selection; masks remove their stationary copies before any motion.
Small hidden vector underlaps reveal table/fox colours at the motion extremes.
"""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/art'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def tag(name):
    return f'{{{NS}}}{name}'


def sub(parent, name, **attrs):
    return ET.SubElement(parent, tag(name), {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def copy_path(path, **attrs):
    item = deepcopy(path)
    item.attrib.pop('id', None)
    item.attrib.pop('data-trace-path', None)
    item.attrib.update({k.replace('_', '-'): str(v) for k, v in attrs.items()})
    return item


def prepare():
    source = ET.parse(ART / 'scene-notice-closeup.svg').getroot()
    assert source.get('viewBox') == '0 0 1298 1212'
    paths = {int(p.get('data-trace-path')): p for p in source.iter(tag('path')) if p.get('data-trace-path')}
    svg = ET.Element(tag('svg'), {
        'viewBox': '-46 32 1390 1148',
        'class': 'chapter-illustration notice-conversation-window',
        'role': 'img', 'aria-labelledby': 'notice-window-title notice-window-description',
    })
    sub(svg, 'title', id='notice-window-title').text = 'Start with someone'
    sub(svg, 'desc', id='notice-window-description').text = (
        'An attentive orange fox looks toward someone offering an open notebook. '
        'Their forearm enters through the left edge of a fine, open frame; the fox rises above it. '
        'The whole tail and the hand with its notebook move as separate, coherent vector layers.'
    )
    # Native 0-based viewport keeps CSS transform-origin coordinates exact even
    # though the outer presentation viewBox includes extra margin.
    scene = sub(svg, 'svg', x=0, y=0, width=1298, height=1212, viewBox='0 0 1298 1212', overflow='visible', aria_hidden='true')
    defs = sub(scene, 'defs')
    for node in source.find(tag('defs')):
        defs.append(deepcopy(node))
    painted = sub(defs, 'g', id='notice-native-paint')
    for node in source:
        if node.tag not in {tag('title'), tag('desc'), tag('metadata'), tag('defs')}:
            painted.append(deepcopy(node))
    clip = sub(defs, 'clipPath', id='notice-window-clip', clipPathUnits='userSpaceOnUse')
    sub(clip, 'path', d='M0 0H1298V1080Q1298 1110 1268 1110H30Q0 1110 0 1080Z')
    book_clip = sub(defs, 'clipPath', id='notice-book-region', clipPathUnits='userSpaceOnUse')
    sub(book_clip, 'rect', x=0, y=738, width=870, height=400)
    offering_clip = sub(defs, 'clipPath', id='notice-offering-clip', clipPathUnits='userSpaceOnUse')
    # Path 4 contains the native sleeve, hand and book cover outline. Path 2's
    # lower connected cream area supplies the pages; its tail tip is excluded.
    offering_clip.append(copy_path(paths[4], fill='white'))
    offering_clip.append(copy_path(paths[14], fill='white'))
    paper = copy_path(paths[2], fill='white')
    paper_outline = paths[2].get('d')
    paper.set('d', 'M-110 305 C-84 306 -59 309 -32 316 ' + paper_outline[paper_outline.index('C-31.02 316.13'):paper_outline.index('C-117.4 305.87')] + 'Z')
    offering_clip.append(paper)
    tail_d = 'M105 380H528L630 555L706 691L741 744C727 769 716 791 704 818L694 843H585L379 808L214 692L105 565Z'
    tail_cut_d = 'M105 380H528L630 555L706 691L727 744C713 769 702 791 690 818L680 843H585L379 808L214 692L105 565Z'
    tail_clip = sub(defs, 'clipPath', id='notice-tail-clip', clipPathUnits='userSpaceOnUse')
    sub(tail_clip, 'path', d=tail_d)
    base_mask = sub(defs, 'mask', id='notice-still-mask', maskUnits='userSpaceOnUse', x=-30, y=0, width=1370, height=1212, style='mask-type:luminance')
    sub(base_mask, 'rect', x=-30, y=0, width=1370, height=1212, fill='white')
    sub(base_mask, 'path', d=tail_cut_d, fill='black')
    for shape in (paths[4], paths[14], paper):
        base_mask.append(copy_path(shape, fill='black', stroke='black', stroke_width=3, stroke_linejoin='round'))
    under_mask = sub(defs, 'mask', id='notice-offering-underlap-mask', maskUnits='userSpaceOnUse', x=-30, y=0, width=1370, height=1212, style='mask-type:luminance')
    for shape in (paths[4], paths[14], paper):
        under_mask.append(copy_path(shape, fill='white', stroke='white', stroke_width=8, stroke_linejoin='round'))
    tail_cream = sub(defs, 'clipPath', id='notice-tail-cream-clip', clipPathUnits='userSpaceOnUse')
    sub(tail_cream, 'rect', x=0, y=0, width=1298, height=735)

    # A loose guiding arc lives behind the art, never across the face or page.
    decorations = sub(scene, 'g', id='notice-guiding-lines', fill='none', stroke_linecap='round', stroke_linejoin='round')
    sub(decorations, 'path', class_='notice-decor-arc', d='M113 298C204 220 374 207 481 259C565 300 592 366 599 410', stroke='#9BAB91', stroke_width=2.2, opacity=.55)
    sub(decorations, 'path', class_='notice-decor-arc-inner', d='M165 286C267 227 387 245 453 279', stroke='#9BAB91', stroke_width=1.8, stroke_dasharray='2 12', opacity=.5)
    leaf = sub(decorations, 'g', class_='notice-decor-leaf', style='transform-box:view-box;transform-origin:468px 284px')
    sub(leaf, 'path', d='M468 284C441 279 434 256 443 239C464 241 479 260 468 284Z', fill='#CAD2BC', stroke='#819679', stroke_width=1.6)
    sub(leaf, 'path', d='M468 284L447 247', stroke='#819679', stroke_width=1.5)
    seed = sub(decorations, 'g', class_='notice-decor-seed', style='transform-box:view-box;transform-origin:128px 292px')
    sub(seed, 'circle', cx=128, cy=292, r=5, fill='#E87532', stroke='none')
    sub(seed, 'path', d='M123 277L120 264M108 286L96 282', stroke='#B8C4AA', stroke_width=2)

    window = sub(scene, 'g', clip_path='url(#notice-window-clip)')
    # Reconstruct only previously hidden material. The hand can lift above the
    # table without revealing a duplicate sleeve/book silhouette underneath.
    under = sub(window, 'g', id='notice-motion-underlap', mask='url(#notice-offering-underlap-mask)')
    sub(under, 'path', d='M249 1023L858 892L1298 925V1145L249 1080Z', fill='#C1C9B3')
    under_top = sub(under, 'g', clip_path='url(#notice-book-region)')
    for n in (1, 3):
        item = copy_path(paths[n], stroke=paths[n].get('fill'), stroke_width=38, stroke_linejoin='round', paint_order='stroke fill')
        under_top.append(item)

    tail = sub(window, 'g', id='notice-tail-rig', class_='notice-tail', style='transform-box:view-box;transform-origin:721px 796px', data_pivot='721 796')
    # Hidden continuation beneath the notebook: its lift must not uncover the
    # old paper-shaped cut in the traced tail. These strips share native fills.
    sub(tail, 'path', d='M348 787L402 746L477 754L489 792L415 780L367 825Z', fill='#FBBD85')
    sub(tail, 'path', d='M474 733C473 754 477 776 491 791Q555 800 619 822L694 809L703 862H599Q530 815 480 803C469 790 465 760 474 733Z', fill='#BD4713')
    tail_parts = sub(tail, 'g', clip_path='url(#notice-tail-clip)')
    for n in (1, 2, 3, 5, 11, 15, 16, 20, 61, 66, 76, 90):
        item = copy_path(paths[n])
        if n == 2:
            upper_cream = sub(tail_parts, 'g', clip_path='url(#notice-tail-cream-clip)')
            upper_cream.append(item)
        else:
            tail_parts.append(item)
    still = sub(window, 'g', id='notice-stationary-art', mask='url(#notice-still-mask)')
    sub(still, 'use', href='#notice-native-paint')
    offering = sub(window, 'g', id='notice-offering-rig', class_='notice-offering', style='transform-box:view-box;transform-origin:0px 881px', data_pivot='0 881')
    selection = sub(offering, 'g', clip_path='url(#notice-offering-clip)')
    sub(selection, 'use', href='#notice-native-paint')
    # Corner ticks belong to the book gesture, outside its native paint.
    marks = sub(offering, 'g', class_='notice-decor-paper', fill='none', stroke='#9AAB8E', stroke_width=2.4, stroke_linecap='round', opacity=.65)
    sub(marks, 'path', d='M364 761L376 749L390 751M812 1081L824 1084L831 1070')

    frame = sub(svg, 'g', id='notice-window-frame', fill='none', stroke_linecap='round', stroke_linejoin='round')
    sub(frame, 'path', d='M246 350H30Q0 350 0 380V1080Q0 1110 30 1110H1268Q1298 1110 1298 1080V875', stroke='#8D9D87', stroke_width=3.5)
    sub(frame, 'circle', cx=268, cy=350, r=4, fill='#E87532')
    # Keep Python-friendly class_ spelling out of the emitted SVG.
    for node in svg.iter():
        if 'class-' in node.attrib:
            node.set('class', node.attrib.pop('class-'))
    ET.indent(svg, space='  ')
    out = ART / 'scene-notice-framed.svg'
    out.write_text(ET.tostring(svg, encoding='unicode') + '\n')
    assert not list(svg.iter(tag('image'))), 'The framed artwork must stay entirely vector.'
    print(out.relative_to(ROOT))


if __name__ == '__main__':
    prepare()

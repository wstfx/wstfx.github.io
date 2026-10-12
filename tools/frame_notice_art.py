"""Frame and non-destructively rig the supplied vectorized Notice close-up.

The untouched trace remains the authority. Only the tail is separated for
motion; the complete native hand, notebook, tabletop and fox body remain in
one stationary paint layer. The existing eyes retain their blink hooks.
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
        'The tail sways behind the still notebook and hand; the fox occasionally blinks.'
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
    # The guard follows the final visible page edge (after all native colour
    # layers), rather than the larger cream underpaint that also spans the tail.
    # This is only an occlusion boundary; the notebook is painted entirely from
    # the unmodified native trace, including its cover, crease and edge pixels.
    book_edge = [(409, 756), (425, 757), (440, 759), (455, 761), (470, 764),
                 (485, 767), (500, 772), (515, 775), (530, 780), (545, 786),
                 (560, 793), (575, 801), (590, 810), (605, 823), (620, 837),
                 (635, 830), (650, 827), (665, 826), (680, 826), (695, 828),
                 (710, 830), (725, 833), (740, 836), (755, 839), (770, 843),
                 (785, 847), (800, 852), (815, 858), (830, 863), (845, 868), (855, 873)]
    paper = ET.Element(tag('path'), {'fill': 'white', 'd':
        'M' + 'L'.join(f'{x} {y}' for x, y in book_edge) + 'L781 1085H260V905Z'})
    tail_d = 'M105 380H528L630 555L706 691L741 744C727 769 716 791 704 818L694 843H585L395 850L205 710L105 565Z'
    tail_cut_d = 'M105 380H528L630 555L706 691L727 744C713 769 702 791 690 818L680 843H585L395 850L205 710L105 565Z'
    tail_clip = sub(defs, 'clipPath', id='notice-tail-clip', clipPathUnits='userSpaceOnUse')
    sub(tail_clip, 'path', d=tail_d)
    base_mask = sub(defs, 'mask', id='notice-still-mask', maskUnits='userSpaceOnUse', x=-30, y=0, width=1370, height=1212, style='mask-type:luminance')
    sub(base_mask, 'rect', x=-30, y=0, width=1370, height=1212, fill='white')
    sub(base_mask, 'path', d=tail_cut_d, fill='black')
    # The tail selection overlaps the notebook. Restore the unchanged native
    # forearm, hand, cover and paper above the moving tail, including edge pixels.
    for shape in (paths[4], paths[14], paper):
        base_mask.append(copy_path(shape, fill='white'))
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
    tail = sub(window, 'g', id='notice-tail-rig', class_='notice-tail', style='transform-box:view-box;transform-origin:721px 796px', data_pivot='721 796')
    # Continue the native apricot and dark tail contours underneath the book.
    # Reusing their exact outer curves avoids visible wedges when the tail rises.
    apricot_underlap = copy_path(paths[11])
    apricot_d = paths[11].get('d')
    apricot_underlap.set('d', apricot_d[:apricot_d.index('C306.65 223.49')] +
        'C322 258 337 278 340 304 C265 317 220 299 182 254 ' +
        apricot_d[apricot_d.index('C175 247.22'):])
    tail.append(apricot_underlap)
    dark_underlap = copy_path(paths[20])
    dark_d = paths[20].get('d')
    dark_underlap.set('d', dark_d[:dark_d.index('C241.43 224.99')] +
        'C242 259 231 286 215 300 C157 290 70 252 50 223 C40 204 38 187 37 165 ' +
        dark_d[dark_d.index('C32.36 157.98'):])
    tail.append(dark_underlap)
    tail_parts = sub(tail, 'g', clip_path='url(#notice-tail-clip)')
    for n in (1, 2, 3, 5, 11, 15, 16, 20, 61, 66, 76, 90):
        item = copy_path(paths[n])
        if n == 2:
            upper_cream = sub(tail_parts, 'g', clip_path='url(#notice-tail-cream-clip)')
            upper_cream.append(item)
        else:
            tail_parts.append(item)
    still = sub(window, 'g', id='notice-stationary-art', mask='url(#notice-still-mask)')
    # Render the eye groups in the live SVG tree. Blink animations inside a
    # <use> shadow tree are not reliably styled by ancestor selectors in Chrome.
    for node in painted:
        still.append(deepcopy(node))
    defs.remove(painted)

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

"""Give the supplied Notice close-up an intentional, open picture edge."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/art'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def tag(name):
    return f'{{{NS}}}{name}'


def prepare():
    source = ET.parse(ART / 'scene-notice-closeup.svg').getroot()
    assert source.get('viewBox') == '0 0 1298 1212'
    svg = ET.Element(tag('svg'), {
        'viewBox': '-46 32 1390 1148',
        'class': 'chapter-illustration notice-conversation-window',
        'role': 'img', 'aria-labelledby': 'notice-window-title notice-window-description',
    })
    ET.SubElement(svg, tag('title'), {'id': 'notice-window-title'}).text = 'Start with someone'
    ET.SubElement(svg, tag('desc'), {'id': 'notice-window-description'}).text = (
        'An attentive orange fox looks toward someone offering an open notebook. '
        'Their forearm enters through the left edge of a fine, open frame; the fox rises above it.'
    )
    defs = ET.SubElement(svg, tag('defs'))
    clip = ET.SubElement(defs, tag('clipPath'), {'id': 'notice-window-clip', 'clipPathUnits': 'userSpaceOnUse'})
    ET.SubElement(clip, tag('path'), {'d': 'M0 0H1298V1080Q1298 1110 1268 1110H30Q0 1110 0 1080Z'})
    window = ET.SubElement(svg, tag('g'), {'clip-path': 'url(#notice-window-clip)'})
    # A nested viewport preserves the converted artwork's native motion pivots.
    source = deepcopy(source)
    source.attrib.update({'x': '0', 'y': '0', 'width': '1298', 'height': '1212', 'aria-hidden': 'true'})
    source.attrib.pop('role', None)
    source.attrib.pop('aria-labelledby', None)
    window.append(source)
    frame = ET.SubElement(svg, tag('g'), {'id': 'notice-window-frame', 'fill': 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round'})
    ET.SubElement(frame, tag('path'), {
        'd': 'M246 350H30Q0 350 0 380V1080Q0 1110 30 1110H1268Q1298 1110 1298 1080V875',
        'stroke': '#8D9D87', 'stroke-width': '3.5',
    })
    ET.SubElement(frame, tag('circle'), {'cx': '268', 'cy': '350', 'r': '4', 'fill': '#E87532'})
    ET.indent(svg, space='  ')
    out = ART / 'scene-notice-framed.svg'
    out.write_text(ET.tostring(svg, encoding='unicode') + '\n')
    assert not list(svg.iter(tag('image'))), 'The framed artwork must stay entirely vector.'
    print(out.relative_to(ROOT))


if __name__ == '__main__':
    prepare()

"""Structural regression checks for live eye animation and authored SVG rigs."""
from pathlib import Path
from hashlib import sha256
import json
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]; N='{http://www.w3.org/2000/svg}'
p1=E.parse(ROOT/'assets/art/scene-notice-framed.svg').getroot()
parents={child:parent for parent in p1.iter() for child in parent}
eyes=[p for p in p1.iter() if 'scene-fox-eye' in p.get('class','').split()]
assert len(eyes)==20
for eye in eyes:
    node=eye
    while node in parents:
        node=parents[node]
        assert node.tag!=N+'defs', 'A blink group in a <use> shadow tree can stop animating in Chrome.'
assert not p1.findall('.//'+N+'use')
assert not any(p.get('class') in ['notice-offering','notice-decor-paper'] for p in p1.iter())
for name,expected in [('build',{'car','tail','eye'}),('return',{'tail','typing'})]:
    root=E.parse(ROOT/f'assets/art/scene-{name}-authored.svg').getroot()
    assert not list(root.iter(N+'image')) and not list(root.iter(N+'style'))
    metadata=json.loads(root.find(N+'metadata').text)
    assert sha256((ROOT/metadata['source']).read_bytes()).hexdigest()==metadata['sha256']
    assert {e.get('data-motion') for e in root.iter() if e.get('data-motion')}==expected
    ids=[e.get('id') for e in root.iter() if e.get('id')];assert len(ids)==len(set(ids))
html=(ROOT/'index.html').read_text()
assert 'scene-build-authored.svg' in html and 'scene-return-authored.svg' in html
assert 'id="P3-car"' in html and 'id="P4-tail"' in html
print('PASS: live Notice eyes, stationary hand/book, scoped native SVGs, unchanged author sources, unique IDs and new scene integration.')

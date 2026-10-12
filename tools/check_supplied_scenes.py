"""Structural regression checks for live eye animation and authored SVG rigs."""
from pathlib import Path
from hashlib import sha256
import json
import re
from prepare_supplied_scenes import absolute
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
    tail=next(e for e in root.iter() if e.get('data-motion')=='tail')
    anchor=float(tail.get('data-fixed-root-x'))
    moving_points=0
    for path in tail:
        phases={phase:absolute(re.search('--tail-'+phase+r':path\("([^"]+)"\)',path.get('style')).group(1)) for phase in ('rest','up','down')}
        assert [c for c,v in phases['rest']]==[c for c,v in phases['up']]==[c for c,v in phases['down']]
        for phase in ('up','down'):
            for (_,rest),(_,bent) in zip(phases['rest'],phases[phase]):
                for j in range(0,len(rest),2):
                    assert rest[j]==bent[j]
                    if rest[j]>=anchor:assert rest[j+1]==bent[j+1], 'Tail attachment must stay fixed throughout its motion.'
                    elif abs(rest[j+1]-bent[j+1])>1:moving_points+=1
    assert moving_points>10
    assert any('ornament-traveller' in e.get('class','') for e in root.iter())
    ids=[e.get('id') for e in root.iter() if e.get('id')];assert len(ids)==len(set(ids))
# Moving parts retain their complete native shadows and painter order.
build=E.parse(ROOT/'assets/art/scene-build-authored.svg').getroot()
car=next(e for e in build.iter() if e.get('id')=='P3-car')
assert {'P3-path-21','P3-path-23','P3-path-30','P3-path-32','P3-path-34'} <= {e.get('id') for e in car}, 'All car shadow fragments must travel together.'
returned=E.parse(ROOT/'assets/art/scene-return-authored.svg').getroot()
children=[e.get('id') for e in returned]
assert children.index('P4-typing')>children.index('P4-path-13'), 'Finger detail must paint above the keyboard.'
hand=next(e for e in returned if e.get('id')=='P4-typing')
assert next(e for e in hand if e.get('id')=='P4-path-9').get('mask')=='url(#P4-hand-skin-mask)'
assert {'P4-path-15','P4-path-16','P4-path-17','P4-path-18','P4-path-19'} <= {e.get('id') for e in hand}
assert next(e for e in returned.iter() if e.get('id')=='P4-sprig-space').get('transform')=='translate(-18 95)'
css=(ROOT/'assets/css/story.css').read_text()
assert 'animation:authored-angled-blink 7.5s' in css and 'rotate(-49deg) scaleY(.10) rotate(49deg)' in css
html=(ROOT/'index.html').read_text()
assert 'scene-build-authored.svg' in html and 'scene-return-authored.svg' in html
assert 'id="P3-car"' in html and 'id="P4-tail"' in html
print('PASS: live Notice eyes, stationary hand/book, scoped native SVGs, unchanged author sources, unique IDs, pinned tail attachments, moving tips, decorative paths and scene integration.')

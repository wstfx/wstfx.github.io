"""Orthographic house illustration. Every architectural point shares one 3D projection."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
# Width 4, depth 5, wall height 3.2, ridge 4.7. All z edges stay vertical.
def p(x,y,z=0): return (250+32*x-32*y,260+16*x+16*y-34*z)
def xy(q): return f'{q[0]:.2f},{q[1]:.2f}'
def points(v): return ' '.join(xy(p(*a)) for a in v)
def poly(v,fill,stroke='#234d3b',width=1.8,extra=''):
 return f'<polygon points="{points(v)}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {extra}/>'
def line(v,stroke='#234d3b',width=2,extra=''):
 return f'<polyline points="{points(v)}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'
def facepath(v): return 'M'+'L'.join(xy(p(*a)) for a in v)+'Z'
def roof(x): return 4.7-.75*abs(x)
s=['<svg class="fire-house-art" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400" fill="none" aria-hidden="true">', '<!-- All house geometry is projected from tools/build_fire_art.py; do not nudge individual vertices. -->']
s += [poly([(-2.6,-3.1,-.22),(2.6,-3.1,-.22),(2.6,3.1,-.22),(-2.6,3.1,-.22)],'#e4e9db','none'),poly([(-2.2,-2.7,0),(2.2,-2.7,0),(2.2,2.7,0),(-2.2,2.7,0)],'#eeeadd','#9dae94'),poly([(2.2,-2.7,0),(2.2,2.7,0),(2.2,2.7,-.18),(2.2,-2.7,-.18)],'#c7d1ba','none'),poly([(-2.2,2.7,0),(2.2,2.7,0),(2.2,2.7,-.18),(-2.2,2.7,-.18)],'#d5ddc9','none')]
# Floor boards and heat footprint stay coplanar with the slab.
for y in [-2,-1,0,1,2]: s.append(line([(-2,y,.02),(2,y,.02)],'#d8d5c7',.8))
s.append('<g class="fh-heat" opacity=".35">')
for bounds,c in [((-1.8,1.8,-2.2,2.2),'#efdcba'),((-1.1,1.6,-1.5,2),'#eab878'),((-.4,1.4,-.5,1.8),'#df8d4a')]:
 a,b,c0,d=bounds;s.append(poly([(a,c0,.03),(b,c0,.03),(b,d,.03),(a,d,.03)],c,'none'))
s.append('</g>')
# Back walls provide a clean interior backdrop when the two near surfaces fade.
s.append(poly([(-2,-2.5,0),(2,-2.5,0),(2,-2.5,3.2),(0,-2.5,4.7),(-2,-2.5,3.2)],'#e4e8d9','#91a285',1.5))
s.append(poly([(-2,-2.5,0),(-2,2.5,0),(-2,2.5,3.2),(-2,-2.5,3.2)],'#eef0e5','#91a285',1.5))
# Structural ribs: posts, rafters and ridge meet at identical projected coordinates.
for y in [-2.5,0,2.5]:
 s.append(line([(-2,y,0),(-2,y,3.2),(0,y,4.7),(2,y,3.2),(2,y,0)],'#526e53',3.2))
for x,z in [(-2,3.2),(0,4.7),(2,3.2)]: s.append(line([(x,-2.5,z),(x,2.5,z)],'#526e53',3.2))
s.append(line([(2,0,0),(2,0,3.2)],'#ce713b',4,'class="fh-warm-member"'))
# Flame is a pictogram on a vertical billboard inside the room, not building geometry.
fx,fy=p(1,.2,.05)
s.append(f'<g transform="translate({fx:.2f} {fy:.2f})"><g class="fh-flame"><path d="M-15 -3C-34 -24-8 -36-8 -59C14 -46 1 -31 14 -26C21 -33 23 -41 22 -45C47 -13 23 5 6 5C-3 5-10 1-15 -3Z" fill="#dd7b35"/><path class="fh-flame-core" d="M-3 -4C-12 -15 6 -24 6 -35C26 -14 19 1 8 1Z" fill="#f7dca3"/></g></g>')
s.append('<g class="fh-plume" opacity=".45" stroke="#96a88d" stroke-width="2.5" stroke-linecap="round">')
for dx in [-8,12]:
 x=fx+dx;s.append(f'<path d="M{x:.2f} {fy-68:.2f}c-16 -15 13 -24 1 -40s10 -24 2 -37"/>')
s.append('</g>')
# Near side wall and roof are removable as one view layer; geometry never moves.
s.append('<g class="fh-shell">')
s.append(poly([(2,-2.5,0),(2,2.5,0),(2,2.5,3.2),(2,-2.5,3.2)],'#cfdbc3'))
for a,b in [(-1.8,-.55),(.5,1.75)]:
 s.append(poly([(2,a,1.25),(2,b,1.25),(2,b,2.45),(2,a,2.45)],'#f5e4bc','#6e8868',1.7))
 s.append(line([(2,(a+b)/2,1.25),(2,(a+b)/2,2.45)],'#8a9d7c',1.2))
 s.append(line([(2,a,1.85),(2,b,1.85)],'#8a9d7c',1.2))
s.append('</g>')
# Front gable stays present in both views. Door is an actual opening.
front=[(-2,2.5,0),(2,2.5,0),(2,2.5,3.2),(0,2.5,4.7),(-2,2.5,3.2)]
door=[(.5,2.5,0),(1.5,2.5,0),(1.5,2.5,2.1),(.5,2.5,2.1)]
s.append(f'<path d="{facepath(front)}{facepath(door)}" fill="#f4f0e4" fill-rule="evenodd" stroke="#234d3b" stroke-width="1.8" stroke-linejoin="round"/>')
s.append(poly([(-1.5,2.5,1.25),(-.35,2.5,1.25),(-.35,2.5,2.4),(-1.5,2.5,2.4)],'#f0d5a0','#76916d',1.8))
s.append(line([(-.925,2.5,1.25),(-.925,2.5,2.4)],'#76916d',1.3))
s.append(line([(-1.5,2.5,1.825),(-.35,2.5,1.825)],'#76916d',1.3))
s.append(poly([(-.42,2.5,3.1),(.42,2.5,3.1),(.42,2.5,3.65),(-.42,2.5,3.65)],'#cbd8bd','#76916d',1.4))
s.append(line([(0,2.5,3.1),(0,2.5,3.65)],'#76916d',1.2))
# Near roof slope, with a consistent 0.16-unit overhang and fascia thickness.
s.append('<g class="fh-shell">')
s.append(poly([(-2.16,-2.66,roof(2.16)),(0,-2.66,roof(0)),(0,2.66,roof(0)),(-2.16,2.66,roof(2.16))],'#bfceb0','#234d3b',2.2))
a=[(0,-2.66,roof(0)),(2.16,-2.66,roof(2.16)),(2.16,2.66,roof(2.16)),(0,2.66,roof(0))]
s.append(poly(a,'#9eb28e','#234d3b',2.2))
s.append(poly([(2.16,-2.66,roof(2.16)),(2.16,2.66,roof(2.16)),(2.16,2.66,roof(2.16)-.14),(2.16,-2.66,roof(2.16)-.14)],'#79946e','#234d3b',1.2))
for y in [-1.8,-.9,0,.9,1.8]: s.append(line([(0,y,roof(0)),(2.16,y,roof(2.16))],'#839e77',1))
for x in [.72,1.44]: s.append(line([(x,-2.66,roof(x)),(x,2.66,roof(x))],'#839e77',1))
s.append('</g>')
# Front rake trim is fixed and continuous with both eaves.
s.append(line([(-2.16,2.66,roof(2.16)),(0,2.66,4.7),(2.16,2.66,roof(2.16))],'#234d3b',3.2))
# Two level instrument cards, deliberately detached from the architectural projection.
s.append('<g transform="translate(24 68)"><rect width="116" height="64" rx="9" fill="#f8f5eb" stroke="#234d3b" stroke-width="1.8"/><path d="M15 48H102M15 15V48" stroke="#c4cfb9"/><path d="M18 44L32 40 46 33 60 20 75 18 89 26 101 31" stroke="#d5753d" stroke-width="2.8" stroke-linecap="round"/><circle cx="101" cy="31" r="3" fill="#d5753d"/></g>')
x,y=p(2,0,1.6)
s.append(f'<path d="M{x:.2f} {y:.2f}H448V312" stroke="#9eaf95" stroke-width="1.2" stroke-dasharray="3 5" opacity=".6"/><circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#f8f5eb" stroke="#d5753d" stroke-width="1.8"/>')
s.append('<g transform="translate(351 312)"><rect width="123" height="60" rx="9" fill="#f8f5eb" stroke="#234d3b" stroke-width="1.8"/><path d="M16 45H108M16 13V45" stroke="#c4cfb9"/><path d="M19 42L36 36 52 25 74 17H106" stroke="#234d3b" stroke-width="2.8" stroke-linecap="round"/></g></svg>')
(ROOT/'assets/art/fire-sim-house.svg').write_text('\n'.join(s)+'\n')

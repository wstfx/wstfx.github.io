"""Derive named web motion layers from the owner's cleaned P3/P4 SVGs.

Original Illustrator exports are immutable inputs. No retracing, face changes,
external API or generated image. Local fills replace global Illustrator .stN
selectors so the two inline SVGs cannot recolour each other.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import re
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'; N='{'+NS+'}'
E.register_namespace('',NS)

def sub(parent,name,**attrs):
    return E.SubElement(parent,N+name,{k.replace('_','-'):str(v) for k,v in attrs.items()})

def absolute(d):
    tokens=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',d)
    i=0;x=y=0;start=(0,0);out=[];cmd=None
    while i<len(tokens):
        if tokens[i].isalpha():cmd=tokens[i];i+=1
        c=cmd.upper();relative=cmd.islower();n={'M':2,'L':2,'C':6,'H':1,'V':1,'Z':0}[c]
        if c=='Z':out.append(('Z',[]));x,y=start;cmd=None;continue
        v=list(map(float,tokens[i:i+n]));i+=n
        if c=='H':v=[v[0]+(x if relative else 0),y];c='L'
        elif c=='V':v=[x,v[0]+(y if relative else 0)];c='L'
        elif relative:v=[a+(x if j%2==0 else y) for j,a in enumerate(v)]
        x,y=v[-2:];out.append((c,v))
        if c=='M':start=(x,y);cmd='l' if relative else 'L'
    return out

def load(scene):
    file=ROOT/f'assets/IllustratorWorkspace/FoxIllustration_{scene}.svg'; original=file.read_bytes(); source=E.fromstring(original)
    assert source.get('viewBox')=='0 0 1254 1254'
    definitions=deepcopy(source.find(N+'defs')); style=definitions.find(N+'style')
    rules={c:dict(re.findall(r'([\w-]+)\s*:\s*([^;]+);',v)) for c,v in re.findall(r'\.([\w-]+)\s*\{([^}]+)\}',style.text)}
    definitions.remove(style)
    svg=E.Element(N+'svg',{'viewBox':'0 0 1254 1254','width':'1254','height':'1254','class':f'chapter-illustration supplied-{scene.lower()}','role':'img','aria-labelledby':f'{scene}-title {scene}-desc'})
    titles={'P3':('Let the world push back','A fox watches an orange car approach a bend in a cream road.'),'P4':('Bring it back to people','A learner tries a laptop while a seated fox watches, its broad tail in the foreground.')}
    sub(svg,'title',id=f'{scene}-title').text=titles[scene][0];sub(svg,'desc',id=f'{scene}-desc').text=titles[scene][1]
    sub(svg,'metadata').text=json.dumps({'source':file.relative_to(ROOT).as_posix(),'sha256':sha256(original).hexdigest(),'treatment':'Original paths and palette; named motion layers, local fills and hidden underpaint repairs. Source file unchanged.'})
    svg.append(definitions)
    paths=[deepcopy(p) for p in source if p.tag in {N+'path',N+'circle',N+'ellipse',N+'polygon'}]
    for i,p in enumerate(paths):
        for k,v in rules.get(p.get('class'),{}).items():p.set(k,v)
        p.attrib.pop('class',None);p.set('id',f'{scene}-path-{i}')
    # Every gradient identifier is scoped to the chapter, including its uses.
    ids={el.get('id'):f'{scene}-{el.get("id")}' for el in definitions.iter() if el.get('id')}
    for el in [*definitions.iter(),*paths]:
        for k,v in list(el.attrib.items()):
            if k=='id' and v in ids:el.set(k,ids[v])
            else:
                for before,after in ids.items():v=v.replace(f'url(#{before})',f'url(#{after})')
                el.set(k,v)
    return svg,definitions,paths

def group(scene,kind,pivot):
    return E.Element(N+'g',{'id':f'{scene}-{kind}','class':f'supplied-{scene.lower()}-{kind}','data-motion':kind,'style':f'transform-box:view-box;transform-origin:{pivot[0]}px {pivot[1]}px'})

def prepare_build():
    svg,defs,p=load('P3');assert len(p)==93
    # The traced road includes the car's outline in its cream underpaint. Restore
    # the short hidden road edge before the car travels, rather than exposing a
    # stationary cream silhouette behind it.
    commands=absolute(p[0].get('d'));assert abs(commands[19][1][-2]-243.52)<.02 and abs(commands[28][1][-2]-701.03)<.02
    commands=commands[:20]+[('C',[395,940,548,895,701.03,852.04])]+commands[29:]
    p[0].set('d',' '.join(c+' '.join(f'{v:.3f}' for v in vs) for c,vs in commands))
    car_indices=set(range(1,20))|{21,22,23,25,26,27,28,31,32,34}
    tail_indices=set(range(46,52));eye_indices={63,64,65}
    car=group('P3','car',(510,1050));tail=group('P3','tail',(778,412));eye=group('P3','eye',(1004,327))
    # Preserve painter order inside each movable group, with the road beneath.
    for i in sorted(car_indices):car.append(p[i])
    for i in sorted(tail_indices):tail.append(p[i])
    for i in sorted(eye_indices):eye.append(p[i])
    for i,path in enumerate(p):
        if i in car_indices|tail_indices|eye_indices:continue
        if i==52:svg.append(tail)
        if i==66:svg.append(eye)
        svg.append(path)
        if i==24:
            sub(svg,'path',id='P3-hidden-road-edge',fill='#9da88c',d='M243.52 983.73C395 940 548 895 701.03 852.04L717.41 872.4C554 914 398 977 243.52 1025Z')
        if i==45:svg.append(car)
    return svg

def prepare_return():
    svg,defs,p=load('P4');assert len(p)==85
    tail_indices={1,2,3,4,5,6,21};hand_indices={9,14,15,16,17,18,19}
    # The cream base was one compound silhouette spanning laptop, hand, desk
    # and tail. Split its native tail contour and restore the hidden desk edge;
    # otherwise the old tail/hand outline remains as a stationary cream halo.
    commands=absolute(p[0].get('d'))
    assert len(commands)==59
    def data(parts):return ' '.join(c+' '.join(f'{v:.3f}' for v in vs) for c,vs in parts)
    tail=group('P4','tail',(1007,1030))
    q=deepcopy(p[0]);q.set('id','P4-tail-cream')
    q.set('d',data([('M',[943.69,835.24])]+commands[34:49]+[('Z',[])]));tail.append(q)
    for i in sorted(tail_indices):tail.append(p[i])
    desk=commands[:12]+[('L',[440,820]),('L',[635.27,781.72])]+commands[21:31]+[('C',[840,835,650,864,520.92,904.11])]+commands[49:]
    p[0].set('d',data(desk))
    hand=group('P4','typing',(631,759))
    for i in sorted(hand_indices):hand.append(p[i])
    for i,path in enumerate(p):
        if i==9:
            # A small skin overlap stays under the shirt and moving wrist.
            sub(svg,'path',id='P4-wrist-underlap',fill='#fdba81',d='M430 706C452 693 470 682 488 694C510 704 527 716 548 716L630 714L637 738L435 730Z')
            svg.append(hand)
        if i==25:svg.append(tail)
        if i not in tail_indices|hand_indices:svg.append(path)
    return svg

def main():
    for name,svg in [('build-authored',prepare_build()),('return-authored',prepare_return())]:
        E.indent(svg,space='  ')
        out=ROOT/f'assets/art/scene-{name}.svg';out.write_text(E.tostring(svg,encoding='unicode')+'\n')
        assert not list(svg.iter(N+'image')) and not list(svg.iter(N+'style'))
        print(out.relative_to(ROOT))
if __name__=='__main__':main()

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

def flex_tail(tail, anchor, reach, amount):
    """Bend only the free end; every control point at the attachment stays exact.

    Matching command topology makes CSS interpolate smoothly. Unsupported CSS
    path animation falls back to the untouched d attribute, not a broken rig.
    """
    for path in tail:
        commands=absolute(path.get('d'))
        def bent(sign):
            result=[]
            for command,values in commands:
                values=values[:]
                for j in range(0,len(values),2):
                    t=max(0,min(1,(anchor-values[j])/reach))
                    values[j+1]+=sign*amount*t*t*(3-2*t)
                result.append(command+' '.join(f'{v:.3f}' for v in values))
            return ' '.join(result)
        # Subpixel overlap prevents anti-alias seams between adjacent colour planes.
        path.set('stroke',path.get('fill'))
        path.set('stroke-width','0.8')
        path.set('stroke-linejoin','round')
        path.set('paint-order','stroke fill')
        path.set('class','authored-tail-flex')
        path.set('style',f'--tail-rest:path("{bent(0)}");--tail-up:path("{bent(-1)}");--tail-down:path("{bent(1)}")')
    tail.set('data-fixed-root-x',str(anchor))

def decorations(svg, scene):
    # One quiet line language: open contours, small nodes, leaf-like terminals.
    # All secondary motion lives on new art, behind the unchanged source paths.
    g=E.Element(N+'g',{'id':scene+'-ornament','fill':'none','stroke':'#b78351','stroke-width':'3.2','stroke-linecap':'round','stroke-linejoin':'round','aria-hidden':'true'})
    svg.insert(list(svg).index(svg.find(N+'defs'))+1,g)
    if scene=='P3':
        sub(g,'path',d='M152 637C109 448 182 164 442 136C637 111 760 220 813 290',opacity='.34')
        sub(g,'path',d='M158 568C141 367 265 191 459 176',stroke_dasharray='2 15',opacity='.5')
        route='M151 644C115 458 189 169 444 138'
        sub(g,'path',d=route,stroke='#c7713b',stroke_width=3.2,pathLength=1,stroke_dasharray='.10 .90',class_='ornament-traveller',opacity='.7')
        for x,y,r in [(150,643,6),(180,350,4),(445,138,5)]:
            sub(g,'circle',cx=x,cy=y,r=r,fill='#f7f5ed',opacity='.8')
        sub(g,'circle',cx=445,cy=138,r=15,class_='ornament-pulse',style='transform-box:fill-box;transform-origin:center',opacity='.35')
        sprig=sub(g,'g',class_='ornament-sprig',style='transform-box:view-box;transform-origin:270px 719px')
        sub(sprig,'path',d='M270 719C258 685 239 649 211 631M252 683C224 684 211 669 210 654C231 651 247 661 252 683M237 660C240 635 233 618 217 612C207 630 214 650 237 660',opacity='.6')
        sub(g,'path',d='M771 858C829 821 859 789 863 750M786 873C846 835 881 791 884 758',opacity='.48',class_='ornament-current')
        sub(g,'path',d='M827 747L837 727L848 748M191 201V225M179 213H203',opacity='.55')
    else:
        # A single open loop joins the space above the learner to the fox;
        # dashes carry the idea onward without drawing another literal UI.
        sub(g,'path',d='M82 421C13 246 128 92 291 93C327 93 356 101 383 117',opacity='.35')
        sub(g,'path',d='M794 130C923 93 1133 149 1178 300',opacity='.4')
        sub(g,'path',d='M831 165C977 139 1096 209 1118 275',stroke_dasharray='2 14',opacity='.48')
        sub(g,'path',d='M794 130C923 93 1133 149 1178 300',pathLength=1,stroke_dasharray='.12 .88',stroke_width=3.2,class_='ornament-traveller',opacity='.75')
        sub(g,'circle',cx=794,cy=130,r=5,fill='#c7713b',stroke='none')
        sub(g,'circle',cx=1178,cy=300,r=7,opacity='.7')
        sub(g,'circle',cx=1178,cy=300,r=18,class_='ornament-pulse',style='transform-box:fill-box;transform-origin:center',opacity='.3')
        sprig_space=sub(g,'g',id='P4-sprig-space',transform='translate(-18 95)')
        sprig=sub(sprig_space,'g',class_='ornament-sprig',style='transform-box:view-box;transform-origin:214px 1040px')
        sub(sprig,'path',d='M214 1040C239 1012 245 982 238 950M232 1013C207 1011 193 995 196 980C218 981 231 993 232 1013M241 986C263 974 269 956 260 943C242 951 237 968 241 986',opacity='.65')
        sub(g,'path',d='M261 1049C310 1076 357 1079 402 1068M273 1068C323 1095 370 1094 415 1081',class_='ornament-current',opacity='.42')
        sub(g,'path',d='M129 289V313M117 301H141M1066 82V102M1056 92H1076',opacity='.55')
    for node in g.iter():
        if node.get('opacity'):node.set('opacity',str(min(.85,float(node.get('opacity'))*1.3)))
        if 'class-' in node.attrib:node.set('class',node.attrib.pop('class-'))

def prepare_build():
    svg,defs,p=load('P3');assert len(p)==93
    # The traced road includes the car's outline in its cream underpaint. Restore
    # the short hidden road edge before the car travels, rather than exposing a
    # stationary cream silhouette behind it.
    commands=absolute(p[0].get('d'));assert abs(commands[19][1][-2]-243.52)<.02 and abs(commands[28][1][-2]-701.03)<.02
    commands=commands[:20]+[('C',[395,940,548,895,701.03,852.04])]+commands[29:]
    p[0].set('d',' '.join(c+' '.join(f'{v:.3f}' for v in vs) for c,vs in commands))
    car_indices=set(range(1,20))|{21,22,23,25,26,27,28,30,31,32,34}
    tail_indices=set(range(46,52));eye_indices={63,64,65}
    car=group('P3','car',(510,1050));tail=group('P3','tail',(778,412));eye=group('P3','eye',(1007,327.5))
    # Preserve painter order inside each movable group, with the road beneath.
    for i in sorted(car_indices):car.append(p[i])
    for i in sorted(tail_indices):tail.append(p[i])
    for i in sorted(eye_indices):eye.append(p[i])
    flex_tail(tail,730,380,27)
    decorations(svg,'P3')
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
    desk=commands[:12]+[('L',[440,820]),('L',[635.27,781.72])]+commands[21:31]+[('C',[840,930,650,933,520.92,904.11])]+commands[49:]
    p[0].set('d',data(desk))
    flex_tail(tail,920,430,23)
    decorations(svg,'P4')
    hand=group('P4','typing',(631,759))
    # The exported skin silhouette also spans the keyboard. Extract the skin
    # using its original keyboard contour, then move that contour with the hand.
    # Keeping it on the static keyboard used to shear off fingers during a tap.
    hand_mask=sub(defs,'mask',id='P4-hand-skin-mask',maskUnits='userSpaceOnUse',x=410,y=675,width=245,height=180,style='mask-type:luminance')
    sub(hand_mask,'rect',x=410,y=675,width=245,height=110,fill='white')
    keyboard_cut=deepcopy(p[10]);keyboard_cut.attrib.pop('id');keyboard_cut.set('fill','black');hand_mask.append(keyboard_cut)
    cuff_clip=sub(defs,'clipPath',id='P4-hand-attachment-clip',clipPathUnits='userSpaceOnUse')
    sub(cuff_clip,'rect',x=410,y=675,width=245,height=63)
    cuff=deepcopy(p[9]);cuff.set('id','P4-hand-attachment');cuff.set('clip-path','url(#P4-hand-attachment-clip)')
    p[9].set('mask','url(#P4-hand-skin-mask)')
    for i in sorted(hand_indices):hand.append(p[i])
    for i,path in enumerate(p):
        if i==9:
            svg.append(cuff)
            # A small skin overlap stays under the shirt and moving wrist.
            sub(svg,'path',id='P4-wrist-underlap',fill='#fdba81',d='M430 706C452 693 470 682 488 694C510 704 527 716 548 716L630 714L637 738L435 730Z')
            # Continue the real keyboard under the fingertips, with no fixed
            # skin silhouettes. Only this normally hidden region is repaired.
            sub(svg,'path',id='P4-keyboard-under-fingers',fill='#838d77',d='M440 747L479 741L514 753L519 775L449 792Z')
        if i==14:svg.append(hand)
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

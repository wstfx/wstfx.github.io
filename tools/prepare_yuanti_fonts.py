"""Build Chinese-only Yuanti SC WOFF2 subsets; --check needs only Python stdlib.

Conversion requires fonttools[woff]. Source is the owner's installed Yuanti.ttc.
The source's embedding flags and copyright are preserved; this utility does not
establish a public web-distribution license. See assets/fonts/yuanti/provenance.json.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/fonts/yuanti'
RANGES = ((0x2E80,0x303F),(0x31C0,0x31EF),(0x3400,0x4DBF),(0x4E00,0x9FFF),
          (0xF900,0xFAFF),(0xFE10,0xFE1F),(0xFE30,0xFE4F),(0xFF00,0xFFEF),(0x20000,0x3FFFF))

def used_characters():
    paths = list(ROOT.glob('*.html')) + list((ROOT/'work').glob('*.html')) + list((ROOT/'sharing').glob('*.html'))
    for folder in ('content', 'assets/js', 'assets/css'):
        paths += [p for p in (ROOT/folder).rglob('*') if p.suffix in ('.html','.json','.js','.css')]
    text = '\n'.join(html.unescape(p.read_text()) for p in paths)
    # JavaScript/JSON may contain escaped Chinese characters.
    text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1],16)), text)
    return sorted({ord(c) for c in text if any(lo <= ord(c) <= hi for lo,hi in RANGES)})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    wanted=used_characters()
    if args.check:
        data=json.loads((OUT/'provenance.json').read_text())
        missing=set(wanted)-set(data['codepoints'])
        if missing:
            raise SystemExit('Yuanti subset needs updating for: '+''.join(chr(n) for n in sorted(missing))+'\nRun tools/prepare_yuanti_fonts.py with fonttools[woff] available.')
        for face in data['faces']:
            p=OUT/face['file']
            if hashlib.sha256(p.read_bytes()).hexdigest()!=face['sha256']:
                raise SystemExit('Font asset changed: '+str(p))
        print(f'PASS: Yuanti subsets cover all {len(wanted)} current Chinese characters and punctuation; font hashes match.')
        return
    from fontTools.ttLib import TTFont
    from fontTools import subset
    candidates=list(Path('/System/Library/AssetsV2').glob('com_apple_MobileAsset_Font*/*/AssetData/Yuanti.ttc'))
    source=args.source or (candidates[0] if candidates else None)
    if source is None or not source.is_file():
        raise SystemExit('Specify --source /path/to/Yuanti.ttc')
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={'family':'Yuanti SC / 圆体-简','source_filename':source.name,
              'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'copyright':'© 2010–2015 Changzhou SinoType Technology Co., Ltd. All rights reserved.',
              'embedding':'fsType 8: editable document embedding. Preserved in every subset. No separate public webfont redistribution authorization was found; verify before public distribution.',
              'references':['https://www.apple.com/legal/sla/docs/macOSTahoe.pdf','https://learn.microsoft.com/en-us/typography/opentype/spec/os2#fstype'],
              'codepoints':wanted,'faces':[]}
    for index,style in ((4,'Light'),(0,'Regular'),(2,'Bold')):
        font=TTFont(source,fontNumber=index,recalcTimestamp=False)
        family=font['name'].getDebugName(1)
        assert family=='Yuanti SC',family
        fs_type=font['OS/2'].fsType
        if fs_type & (0x2|0x100|0x200):
            raise SystemExit(f'Source embedding/subsetting restriction requires review: {fs_type}')
        missing=set(wanted)-set(font.getBestCmap())
        if missing:raise SystemExit('Source lacks: '+''.join(chr(n) for n in sorted(missing)))
        options=subset.Options()
        options.flavor='woff2'
        options.name_IDs=['*'];options.name_languages=['*'];options.name_legacy=True
        worker=subset.Subsetter(options=options);worker.populate(unicodes=wanted);worker.subset(font)
        assert font['OS/2'].fsType==fs_type
        font.flavor='woff2'
        output=OUT/f'YuantiSC-{style}.woff2';font.save(output);font.close()
        # Decode the actual output, checking Unicode coverage and preserved restrictions.
        check=TTFont(output)
        assert set(wanted)<=set(check.getBestCmap())
        assert check['OS/2'].fsType==fs_type
        check.close()
        manifest['faces'].append({'file':output.name,'style':style,'source_index':index,'fsType':fs_type,
                                  'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        print(output.relative_to(ROOT),output.stat().st_size,'bytes')
    (OUT/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    css_path=ROOT/'assets/css/type-system.css'
    css=css_path.read_text()
    for face in manifest['faces']:
        css=re.sub(re.escape(face['file'])+r'(?:\?v=[a-f0-9]+)?', face['file']+'?v='+face['sha256'][:10], css)
    css_path.write_text(css)
    version=hashlib.sha256(css_path.read_bytes()).hexdigest()[:10]
    for page in ROOT.rglob('*.html'):
        if '.git' in page.parts or 'content' in page.relative_to(ROOT).parts:continue
        old=page.read_text()
        new=re.sub(r'(assets/css/type-system\.css)(?:\?v=[a-zA-Z0-9]+)?',r'\1?v='+version,old)
        if new!=old:page.write_text(new)
    print(f'Exported {len(wanted)} Chinese characters and punctuation in 3 weights.')

if __name__=='__main__':main()

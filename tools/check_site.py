"""Check generated HTML paths and anchors against exact filesystem spelling."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.refs = path, set(), []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            assert attrs['id'] not in self.ids, f'Duplicate ID: {self.path}: {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag == 'img':
            assert 'alt' in attrs, f'Missing alt: {self.path}'
        for name in ['href', 'src', 'data-lightbox']:
            if attrs.get(name):
                self.refs.append(attrs[name])

pages = {p: Page(p) for p in ROOT.rglob('*.html') if '.git' not in p.parts and 'content' not in p.relative_to(ROOT).parts}
count = 0
for path, page in pages.items():
    for ref in page.refs:
        u = urlsplit(ref)
        if u.scheme or u.netloc:
            continue
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        assert target.is_file(), f'Missing path: {path.relative_to(ROOT)} → {ref}'
        folder = ROOT
        for part in target.relative_to(ROOT).parts:
            assert part in {p.name for p in folder.iterdir()}, f'Case mismatch: {ref}'
            folder = folder / part
        if u.fragment and target in pages:
            assert unquote(u.fragment) in pages[target].ids, f'Missing anchor: {path} → {ref}'
        count += 1
print(f'PASS: {len(pages)} HTML pages, {count} local references, exact filename casing, anchors and image alt attributes.')

# Font subset coverage must keep pace with newly authored Chinese copy.
import subprocess
import sys
subprocess.run([sys.executable, str(ROOT / 'tools/prepare_yuanti_fonts.py'), '--check'], check=True)

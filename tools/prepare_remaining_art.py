#!/usr/bin/env python3
"""Prepare supplied Build/Return PNGs as static editable SVG cleanup drafts.

Uses local vtracer==0.6.15 and the same Node/Sharp gradient fitting as the other
chapter conversions. No network, generation, bitmap retouching or motion rig.
PNG originals remain unchanged. Paths retain painter order and receive simple
regional labels; these labels are editing aids, not fully separated objects.

    /tmp/portfolio-vectorize-venv/bin/python tools/prepare_remaining_art.py \
        --node /path/to/node --sharp /path/to/node_modules/sharp
"""

from argparse import ArgumentParser
from hashlib import sha256
from importlib.metadata import version
import json
import re
import xml.etree.ElementTree as ET

from prepare_chapter_art import ART, ROOT, TAG, TRACE_OPTIONS, bounds, trace_pixels
from prepare_notice_art import fit_gradient, visible_samples


SCENES = {
    "build-road": {
        "hash": "a5f91829f04e3c596484ae2108921c08b5d833ea557d9638676a6eef07b26ec7",
        "trace_paths": 154,
        "title": "Let the world push back — editable road illustration",
        "description": "An orange car approaches a cone on a curved cream road while a fox looks back from the far end.",
    },
    "return-learning": {
        "hash": "27fa0a084174c500f36ac4ddd989f0df1e05f48b141adfd82e85da2735be629b",
        "trace_paths": 129,
        "title": "Bring it back to people — editable learning illustration",
        "description": "A learner works at a laptop while an orange fox watches from across the table, with its broad tail in the foreground.",
    },
}


def region_name(scene, index, path):
    """Conservative location labels; large shared trace bases remain explicit."""
    left, top, right, bottom = bounds(path)
    if index == 0:
        return "shared-underpaint"
    if scene == "build-road":
        if index == 1:
            return "shared-orange-underpaint"
        if top >= 775 and right < 780:
            return "car-area"
        if top >= 760 and left > 850 and right < 990:
            return "cone-area"
        if bottom < 745 and left >= 330:
            return "fox-and-foliage-area"
        return "road-and-shared-paint"
    if left >= 895 or (top >= 815 and left >= 475):
        return "fox-area"
    if left >= 330 and right < 670 and bottom < 555:
        return "learner-face-area"
    if left >= 610 and top >= 375 and bottom <= 806:
        return "learner-and-chair-area"
    if right <= 640 and top >= 540 and bottom <= 845:
        return "laptop-and-hands-area"
    if top >= 720 and bottom <= 975:
        return "table-and-sheet-area"
    return "shared-scene-paint"


def prepare(name, node, sharp):
    import vtracer
    assert version("vtracer") == "0.6.15"
    spec = SCENES[name]
    source = ART / f"chapter-sources/{name}.png"
    output = ART / f"scene-{name}.svg"
    original = source.read_bytes()
    assert sha256(original).hexdigest() == spec["hash"], "Review conversion when the source changes."
    pixels, size = trace_pixels(original)
    raw = ET.fromstring(vtracer.convert_pixels_to_svg(pixels, size, **TRACE_OPTIONS))
    paths = list(raw.iter(TAG("path")))
    assert len(paths) == spec["trace_paths"], "Review conversion when trace settings change."
    samples = visible_samples(paths, pixels, size, node, sharp)
    width, height = size
    prefix = f"art-{name}"
    svg = ET.Element(TAG("svg"), {
        "viewBox": f"0 0 {width} {height}", "width": str(width), "height": str(height),
        "class": f"chapter-illustration chapter-illustration-{name}",
        "role": "img", "aria-labelledby": f"{prefix}-title {prefix}-description",
    })
    ET.SubElement(svg, TAG("title"), {"id": f"{prefix}-title"}).text = spec["title"]
    ET.SubElement(svg, TAG("desc"), {"id": f"{prefix}-description"}).text = spec["description"]
    metadata = ET.SubElement(svg, TAG("metadata"), {"id": f"{prefix}-provenance"})
    definitions = ET.SubElement(svg, TAG("defs"))
    stack = ET.SubElement(svg, TAG("g"), {
        "id": f"{prefix}-editable-paint-stack", "data-name": "Editable paths — preserve painter order",
    })
    gradients, regions = [], {}
    art_path_count = 0
    for index, path in enumerate(paths):
        if not path.get("d", "").strip():
            continue
        art_path_count += 1
        region = region_name(name, index, path)
        regions[index] = region
        path.set("id", f"{prefix}-{index:03}-{region}")
        path.set("data-name", f"{index:03} {region.replace('-', ' ')}")
        path.set("data-region", region)
        gradient = fit_gradient(samples[index])
        if gradient:
            shift = [float(v) for v in re.findall(r"-?[\d.]+", path.get("transform", ""))]
            tx, ty = shift if len(shift) == 2 else (0, 0)
            (x1, y1), (x2, y2) = gradient["points"]
            identifier = f"{prefix}-gradient-{index:03}"
            paint = ET.SubElement(definitions, TAG("linearGradient"), {
                "id": identifier, "gradientUnits": "userSpaceOnUse",
                "x1": f"{x1-tx:.2f}", "y1": f"{y1-ty:.2f}",
                "x2": f"{x2-tx:.2f}", "y2": f"{y2-ty:.2f}",
            })
            for offset, color in zip(["0", "1"], gradient["colors"]):
                ET.SubElement(paint, TAG("stop"), {
                    "offset": offset, "stop-color": "#%02x%02x%02x" % tuple(color),
                })
            path.set("fill", f"url(#{identifier})")
            gradients.append(index)
        stack.append(path)
    metadata.text = json.dumps({
        "source": source.relative_to(ROOT).as_posix(), "source_sha256": spec["hash"],
        "source_unchanged": True, "source_size": list(size),
        "export_viewBox": f"0 0 {width} {height}",
        "purpose": "Static editable SVG for the user's manual Illustrator cleanup before animation.",
        "tracer": "vtracer", "version": "0.6.15", "options": TRACE_OPTIONS,
        "alpha_contour": "50%", "artwork_paths": art_path_count, "gradients": gradients,
        "gradient_method": "Least-squares RGB linear gradients fitted to visible source pixels.",
        "grouping": "One ordered editable paint stack. Regional labels assist selection; compound underpaint paths can span several subjects and are not separated semantic layers.",
        "regions": regions, "motion_rig": False, "face_replacement": False,
        "format": "Native SVG paths and gradients, no embedded raster image or external API.",
        "limits": "Simplified color planes and fitted shading approximate the supplied PNG. Trace edges, shared underpaint and regions remain available for manual cleanup. Original pose, face and framing are retained.",
    }, separators=(",", ":"))
    ET.indent(svg, space="  ")
    output.write_text(ET.tostring(svg, encoding="unicode") + "\n")
    assert source.read_bytes() == original
    assert not list(svg.iter(TAG("image")))
    print(f"{output.relative_to(ROOT)}: {width}×{height}, {art_path_count} paths, "
          f"{len(gradients)} gradients, {output.stat().st_size:,} bytes")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    parser.add_argument("--sharp", default="sharp")
    parser.add_argument("--scene", choices=SCENES, help="Convert only one scene; omitted converts both.")
    args = parser.parse_args()
    for name in ([args.scene] if args.scene else SCENES):
        prepare(name, args.node, args.sharp)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Trace approved concept PNGs to native SVG without changing the source PNG.

The build has no tracing dependency. To reproduce artwork preparation only:

    python3 -m venv /tmp/portfolio-vectorize-venv
    /tmp/portfolio-vectorize-venv/bin/python -m pip install \\
        --index-url https://pypi.org/simple vtracer==0.6.15
    /tmp/portfolio-vectorize-venv/bin/python tools/prepare_chapter_art.py \\
        assets/art/chapter-sources/notice.png --name notice

VTracer 0.6.15 is MIT licensed: https://pypi.org/project/vtracer/0.6.15/
Spline conversion is local; artwork is never uploaded to a tracing service.
Source RGB values are passed unchanged; the alpha contour uses a 50% threshold.
SVG paths, rather than raster retouching, are then grouped for animation.
Tracing is not an automatic
semantic rig: the small motion maps below are reviewed against rendered art.
"""

from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zlib


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "assets/art"
NS = "http://www.w3.org/2000/svg"
TAG = lambda name: f"{{{NS}}}{name}"
ET.register_namespace("", NS)

TRACE_OPTIONS = {
    "colormode": "color",
    "hierarchical": "stacked",
    "mode": "spline",
    "filter_speckle": 4,
    "color_precision": 6,
    "layer_difference": 16,
    "corner_threshold": 60,
    "length_threshold": 4.0,
    "max_iterations": 10,
    "splice_threshold": 45,
    "path_precision": 2,
}

# Maps are intentionally explicit and source-hash locked. Each contains a
# source hash, semantic path indices, and optional exact-source eye replacement.
# A changed image or tracing preset must be reviewed before reusing a motion map.
SCENES = {
    "notice": {
        "title": "Start with someone",
        "description": "An orange fox and a seated person share a quiet conversation beside an open notebook.",
        "sha256": "5a43b082e1bb713c6086fe893d0d3a473852066ffb5e27e643443eadef0b45f3",
        "parts": {
            "fox-tail": [5, 6, 12, 14, 21, 22, 118, 122, 128, 136, 159],
            "paper": [50, 86],
        },
        "pivots": {"fox-tail": [337, 840], "paper": [710, 697]},
        "occlusion_masks": [{"part": "fox-tail", "paths": [0, 1]}],
        "eye": {
            "remove_paths": [79, 91, 119, 124, 129, 150],
            "transform": "translate(638 454) rotate(-25) scale(.83) translate(-824 -405)",
            "pivot": [638, 454],
        },
    },
    "build": {
        "title": "Let the world push back",
        "description": "An orange fox tests a model car on a small curved road beside a traffic cone.",
        "sha256": "7fdafc268414437fb6ef127fe3c0a81b05f2185cf5957fe3faf653b6de309234",
        "parts": {
            "fox-tail": [4, 5, 9, 12, 14, 18, 86, 96, 103, 112, 113, 119],
            "car": [24, 45, 51, 52, 55, 56, 57, 58, 61, 65, 67, 68, 69, 70,
                    71, 72, 74, 79, 80, 82, 85, 87, 88, 90, 92, 93, 97, 105,
                    114, 120, 121],
        },
        "pivots": {"fox-tail": [426, 575], "car": [840, 975]},
        "occlusion_masks": [{
            "part": "fox-tail", "paths": [0],
            "keep_strokes": ["M426 562 C407 579 388 613 372 636"],
        }],
        "eye": {
            "remove_paths": [60, 75, 77, 91, 95, 98, 99, 101, 108],
            "transform": "translate(853 516) scale(1.35) translate(-824 -405)",
            "pivot": [853, 516],
        },
    },
    "return": {
        "title": "Bring it back to people",
        "description": "An orange fox shares a classroom activity with two learners at a laptop.",
        "sha256": "44b718abe2bbf4e0588f1586da99e62e1a8d8401ba1284d237cdc6b64bd1fc5f",
        "parts": {
            "fox-tail": [7, 11, 14, 22, 23, 28, 145, 154, 162, 187],
            "gesture": [50, 103, 127, 139],
        },
        "pivots": {"fox-tail": [270, 761], "gesture": [672, 617]},
        "occlusion_masks": [{"part": "fox-tail", "paths": [1]},
                            {"part": "gesture", "paths": [0, 2]}],
        "eye": {
            "remove_paths": [121, 140, 144, 156, 177, 178, 214],
            "transform": "translate(550 412) rotate(-12) scale(.92) translate(-824 -405)",
            "pivot": [550, 412],
        },
    },
    "test": {
        "title": "Give curiosity something to push against",
        "description": "An orange fox inspects a model landscape through a magnifying glass, studying one highlighted sample.",
        "sha256": "0617d47b03a66dd05d1d8e1a57c70b86a2ac2c00baad0693ff19234013a9fe51",
        "parts": {
            "fox-tail": [4, 6, 9, 17, 20, 23, 67, 78, 97, 110, 112, 122, 139, 152],
            "pin": [46, 58, 60, 75, 80, 88, 90, 101, 146],
        },
        "pivots": {"fox-tail": [424, 640], "pin": [1017, 655]},
        "occlusion_masks": [{
            "part": "fox-tail", "paths": [0, 1],
            "keep_strokes": ["M424 636 C408 660 397 690 386 722"],
        }],
        "eye": {
            "remove_paths": [55, 64, 77, 111, 136, 142, 163],
            "transform": "translate(893 480) scale(1.16) translate(-824 -405)",
            "pivot": [893, 480],
        },
    },
}


def png_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Expected an unmodified PNG concept source.")
    return struct.unpack(">II", data[16:24])


def trace_pixels(data: bytes) -> tuple[list[tuple[int, int, int, int]], tuple[int, int]]:
    """Decode RGBA PNG and interpret its alpha as a vector silhouette.

    The source and its RGB values remain untouched. VTracer needs binary alpha:
    generated antialiased PNGs can have RGB data in almost invisible pixels.
    A 50% alpha contour represents the visible boundary without tracing those
    hidden colors as stray shapes. This creates no modified raster file.
    """
    width, height = png_size(data)
    bit_depth, color_type, _, _, interlace = struct.unpack("5B", data[24:29])
    if (bit_depth, color_type, interlace) != (8, 6, 0):
        raise ValueError("This preparation script expects noninterlaced 8-bit RGBA PNG.")
    chunks = []
    cursor = 8
    while cursor < len(data):
        size = struct.unpack(">I", data[cursor:cursor + 4])[0]
        kind = data[cursor + 4:cursor + 8]
        if kind == b"IDAT":
            chunks.append(data[cursor + 8:cursor + 8 + size])
        cursor += size + 12
    stream = zlib.decompress(b"".join(chunks))
    stride = width * 4
    assert len(stream) == height * (stride + 1)
    previous = bytearray(stride)
    pixels = []
    for y in range(height):
        start = y * (stride + 1)
        method = stream[start]
        row = bytearray(stream[start + 1:start + stride + 1])
        for x in range(stride):
            left = row[x - 4] if x >= 4 else 0
            above = previous[x]
            upper_left = previous[x - 4] if x >= 4 else 0
            if method == 1:
                row[x] = (row[x] + left) & 255
            elif method == 2:
                row[x] = (row[x] + above) & 255
            elif method == 3:
                row[x] = (row[x] + (left + above) // 2) & 255
            elif method == 4:
                prediction = left + above - upper_left
                distances = [abs(prediction - value) for value in (left, above, upper_left)]
                predictor = (left, above, upper_left)[distances.index(min(distances))]
                row[x] = (row[x] + predictor) & 255
            elif method != 0:
                raise ValueError("Unsupported PNG filter.")
        for x in range(0, stride, 4):
            r, g, b, alpha = row[x:x + 4]
            pixels.append((r, g, b, 255) if alpha >= 128 else (0, 0, 0, 0))
        previous = row
    return pixels, (width, height)


def bounds(shape: ET.Element) -> tuple[float, float, float, float]:
    """Conservative control-hull bounds of VTracer's absolute spline output."""
    data = shape.get("d", "")
    if re.search(r"[a-zA-BD-KN-Y]", data):
        raise ValueError("Review path bounds: expected absolute M, L, C and Z only.")
    values = [float(x) for x in re.findall(r"-?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", data)]
    if len(values) % 2:
        raise ValueError("Unexpected coordinate count in traced path.")
    xs, ys = values[0::2], values[1::2]
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    tx = ty = 0.0
    if transform := shape.get("transform"):
        match = re.fullmatch(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)", transform)
        if not match:
            raise ValueError(f"Review unsupported traced transform: {transform}")
        tx, ty = map(float, match.groups())
    return (round(min(xs) + tx, 2), round(min(ys) + ty, 2),
            round(max(xs) + tx, 2), round(max(ys) + ty, 2))


def apply_source_eye(svg: ET.Element, name: str, setting: dict) -> None:
    """Insert all four original eye paths with a reviewed affine transform."""
    source = ET.parse(ART / "fox-workbench.svg").getroot()
    x, y = setting["pivot"]
    outer = ET.SubElement(svg, TAG("g"), {
        "id": f"art-{name}-approved-eye", "class": "chapter-part scene-fox-eye",
        "data-part": "fox-eye", "style": f"transform-box:view-box;transform-origin:{x}px {y}px",
    })
    group = ET.SubElement(outer, TAG("g"), {"transform": setting["transform"]})
    for index in range(172, 176):
        path = deepcopy(source.find(f".//{TAG('path')}[@id='fw-path-{index}']"))
        path.set("id", f"art-{name}-approved-eye-{index - 172}")
        group.append(path)


def prepare(source: Path, name: str, title: str, description: str, inspect: bool) -> None:
    try:
        import vtracer
    except ImportError as error:
        raise SystemExit("Use the isolated VTracer environment described in this file.") from error
    if version("vtracer") != "0.6.15":
        raise SystemExit("Reproducible artwork preparation requires vtracer==0.6.15.")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise SystemExit("Use a lowercase scene name with letters, numbers and hyphens.")
    source = source.resolve()
    original = source.read_bytes()
    digest = sha256(original).hexdigest()
    width, height = png_size(original)
    spec = SCENES.get(name, {})
    title = title or spec.get("title", "A fox follows a question")
    description = description or spec.get("description", "A geometric orange fox in a project-inspired scene.")
    if spec and digest != spec["sha256"]:
        raise SystemExit("The source changed. Review the path map before applying it.")
    pixels, size = trace_pixels(original)
    raw = ET.fromstring(vtracer.convert_pixels_to_svg(pixels, size, **TRACE_OPTIONS))
    paths = list(raw.iter(TAG("path")))
    if inspect:
        print(json.dumps([
            {"index": index, "fill": path.get("fill"), "bounds": bounds(path),
             "bytes": len(path.get("d", ""))}
            for index, path in enumerate(paths)
        ], indent=2))
        return
    svg = ET.Element(TAG("svg"), {
        "viewBox": f"0 0 {width} {height}",
        "class": f"chapter-illustration chapter-illustration-{name}",
        "role": "img", "aria-labelledby": f"art-{name}-title art-{name}-description",
    })
    ET.SubElement(svg, TAG("title"), {"id": f"art-{name}-title"}).text = title
    ET.SubElement(svg, TAG("desc"), {"id": f"art-{name}-description"}).text = description
    metadata = ET.SubElement(svg, TAG("metadata"), {"id": f"art-{name}-provenance"})
    try:
        source_label = source.relative_to(ROOT).as_posix()
    except ValueError:
        source_label = source.name
    metadata.text = json.dumps({
        "source": source_label, "source_sha256": digest,
        "source_unchanged": True, "tracer": "vtracer", "version": "0.6.15",
        "tracer_license": "MIT", "options": TRACE_OPTIONS,
        "alpha_contour": "50% alpha threshold for vector silhouette; source RGB unchanged.",
        "format": "Native SVG spline paths; no embedded raster image.",
        "grouping": "Reviewed semantic fragments retain original painter order.",
        "paths_before_edit": len(paths),
        "path_map": spec.get("parts", {}),
        "eye_replacement": spec.get("eye"),
        "occlusion_masks": spec.get("occlusion_masks", []),
    }, separators=(",", ":"))
    # Stacked traces contain a base silhouette underneath later color planes.
    # Exclude each moving part from that base, or it would leave a colored ghost
    # at the rest position. These masks alter vector compositing only.
    for mask_spec in spec.get("occlusion_masks", []):
        mask_id = f"art-{name}-exclude-{mask_spec['part']}"
        definitions = svg.find(TAG("defs"))
        if definitions is None:
            definitions = ET.SubElement(svg, TAG("defs"))
        mask = ET.SubElement(definitions, TAG("mask"), {
            "id": mask_id, "maskUnits": "userSpaceOnUse", "maskContentUnits": "userSpaceOnUse",
            "x": "0", "y": "0", "width": str(width), "height": str(height),
            "style": "mask-type:luminance",
        })
        ET.SubElement(mask, TAG("rect"), {"width": str(width), "height": str(height), "fill": "white"})
        for index in spec["parts"][mask_spec["part"]]:
            shape = deepcopy(paths[index])
            shape.set("fill", "black")
            shape.set("stroke", "black")
            shape.set("stroke-width", "4")
            mask.append(shape)
        # Keep a narrow strip of the original body under tail/body joints.
        # This underlap closes the antialias seam at rest and during the reviewed
        # ±2.5-degree swing, while never drawing outside the source silhouette.
        for joint in mask_spec.get("keep_strokes", []):
            ET.SubElement(mask, TAG("path"), {
                "d": joint, "fill": "none", "stroke": "white",
                "stroke-width": "14", "stroke-linecap": "round",
            })
        for index in mask_spec["paths"]:
            paths[index].set("mask", f"url(#{mask_id})")
    part_map = {}
    for part, indices in spec.get("parts", {}).items():
        for index in indices:
            if index in part_map or index >= len(paths):
                raise ValueError("Invalid or overlapping reviewed path map.")
            part_map[index] = part
    skip = set(spec.get("eye", {}).get("remove_paths", []))
    skip.update(spec.get("remove_paths", []))
    counts = defaultdict(int)
    current_part = None
    group = None
    for index, path in enumerate(paths):
        if index in skip:
            continue
        part = part_map.get(index, "still")
        if part != current_part:
            counts[part] += 1
            attrs = {
                "id": f"art-{name}-{part}-{counts[part]:02}",
                "class": f"chapter-part scene-{part}", "data-part": part,
            }
            if pivot := spec.get("pivots", {}).get(part):
                attrs["style"] = f"transform-box:view-box;transform-origin:{pivot[0]}px {pivot[1]}px"
            group = ET.SubElement(svg, TAG("g"), attrs)
            current_part = part
        path.set("id", f"art-{name}-path-{index:04}")
        path.set("data-trace-path", str(index))
        if mask := path.attrib.pop("mask", None):
            # Keep root-coordinate masks outside the path's local translate().
            wrapper = ET.SubElement(group, TAG("g"), {"mask": mask})
            wrapper.append(path)
        else:
            group.append(path)
    if "eye" in spec:
        apply_source_eye(svg, name, spec["eye"])
    output = ART / f"scene-{name}.svg"
    ET.indent(svg, space="  ")
    output.write_text(ET.tostring(svg, encoding="unicode") + "\n")
    assert source.read_bytes() == original, "Concept sources must remain untouched."
    assert not list(svg.iter(TAG("image"))), "Production output must be native SVG."
    print(f"{output.relative_to(ROOT)}: {width}×{height}, {len(paths)} traced paths, "
          f"{len(list(svg.iter(TAG('path'))))} output paths, {output.stat().st_size:,} bytes")


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--title")
    parser.add_argument("--description")
    parser.add_argument("--inspect", action="store_true", help="Print path bounds for review instead of writing output.")
    args = parser.parse_args()
    prepare(args.source, args.name, args.title, args.description, args.inspect)


if __name__ == "__main__":
    main()

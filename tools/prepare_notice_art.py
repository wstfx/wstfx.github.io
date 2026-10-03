#!/usr/bin/env python3
"""Convert the supplied close-up PNG into native SVG paths and linear gradients.

Uses the isolated vtracer==0.6.15 environment described in prepare_chapter_art.py.
Gradient fitting additionally uses Node + Sharp (pass --node and --sharp when
they are supplied by the workspace runtime). No network/API or raster edits.
The PNG remains byte-for-byte unchanged; gradients are fitted from its visible
RGB values inside traced color planes, not from a newly generated image.

    /tmp/portfolio-vectorize-venv/bin/python tools/prepare_notice_art.py
"""

from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from importlib.metadata import version
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from prepare_chapter_art import ART, ROOT, TAG, TRACE_OPTIONS, trace_pixels


PREFIX = "art-notice-closeup"
SOURCE = ART / "chapter-sources/notice-closeup.png"
OUTPUT = ART / "scene-notice-closeup.svg"
SOURCE_HASH = "108816e319f8800492c61e9588661fbbab14621ec34049074ddb4a03c4358016"
# Both eyes are the incoming image's geometry, never substituted with a side eye.
# Fragment wrappers preserve painter order, including tiny antialias color planes.
EYES = {
    "near": {"pivot": (848, 444), "paths": [36, 43, 56, 65, 84, 85, 91, 94, 95, 98, 108]},
    "far": {"pivot": (755, 388), "paths": [42, 49, 51, 55, 60, 73, 88, 103, 109]},
}


def solve(matrix, vector):
    """Small pivoted linear solve, keeping artwork preparation dependency-light."""
    a = [list(row) + [value] for row, value in zip(matrix, vector)]
    for column in range(3):
        pivot = max(range(column, 3), key=lambda row: abs(a[row][column]))
        a[column], a[pivot] = a[pivot], a[column]
        if abs(a[column][column]) < 1e-8:
            return None
        divisor = a[column][column]
        a[column] = [value / divisor for value in a[column]]
        for row in range(3):
            if row != column:
                multiplier = a[row][column]
                a[row] = [x - multiplier * y for x, y in zip(a[row], a[column])]
    return [row[-1] for row in a]


def fit_gradient(samples):
    if len(samples) < 100:
        return None
    # Normalize coordinates so the fit stays well-conditioned.
    n = len(samples)
    cx = sum(p[0] for p in samples) / n
    cy = sum(p[1] for p in samples) / n
    rows = [(1, (p[0] - cx) / 500, (p[1] - cy) / 500) for p in samples]
    matrix = [[sum(row[i] * row[j] for row in rows) for j in range(3)] for i in range(3)]
    channels = [solve(matrix, [sum(row[i] * p[2 + c] for row, p in zip(rows, samples))
                              for i in range(3)]) for c in range(3)]
    if any(channel is None for channel in channels):
        return None
    # A native SVG linear gradient has one common direction for all channels.
    # Use the principal direction of the three fitted RGB slope vectors.
    xx = sum(c[1] ** 2 for c in channels)
    xy = sum(c[1] * c[2] for c in channels)
    yy = sum(c[2] ** 2 for c in channels)
    angle = .5 * math.atan2(2 * xy, xx - yy)
    dx, dy = math.cos(angle), math.sin(angle)
    projections = [(p[0] - cx) * dx + (p[1] - cy) * dy for p in samples]
    low, high = min(projections), max(projections)
    if high - low < 20:
        return None
    slopes = [(c[1] * dx + c[2] * dy) / 500 for c in channels]
    flat_error = sum((p[2 + c] - channels[c][0]) ** 2 for p in samples for c in range(3))
    fitted_error = sum((p[2 + c] - channels[c][0] - slopes[c] * t) ** 2
                       for p, t in zip(samples, projections) for c in range(3))
    if flat_error / (n * 3) < 3 or fitted_error > flat_error * .7:
        return None
    colors = [[max(0, min(255, round(c[0] + slope * t)))
               for c, slope in zip(channels, slopes)] for t in [low, high]]
    return {"points": [(cx + dx * t, cy + dy * t) for t in [low, high]], "colors": colors}


def visible_samples(paths, pixels, size, node, sharp):
    """Rasterize vector IDs only to locate visible samples in the original PNG."""
    width, height = size
    id_svg = ET.Element(TAG("svg"), {"width": str(width), "height": str(height)})
    lookup = {}
    for i, path in enumerate(paths):
        color = ((47 + i * 71) % 256, (89 + i * 113) % 256, (131 + i * 157) % 256)
        lookup[color] = i
        marker = deepcopy(path)
        marker.set("fill", "#%02x%02x%02x" % color)
        id_svg.append(marker)
    with tempfile.TemporaryDirectory(prefix="notice-vector-") as directory:
        svg_file, raw_file = Path(directory) / "ids.svg", Path(directory) / "ids.rgba"
        svg_file.write_text(ET.tostring(id_svg, encoding="unicode"))
        script = ("const sharp=require(process.argv[1]);const fs=require('fs');"
                  "sharp(process.argv[2]).ensureAlpha().raw().toBuffer()"
                  ".then(data=>fs.writeFileSync(process.argv[3],data));")
        subprocess.run([node, "-e", script, sharp, str(svg_file), str(raw_file)], check=True)
        mask = raw_file.read_bytes()
    samples = defaultdict(list)
    for y in range(2, height - 2, 3):
        for x in range(2, width - 2, 3):
            offset = (y * width + x) * 4
            color = tuple(mask[offset:offset + 3])
            if color not in lookup or mask[offset + 3] < 255:
                continue
            # Keep interior pixels so antialias blends do not pollute color fits.
            if any(mask[offset + shift:offset + shift + 3] != bytes(color)
                   for shift in [-8, 8, -8 * width, 8 * width]):
                continue
            r, g, b, alpha = pixels[y * width + x]
            if alpha:
                samples[lookup[color]].append((x, y, r, g, b))
    return samples


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    parser.add_argument("--sharp", default="sharp")
    args = parser.parse_args()
    import vtracer
    assert version("vtracer") == "0.6.15"
    original = SOURCE.read_bytes()
    assert sha256(original).hexdigest() == SOURCE_HASH, "Review maps when source changes."
    pixels, size = trace_pixels(original)
    traced = ET.fromstring(vtracer.convert_pixels_to_svg(pixels, size, **TRACE_OPTIONS))
    paths = list(traced.iter(TAG("path")))
    assert len(paths) == 114, "Review maps when trace changes."
    samples = visible_samples(paths, pixels, size, args.node, args.sharp)
    width, height = size
    svg = ET.Element(TAG("svg"), {
        "viewBox": f"0 0 {width} {height}",
        "class": "chapter-illustration chapter-illustration-notice-closeup",
        "role": "img", "aria-labelledby": f"{PREFIX}-title {PREFIX}-description",
    })
    ET.SubElement(svg, TAG("title"), {"id": f"{PREFIX}-title"}).text = "Start with someone"
    ET.SubElement(svg, TAG("desc"), {"id": f"{PREFIX}-description"}).text = (
        "A close-up orange fox looks attentively toward someone holding an open notebook, "
        "with one paw resting beside the pages.")
    metadata = ET.SubElement(svg, TAG("metadata"), {"id": f"{PREFIX}-provenance"})
    definitions = ET.SubElement(svg, TAG("defs"))
    gradient_indices = []
    part_by_index = {index: eye for eye, spec in EYES.items() for index in spec["paths"]}
    for index, path in enumerate(paths):
        path.set("id", f"{PREFIX}-path-{index:03}")
        path.set("data-trace-path", str(index))
        gradient = fit_gradient(samples[index]) if index not in part_by_index else None
        if gradient:
            shift = [float(v) for v in re.findall(r"-?[\d.]+", path.get("transform", ""))]
            tx, ty = shift if len(shift) == 2 else (0, 0)
            (x1, y1), (x2, y2) = gradient["points"]
            identifier = f"{PREFIX}-gradient-{index:03}"
            paint = ET.SubElement(definitions, TAG("linearGradient"), {
                "id": identifier, "gradientUnits": "userSpaceOnUse",
                "x1": f"{x1 - tx:.2f}", "y1": f"{y1 - ty:.2f}",
                "x2": f"{x2 - tx:.2f}", "y2": f"{y2 - ty:.2f}",
            })
            for offset, color in zip(["0", "1"], gradient["colors"]):
                ET.SubElement(paint, TAG("stop"), {
                    "offset": offset, "stop-color": "#%02x%02x%02x" % tuple(color),
                })
            path.set("fill", f"url(#{identifier})")
            gradient_indices.append(index)
        if index in part_by_index:
            eye = part_by_index[index]
            x, y = EYES[eye]["pivot"]
            group = ET.SubElement(svg, TAG("g"), {
                "id": f"{PREFIX}-eye-{eye}-{index:03}",
                "class": "chapter-part scene-fox-eye", "data-part": f"fox-eye-{eye}",
                "style": f"transform-box:view-box;transform-origin:{x}px {y}px",
            })
            group.append(path)
        else:
            svg.append(path)
    metadata.text = json.dumps({
        "source": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": SOURCE_HASH,
        "source_unchanged": True, "tracer": "vtracer", "version": "0.6.15",
        "options": TRACE_OPTIONS, "alpha_contour": "50%", "paths": len(paths),
        "gradients": gradient_indices,
        "gradient_method": "Least-squares RGB linear gradients fitted to visible source pixels.",
        "eye_groups": EYES, "eye_replacement": False,
        "format": "Native SVG spline paths and gradients; no raster image, API or generation.",
        "motion_boundary": "Both eyes only; the shared tail/body planes and hand remain still.",
    }, separators=(",", ":"))
    ET.indent(svg, space="  ")
    OUTPUT.write_text(ET.tostring(svg, encoding="unicode") + "\n")
    assert SOURCE.read_bytes() == original
    assert not list(svg.iter(TAG("image")))
    print(f"{OUTPUT.relative_to(ROOT)}: {width}×{height}, {len(paths)} paths, "
          f"{len(gradient_indices)} gradients, {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

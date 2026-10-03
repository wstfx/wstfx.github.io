#!/usr/bin/env python3
"""Locally convert the supplied overhead Test illustration to native SVG.

Uses vtracer==0.6.15, Node and Sharp, as in prepare_notice_art.py. The original
PNG stays byte-for-byte unchanged. The shared 50% alpha contour excludes faint
background-removal residue; it does not reconstruct hidden fox anatomy.

    /tmp/portfolio-vectorize-venv/bin/python tools/prepare_test_art.py \
        --node /path/to/node --sharp /path/to/node_modules/sharp
"""

from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from importlib.metadata import version
import json
import re
import xml.etree.ElementTree as ET

from prepare_chapter_art import ART, ROOT, TAG, TRACE_OPTIONS, trace_pixels
from prepare_notice_art import fit_gradient, visible_samples


PREFIX = "art-test-overhead"
SOURCE = ART / "chapter-sources/test-overhead.png"
OUTPUT = ART / "scene-test-overhead.svg"
SOURCE_HASH = "d534a98d6b0bd187c738af3314ff41839b5ad53b28aa82e1d8d4b93931bc0f22"
SAMPLE_PATHS = [37, 74]
# Preserve the supplied four separate dash shapes. Numbers follow the path from
# the lower existing sample toward the highlighted orange next measurement.
ROUTE_STEPS = {49: 0, 47: 1, 50: 2, 48: 3, 76: 3}
SAMPLE_PIVOT = (557, 544)
# Retain source-space coordinates while removing unused lower canvas. The lowest
# painted contour ends at y=1071, leaving a 39-unit margin in the exported crop.
EXPORT_VIEWBOX = "0 0 1254 1110"


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
    raw = ET.fromstring(vtracer.convert_pixels_to_svg(pixels, size, **TRACE_OPTIONS))
    paths = list(raw.iter(TAG("path")))
    assert len(paths) == 81, "Review maps when tracer output changes."
    samples = visible_samples(paths, pixels, size, args.node, args.sharp)
    width, height = size
    svg = ET.Element(TAG("svg"), {
        "viewBox": EXPORT_VIEWBOX,
        "class": "chapter-illustration chapter-illustration-test-overhead",
        "role": "img", "aria-labelledby": f"{PREFIX}-title {PREFIX}-description",
    })
    ET.SubElement(svg, TAG("title"), {"id": f"{PREFIX}-title"}).text = "Choose the next question"
    ET.SubElement(svg, TAG("desc"), {"id": f"{PREFIX}-description"}).text = (
        "Viewed from above, an orange fox reaches toward an orange measurement point "
        "on a cream and sage contour map. A dashed route connects it to an earlier sample.")
    metadata = ET.SubElement(svg, TAG("metadata"), {"id": f"{PREFIX}-provenance"})
    definitions = ET.SubElement(svg, TAG("defs"))

    # A stacked color trace puts the orange base beneath the cream map as well.
    # Remove that hidden base from the map region to avoid an orange antialias
    # hairline around a shape whose supplied perimeter is cream. No silhouette
    # is changed: the cream path still renders at its original traced boundary.
    mask_id = f"{PREFIX}-map-underpaint"
    mask = ET.SubElement(definitions, TAG("mask"), {
        "id": mask_id, "maskUnits": "userSpaceOnUse", "maskContentUnits": "userSpaceOnUse",
        "x": "0", "y": "0", "width": str(width), "height": str(height),
        "style": "mask-type:luminance",
    })
    ET.SubElement(mask, TAG("rect"), {"width": str(width), "height": str(height), "fill": "white"})
    map_region = deepcopy(paths[1])
    map_region.set("fill", "black")
    map_region.set("stroke", "black")
    map_region.set("stroke-width", "1")
    mask.append(map_region)

    gradients = []
    art_path_count = 0
    for index, path in enumerate(paths):
        if not path.get("d", "").strip():
            continue
        art_path_count += 1
        path.set("id", f"{PREFIX}-path-{index:03}")
        path.set("data-trace-path", str(index))
        gradient = fit_gradient(samples[index])
        if gradient:
            shift = [float(v) for v in re.findall(r"-?[\d.]+", path.get("transform", ""))]
            tx, ty = shift if len(shift) == 2 else (0, 0)
            (x1, y1), (x2, y2) = gradient["points"]
            identifier = f"{PREFIX}-gradient-{index:03}"
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

        parent = svg
        if index == 0:
            parent = ET.SubElement(svg, TAG("g"), {"mask": f"url(#{mask_id})"})
        elif index in SAMPLE_PATHS:
            x, y = SAMPLE_PIVOT
            parent = ET.SubElement(svg, TAG("g"), {
                "id": f"{PREFIX}-sample-point-{index:03}",
                "class": "chapter-part test-sample-point", "data-part": "selected-sample",
                "style": f"transform-box:view-box;transform-origin:{x}px {y}px",
            })
        elif index in ROUTE_STEPS:
            step = ROUTE_STEPS[index]
            parent = ET.SubElement(svg, TAG("g"), {
                "id": f"{PREFIX}-sample-route-{index:03}",
                "class": "chapter-part test-sample-route", "data-part": "sampling-route",
                "data-route-step": str(step), "style": f"--route-step:{step}",
            })
        parent.append(path)

    metadata.text = json.dumps({
        "source": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": SOURCE_HASH,
        "source_size": [width, height], "export_viewBox": EXPORT_VIEWBOX,
        "source_unchanged": True, "tracer": "vtracer", "version": "0.6.15",
        "options": TRACE_OPTIONS, "alpha_contour": "50%", "artwork_paths": art_path_count,
        "gradients": gradients,
        "gradient_method": "Least-squares RGB gradients fitted to visible source pixels.",
        "sample_paths": SAMPLE_PATHS, "sample_pivot": SAMPLE_PIVOT, "route_steps": ROUTE_STEPS,
        "route_motion": "Modest opacity emphasis only; the four supplied dashes are filled shapes, not a stroked path. Keep their position over the sage map underpaint.",
        "face_replacement": False,
        "cleanup": "Faint band between legs/tail falls below the shared alpha threshold. Original PNG unchanged. Orange hidden underpaint excluded from the cream map perimeter.",
        "format": "Native SVG paths, gradients and vector mask; no embedded raster image or API.",
        "motion_boundary": "Selected sample and original route dashes only. Fox anatomy, face, tail, contour map and existing measurement points stay still.",
    }, separators=(",", ":"))
    ET.indent(svg, space="  ")
    OUTPUT.write_text(ET.tostring(svg, encoding="unicode") + "\n")
    assert SOURCE.read_bytes() == original
    assert not list(svg.iter(TAG("image")))
    print(f"{OUTPUT.relative_to(ROOT)}: source {width}×{height}, export viewBox {EXPORT_VIEWBOX}, "
          f"{art_path_count} artwork paths, "
          f"{len(gradients)} gradients, {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

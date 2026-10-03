#!/usr/bin/env python3
"""Prepare the supplied Illustrator export without redrawing or reordering it.

The source's paths are not a rig: some traced shapes span several anatomical
parts. Small, independent details receive motion hooks, while connected shapes
remain static. Global path indices below are zero-based and ignore the ellipse.
Only the standard library is needed; IllustratorWorkspace is always read-only.
"""

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/IllustratorWorkspace/FoxHomepage_0.svg"
OUTPUT = ROOT / "assets/art/fox-workbench.svg"
NS = "http://www.w3.org/2000/svg"
TAG = lambda name: f"{{{NS}}}{name}"
ET.register_namespace("", NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

# Keep all geometry in its original root coordinates and painter order. A part
# may have several fragments because moving it in the document would change
# the appearance of overlapped shapes.
PARTS = {
    "fox-neck": [0, 1, 2],
    "fox-shoulder": [3, 40],
    "fox-throat": [11],
    "fox-muzzle": [12, 13],
    "fox-near-leg": [14],
    "fox-forepaw": [25, 137, 138, 139],
    "fox-body": [33, 34, 35, 36, 37, 43, 44],
    "fox-rear-legs": [45, 46, 47],
    "fox-tail": list(range(79, 86)),
    "fox-head": [133, 134, 135, 136, 141, 142, 143, 144],
    "fox-eye": [172, 173, 174, 175],
    "paper": [48, 54, 55, 56],
    "paper-curl": [111, 112, 113],
    "car": list(range(57, 79)),
    "ground": [140],
    "plant-near-fox": [26, 28, 29, 30, 31, 32],
    "plant-small": [38, 39, 41, 42],
    "plant-bench-base": [145, 151, 155, 156, 166, 171],
    "plant-roadside": [146, 150, 159, 160, 161, 162, 163, 167],
    "plant-vine-upper": [88, 89, 97, 103],
    "plant-vine-lower": [91, 93, 98, 116, 117, 118],
    "plant-vine-leaf-top": [154],
    "plant-vine-leaf-right": [152, 153],
    "plant-vine-leaf-middle": [157],
    "brush-tall": [147, 148, 149],
    "brush-small": [164, 165, 168],
    "pencil": [158, 169, 170],
}

# Animation origins are root-space attachment points, not bounding-box centers.
# Only these independently isolated details are safe for restrained motion.
PIVOTS = {
    "fox-tail": (426, 569),
    "fox-forepaw": (770, 512),
    "fox-eye": (824, 405),
    "paper-curl": (1028, 597),
    "car": (1040, 1052),
    "plant-vine-leaf-top": (1161, 520),
    "plant-vine-leaf-right": (1176, 529),
    "plant-vine-leaf-middle": (1198, 565),
}

FOX_PATHS = sorted(
    index for part, indices in PARTS.items() if part.startswith("fox-") for index in indices
)


def prepare() -> None:
    original_bytes = SOURCE.read_bytes()
    original = ET.fromstring(original_bytes)
    assert original.attrib["viewBox"] == "0 0 1298 1212"
    source_paths = list(original.iter(TAG("path")))
    assert len(source_paths) == 176, "The source changed; review its semantic map."
    source_shapes = [e for e in original.iter() if e.tag in {TAG("path"), TAG("ellipse")}]
    assert len(source_shapes) == 177
    for group in original.iter(TAG("g")):
        assert not (set(group.attrib) - {"id", "data-name"}), "Review inherited group attributes."

    definitions = deepcopy(original.find(TAG("defs")))
    rules = defaultdict(dict)
    for style in list(definitions.findall(TAG("style"))):
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]+)\}", style.text or ""):
            declarations = dict(re.findall(r"([\w-]+)\s*:\s*([^;]+);?", body))
            for selector in selectors.split(","):
                rules[selector.strip().removeprefix(".")].update(declarations)
        definitions.remove(style)

    gradient_ids = {}
    for index, gradient in enumerate(definitions, 1):
        old_id = gradient.attrib["id"]
        new_id = f"fw-gradient-{index:02}"
        gradient_ids[old_id] = new_id
        gradient.set("id", new_id)
        gradient.attrib.pop("data-name", None)

    part_for_path = {}
    for part, indices in PARTS.items():
        for index in indices:
            assert index not in part_for_path
            part_for_path[index] = part

    output = ET.Element(TAG("svg"), {
        "viewBox": original.attrib["viewBox"],
        "class": "fox-workbench-art",
        "role": "img",
        "aria-labelledby": "fw-title fw-description",
    })
    ET.SubElement(output, TAG("title"), {"id": "fw-title"}).text = "A fox follows a paper road"
    ET.SubElement(output, TAG("desc"), {"id": "fw-description"}).text = (
        "The supplied orange fox reaches toward a curled paper sheet on a sage workbench. "
        "The sheet unfolds into a winding road with a small orange car. "
        "Faithful web derivative of FoxHomepage_0.svg: all 176 paths, one ellipse, "
        "19 gradients and original painting order are retained. The source AI, SVG "
        "and source provenance metadata remain unchanged in IllustratorWorkspace."
    )
    metadata = ET.SubElement(output, TAG("metadata"), {"id": "fw-source-map"})
    output.append(definitions)
    artwork = ET.SubElement(output, TAG("g"), {"id": "fw-artwork"})
    counts = Counter()
    fragments = defaultdict(list)
    current_part = None
    current_group = None
    path_index = 0
    for source_shape in source_shapes:
        shape = deepcopy(source_shape)
        is_path = shape.tag == TAG("path")
        part = part_for_path.get(path_index, "workbench") if is_path else "fox-forehead-highlight"
        if part != current_part:
            counts[part] += 1
            group_id = f"fw-{part}-{counts[part]:02}"
            attributes = {"id": group_id, "class": f"fw-part fw-{part}", "data-part": part}
            if part in PIVOTS:
                x, y = PIVOTS[part]
                attributes.update({
                    "data-pivot": f"{x} {y}",
                    "style": f"transform-box:view-box;transform-origin:{x}px {y}px",
                })
            current_group = ET.SubElement(artwork, TAG("g"), attributes)
            fragments[part].append(group_id)
            current_part = part
        for class_name in shape.attrib.pop("class", "").split():
            for key, value in rules[class_name].items():
                shape.set(key, value.strip())
        for key, value in list(shape.attrib.items()):
            for old_id, new_id in gradient_ids.items():
                value = value.replace(f"url(#{old_id})", f"url(#{new_id})")
            shape.set(key, value)
        if is_path:
            shape.set("id", f"fw-path-{path_index:03}")
            shape.set("data-source-path", str(path_index))
            path_index += 1
        else:
            shape.set("id", "fw-forehead-highlight")
        current_group.append(shape)

    metadata.text = json.dumps({
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "geometry": "All source path d values, ellipse attributes and painter order unchanged.",
        "indexing": "Zero-based source path order, excluding the ellipse.",
        "fox_paths": FOX_PATHS,
        "fox_additional_shape": "fw-forehead-highlight",
        "part_paths": {**PARTS, "workbench": [i for i in range(176) if i not in part_for_path]},
        "part_fragments": dict(fragments),
        "root_coordinate_pivots": PIVOTS,
        "motion_notes": {
            "fox-tail": "Use a restrained rotation, within about 1 degree; root joins the body.",
            "fox-forepaw": "Two fragments must share a transform; keep the paw touching paper.",
            "fox-eye": "A brief vertical squash can blink; forehead highlight stays still.",
            "car": "Includes original car shadow, suitable for a short 8–16 unit roll.",
            "static_anatomy": "Head, throat and body overlap; do not rotate them independently.",
            "static_vine": "Some vine geometry is fused to the bench; animate only named individual leaves.",
        },
        "provenance": "Unsigned web derivative; original embedded provenance remains in the untouched source SVG.",
    }, ensure_ascii=False, separators=(",", ":"))

    # Verify identity of every geometric element, independently of grouping.
    output_paths = list(output.iter(TAG("path")))
    assert [p.attrib["d"] for p in source_paths] == [p.attrib["d"] for p in output_paths]
    assert SOURCE.read_bytes() == original_bytes
    ET.indent(output, space="  ")
    OUTPUT.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(output, encoding="unicode") + "\n")
    print(f"Prepared {OUTPUT.relative_to(ROOT)}: 176 paths, 1 ellipse, 19 gradients; source untouched.")


if __name__ == "__main__":
    prepare()

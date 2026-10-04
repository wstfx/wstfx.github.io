#!/usr/bin/env python3
"""Prepare an animation derivative; leave the editable overhead artwork intact.

The original traced dots retain their silhouettes and painter order. Existing
route dashes become a static fallback, not pixels to conceal with a patch.
The browser supplies one moving marker and a temporary connection at a time.
Run this after preparing scene-test-overhead.svg and review the map if its
source hash changes. No tracing, image service, or third-party package is used.
"""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/art/scene-test-overhead.svg"
OUTPUT = ROOT / "assets/art/scene-test-journey.svg"
SOURCE_SHA256 = "d6879050b49e47b1061c93a6a37248f5e1788def4c2f74be4bd91b632caec126"
NS = "http://www.w3.org/2000/svg"
T = lambda name: f"{{{NS}}}{name}"
ET.register_namespace("", NS)

# Native trace indices, verified against the source at its 1254px coordinates.
# Light fragments remain separately colorable, so the original dot texture
# survives instead of being covered by perfect circles.
NODES = {
    "a": {"point": [278, 489], "paths": [43, 78]},
    "b": {"point": [433, 684], "paths": [41]},
    "c": {"point": [255, 766], "paths": [44]},
    "d": {"point": [716, 720], "paths": [42, 67, 73]},
    "e": {"point": [557, 544], "paths": [37, 74]},
}
HIGHLIGHTS = {67, 74, 78}
ROUTE_PATHS = {47, 48, 49, 50, 76}


def build() -> None:
    data = SOURCE.read_bytes()
    digest = sha256(data).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("Overhead master changed: review trace-path mappings before regenerating the journey.")
    # Namespace all definitions, including gradients and the underpaint mask,
    # so the master and derivative may safely appear on the same review page.
    text = data.decode().replace("art-test-overhead-", "art-test-journey-")
    svg = ET.fromstring(text)
    svg.set("class", "chapter-illustration chapter-illustration-test-journey")
    svg.set("data-test-journey", "")
    svg.find(T("desc")).text = (
        "An orange fox investigates a contour map. A small marker travels "
        "between existing sample points, briefly tracing each connection and "
        "turning the point it reaches orange. This is an illustration of inquiry, not research data."
    )
    original_metadata = json.loads(svg.find(T("metadata")).text)
    svg.find(T("metadata")).text = json.dumps({
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": digest,
        "source_unchanged": True, "original_provenance": original_metadata,
        "node_map": NODES, "static_route_paths": sorted(ROUTE_PATHS),
        "motion_boundary": "Only existing samples, a temporary path, and a moving marker. Fox and map stay still.",
        "static_fallback": "Original five sample dots and original dashed route; visible without JavaScript.",
    }, separators=(",", ":"))

    fallback = ET.Element(T("g"), {"id": "test-journey-static-route", "data-journey-fallback": ""})
    for parent in list(svg.iter()):
        for child in list(parent):
            classes = child.get("class", "").split()
            if "test-sample-route" in classes:
                for path in child:
                    fallback.append(deepcopy(path))
                parent.remove(child)
            elif "test-sample-point" in classes:
                position = list(parent).index(child)
                for offset, path in enumerate(list(child)):
                    parent.insert(position + offset, path)
                parent.remove(child)

    mapping = {index: node for node, spec in NODES.items() for index in spec["paths"]}
    found = set()
    for parent in list(svg.iter()):
        for path in list(parent):
            index = path.get("data-trace-path")
            if index is None or int(index) not in mapping:
                continue
            index = int(index)
            found.add(index)
            node = mapping[index]
            group = ET.Element(T("g"), {
                "id": f"test-journey-node-{node}-{index:03}",
                "data-journey-node": node,
                "data-node-point": " ".join(map(str, NODES[node]["point"])),
            })
            path.set("data-native-fill", path.get("fill"))
            path.set("data-idle-fill", "#78856C" if index in HIGHLIGHTS else "#374535")
            path.set("data-active-fill", "#FFB875" if index in HIGHLIGHTS else "#F47B20")
            position = list(parent).index(path)
            parent.remove(path)
            group.append(path)
            parent.insert(position, group)
    assert found == set(mapping), "Every node fragment must be located."
    assert {int(p.get("data-trace-path")) for p in fallback} == ROUTE_PATHS
    svg.append(fallback)
    live = ET.SubElement(svg, T("g"), {
        "id": "test-journey-live", "data-journey-live": "",
        "visibility": "hidden", "pointer-events": "none", "aria-hidden": "true",
    })
    ET.SubElement(live, T("path"), {
        "id": "test-journey-route", "data-journey-route": "", "d": "M557 544",
        "fill": "none", "stroke": "#536B50", "stroke-width": "4.5",
        "stroke-linecap": "round", "pathLength": "1", "stroke-dasharray": "1 1",
        "stroke-dashoffset": "1", "opacity": "0",
    })
    ET.SubElement(live, T("circle"), {
        "id": "test-journey-marker", "data-journey-marker": "",
        "cx": "557", "cy": "544", "r": "9", "fill": "#F47B20",
        "stroke": "#FFF0DA", "stroke-width": "3", "opacity": "0",
    })
    # Let the marker disappear into the existing destination silhouette. The
    # route stays beneath all five dots instead of cutting across their faces.
    svg.remove(live)
    first_node = next(i for i, item in enumerate(svg) if item.get("data-journey-node"))
    svg.insert(first_node, live)
    ET.indent(svg, space="  ")
    OUTPUT.write_text(ET.tostring(svg, encoding="unicode") + "\n")
    assert SOURCE.read_bytes() == data, "Never alter the editable master."
    print(f"{OUTPUT.relative_to(ROOT)}: {len(NODES)} source nodes, native route and marker, static fallback preserved")


if __name__ == "__main__":
    build()

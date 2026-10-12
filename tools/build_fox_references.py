#!/usr/bin/env python3
"""Extract reusable mascot references from the approved Illustrator artwork.

Run prepare_fox_art.py first. No anatomy is redrawn: the color assets retain
the source paths, gradients and painter order. Mirroring is a layout option,
not a new pose. The contour uses an SVG mask to reveal the exterior of the
source silhouette, plus a few of its original interior color boundaries.
It has no baked-in paper fill, raster tracing, filter, or background image.
"""

from copy import deepcopy
import re
import xml.etree.ElementTree as ET

from prepare_fox_art import FOX_PATHS, NS, OUTPUT, ROOT, TAG

ET.register_namespace("", NS)
ART = ROOT / "assets/art"
NORMALIZE = "translate(7 -74) scale(.6)"
OUTLINE_COLOR = "#d85a18"


def canvas(name: str, description: str) -> ET.Element:
    svg = ET.Element(TAG("svg"), {
        "viewBox": "0 0 600 500",
        "role": "img",
        "aria-labelledby": f"{name}-title {name}-desc",
    })
    ET.SubElement(svg, TAG("title"), {"id": f"{name}-title"}).text = name.replace("-", " ").capitalize()
    ET.SubElement(svg, TAG("desc"), {"id": f"{name}-desc"}).text = description
    return svg


def source_fox(source: ET.Element) -> ET.Element:
    """Keep semantic fragments in source painter order, including the eye."""
    group = ET.Element(TAG("g"), {"class": "reference-source-fox"})
    for fragment in source.find(f"{TAG('g')}[@id='fw-artwork']"):
        if fragment.get("data-part", "").startswith("fox-"):
            clone = deepcopy(fragment)
            # Reference assets are intentionally static. Keep pivot metadata,
            # while removing the homepage's CSS hooks to avoid accidental motion.
            clone.attrib.pop("style", None)
            clone.attrib.pop("class", None)
            group.append(clone)
    paths = [int(p.get("data-source-path")) for p in group.iter(TAG("path"))]
    assert paths == FOX_PATHS, "Review the fox map if the supplied artwork changes."
    return group


def write(name: str, svg: ET.Element) -> None:
    # Namespacing makes these SVGs safe to inline together in a reference sheet.
    text = ET.tostring(svg, encoding="unicode")
    for original_id in re.findall(r'\bid="([^"]+)"', text):
        if original_id.startswith("fw-"):
            replacement = f"{name}-{original_id[3:]}"
            text = text.replace(f'id="{original_id}"', f'id="{replacement}"')
            text = text.replace(f"#{original_id})", f"#{replacement})")
    path = ART / f"fox-reference-{name}.svg"
    path.write_text(text + "\n")
    print(path.relative_to(ROOT))


def color_reference(source: ET.Element, fox: ET.Element, name: str,
                    description: str, transform: str) -> None:
    svg = canvas(f"fox-{name}", description)
    definitions = deepcopy(source.find(TAG("defs")))
    required = set(re.findall(r"url\(#([^)]+)\)", ET.tostring(fox, encoding="unicode")))
    for definition in list(definitions):
        if definition.get("id") not in required:
            definitions.remove(definition)
    svg.append(definitions)
    normalized = ET.SubElement(svg, TAG("g"), {"transform": transform})
    normalized.append(deepcopy(fox))
    write(name, svg)


def contour_reference(fox: ET.Element) -> None:
    svg = canvas("fox-contour", (
        "A transparent orange contour study of the supplied reaching fox. "
        "The outer contour and selected internal planes use the original vector "
        "geometry. Native SVG masks hide internal overlap; the background is transparent."
    ))
    definitions = ET.SubElement(svg, TAG("defs"))
    geometry = ET.SubElement(definitions, TAG("g"), {"id": "fr-contour-geometry"})
    indexed = {int(p.get("data-source-path")): p for p in fox.iter(TAG("path"))}
    for path in indexed.values():
        ET.SubElement(geometry, TAG("path"), {"d": path.get("d")})
    mask = ET.SubElement(definitions, TAG("mask"), {
        "id": "fr-contour-outside", "maskUnits": "userSpaceOnUse",
        "x": "0", "y": "0", "width": "1300", "height": "1200",
        "style": "mask-type:luminance",
    })
    ET.SubElement(mask, TAG("rect"), {"width": "1300", "height": "1200", "fill": "white"})
    ET.SubElement(mask, TAG("use"), {
        "href": "#fr-contour-geometry", "fill": "black", "stroke": "black",
        "stroke-width": "2", "stroke-linejoin": "round",
    })
    body = ET.SubElement(svg, TAG("g"), {
        "transform": NORMALIZE, "stroke": OUTLINE_COLOR,
        "stroke-width": "2.5", "fill": "none",
        "stroke-linejoin": "round", "stroke-linecap": "round",
    })
    ET.SubElement(body, TAG("use"), {
        "href": "#fr-contour-geometry", "stroke-width": "7",
        "mask": "url(#fr-contour-outside)",
    })
    # Selected source boundaries: throat, thigh, belly, flank, tail ribbon,
    # cream tail tip, inner ear and raised foreleg. Avoid the traced neck
    # fragments whose hidden closures would introduce a spurious contour.
    for index in [11, 33, 34, 44, 80, 84, 134, 137]:
        ET.SubElement(body, TAG("path"), {
            "d": indexed[index].get("d"), "data-source-path": str(index),
        })
    for index in [12, 172]:
        ET.SubElement(body, TAG("path"), {
            "d": indexed[index].get("d"), "data-source-path": str(index),
            "fill": OUTLINE_COLOR, "stroke": "none",
        })
    write("contour", svg)


def main() -> None:
    if not OUTPUT.exists():
        raise SystemExit("Run python3 tools/prepare_fox_art.py first.")
    source = ET.parse(OUTPUT).getroot()
    fox = source_fox(source)
    color_reference(source, fox, "reaching", (
        "The approved orange fox, isolated from FoxHomepage_0.svg. Its raised "
        "forepaw, long legs, cream throat and broad layered brush tail retain "
        "the supplied geometry and colors. This is the original reaching pose."
    ), NORMALIZE)
    color_reference(source, fox, "reaching-left", (
        "A mirrored layout option for the original reaching fox. All source "
        "geometry and colors are retained; this is not a newly drawn pose."
    ), "translate(600 0) scale(-1 1) " + NORMALIZE)
    color_reference(source, fox, "detail", (
        "A close view of the approved fox's head, ears and layered neck. "
        "This crop records the supplied facial proportions and color planes; "
        "it is a detail reference, not a new pose."
    ), "translate(-764 -270) scale(1.3)")
    contour_reference(fox)


if __name__ == "__main__":
    main()

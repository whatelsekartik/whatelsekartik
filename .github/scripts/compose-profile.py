#!/usr/bin/env python3
"""Compose a single warm, readable SVG board containing the banner and 3 graphs."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

def tag(name):
    return f"{{{SVG_NS}}}{name}"

def prefix_ids(root, prefix):
    mapping = {}
    for element in root.iter():
        value = element.attrib.get("id")
        if value:
            mapping[value] = f"{prefix}-{value}"
    if not mapping:
        return root

    for element in root.iter():
        for key, value in list(element.attrib.items()):
            if key == "id" and value in mapping:
                element.set(key, mapping[value])
            elif key == "aria-labelledby":
                element.set(key, " ".join(mapping.get(part, part) for part in value.split()))
            else:
                value = re.sub(
                    r"url\(#([^)]+)\)",
                    lambda match: f"url(#{mapping.get(match.group(1), match.group(1))})",
                    value,
                )
                if key in ("href", "{http://www.w3.org/1999/xlink}href") and value.startswith("#"):
                    value = "#" + mapping.get(value[1:], value[1:])
                element.set(key, value)
    return root

def embed_svg(board, path, x, y, width, height, prefix):
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Missing generated or design SVG: {source}")
    child = ET.parse(source).getroot()
    child = prefix_ids(child, prefix)
    child.set("x", str(x))
    child.set("y", str(y))
    child.set("width", str(width))
    child.set("height", str(height))
    child.set("preserveAspectRatio", "xMidYMid meet")
    board.append(child)

def rect(board, x, y, width, height, fill, rx=0, stroke=None, stroke_width=None):
    attrs = {
        "x": str(x), "y": str(y), "width": str(width), "height": str(height),
        "fill": fill,
    }
    if rx:
        attrs["rx"] = str(rx)
    if stroke:
        attrs["stroke"] = stroke
    if stroke_width:
        attrs["stroke-width"] = str(stroke_width)
    ET.SubElement(board, tag("rect"), attrs)

def text(board, value, x, y, size, fill, family="Arial, Helvetica, sans-serif",
         weight="normal", letter_spacing=None, anchor=None):
    attrs = {
        "x": str(x), "y": str(y), "fill": fill,
        "font-family": family, "font-size": str(size), "font-weight": weight,
    }
    if letter_spacing is not None:
        attrs["letter-spacing"] = str(letter_spacing)
    if anchor:
        attrs["text-anchor"] = anchor
    element = ET.SubElement(board, tag("text"), attrs)
    element.text = value

def main():
    board = ET.Element(tag("svg"), {
        "width": "1200", "height": "1640", "viewBox": "0 0 1200 1640",
        "role": "img", "aria-labelledby": "profile-board-title profile-board-desc",
    })
    title = ET.SubElement(board, tag("title"), {"id": "profile-board-title"})
    title.text = "Kartik Gaikwad — warm minimal profile and contribution skyline"
    desc = ET.SubElement(board, tag("desc"), {"id": "profile-board-desc"})
    desc.text = "Ivory and terracotta profile artwork with three contribution graphs arranged two above and one centred below."

    # Warm paper surround and a subtly lighter central sheet.
    rect(board, 0, 0, 1200, 1640, "#eee3d5")
    rect(board, 14, 14, 1172, 1612, "#fbf7f0", 26, "#dfcbb6", 2)

    # Preserve the profile header artwork, then compose the whole activity section
    # onto the same warm canvas so there is no mismatched page-coloured gap.
    embed_svg(board, "profile-header.svg", 35, 30, 1130, 282.5, "profile-header")
    embed_svg(board, "profile-section-contributions.svg", 40, 340, 1120, 149.33, "profile-section")

    # Top row: two matching contribution cards.
    rect(board, 34, 512, 552, 412, "#f1e6d8", 18, "#dfcbb6", 1.5)
    rect(board, 614, 512, 552, 412, "#f1e6d8", 18, "#dfcbb6", 1.5)
    text(board, "01 / WHATELSEKARTIK", 54, 548, 14, "#82452f", weight="bold", letter_spacing=1.5)
    text(board, "02 / AMINOTKARTIK", 634, 548, 14, "#82452f", weight="bold", letter_spacing=1.5)
    embed_svg(board, "profile-3d-contrib/main-account.svg", 44, 560, 532, 353.125, "graph-main")
    embed_svg(board, "profile-3d-contrib/second-account.svg", 624, 560, 532, 353.125, "graph-second")

    # Third card, optically centred below the top pair.
    rect(board, 190, 944, 820, 570, "#f1e6d8", 20, "#dfcbb6", 1.5)
    text(board, "03 / SITEMANGO", 220, 981, 14, "#82452f", weight="bold", letter_spacing=1.5)
    embed_svg(board, "profile-3d-contrib/third-account.svg", 220, 994, 760, 504.6875, "graph-sitemango")

    # Retain the matching footer design.
    embed_svg(board, "profile-footer.svg", 40, 1520, 1120, 98, "profile-footer")

    Path("profile-board.svg").write_bytes(
        ET.tostring(board, encoding="utf-8", xml_declaration=True)
    )
    print("Created profile-board.svg")

if __name__ == "__main__":
    main()

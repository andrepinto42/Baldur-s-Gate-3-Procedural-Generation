from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import plot_points

def get_attr(node: ET.Element, attr_id: str) -> Optional[str]:
    """Helper: get attribute value by id"""
    for a in node.findall("attribute"):
        if a.attrib.get("id") == attr_id:
            return a.attrib.get("value")
    return None


def parse_construction_points(root: ET.Element) -> Dict[str, Dict[str, Optional[str]]]:
	points: Dict[str, Dict[str, Optional[str]]] = {}
	spline = root.find(".//node[@id='ConstructionSpline']")

	for node in spline.iter("node"):
		if node.attrib.get("id") != "ConstructionPoint":
			continue

		cp_id = get_attr(node, "ConstructionPointId")
		if not cp_id:
			continue

		stretch = get_attr(node, "ConstructionPointStretch") == "True"
		helper = get_attr(node, "ConstructionHelperPoint") == "True"

		transform = node.find(".//node[@id='ConstructionPointTransform']")
		pos = None
		if transform is not None:
			pos = get_attr(transform, "Position")

		points[cp_id] = {
			"position": pos,
			"stretch": stretch,
			"helper": helper,
		}

	return points

def parse_construction_lines(root: ET.Element) -> List[List[str]]:
    paths: List[List[str]] = []

    line = root.find(".//node[@id='ConstructionLine']")

    # Get ordered ConstructionPoints
    cps = line.find("./children/node[@id='ConstructionPoints']")

    ordered = []
    print(cps.find("children").findall("node"))
    for cp in cps.find("children").findall("node"):
        cp_id = get_attr(cp,"ConstructionPointId")
        if cp_id:
            ordered.append(cp_id)

    if ordered:
        paths.append(ordered)

    return paths

def parse_tiles(root: ET.Element) -> List[Dict[str, Optional[str]]]:
    tiles = []

    for node in root.iter("node"):
        if node.attrib.get("id") != "tile":
            continue

        tile = {
            "uuid": get_attr(node, "UUID"),
            "translate": get_attr(node, "Translate"),
            "rotate": get_attr(node, "QRotate"),
            "stretchable": get_attr(node, "Stretchable") == "True",
        }
        tiles.append(tile)

    return tiles

def load_xml_data():
	tree = ET.parse(r"E:\Games\Baldurs Gate 3\Data\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\TileConstructions\03d51ba4-e614-4b56-81f4-a90df060d57e.lsx")
	root = tree.getroot()

	points = parse_construction_points(root)
	paths = parse_construction_lines(root)
	tiles = parse_tiles(root)

	print("\n=== LOGICAL PATHS ===")
	for p in paths:
		print(" -> ".join(p))

	print("\n=== CONSTRUCTION POINTS ===")
	for k, v in points.items():
		print(k, v)

	print("\n=== TILE SEGMENTS ===")
	for t in tiles:
		print(t)
          
	polylines = plot_points.build_polylines(points, paths)
	plot_points.draw_polylines(polylines)


if __name__ == "__main__":
      load_xml_data()
      
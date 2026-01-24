import re
from typing import Tuple, Optional
import os
import uuid
from pyrr import Vector3, Quaternion


XML_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<save>
	<version major="4" minor="8" revision="0" build="10" lslib_meta="v1,bswap_guids,lsf_keys_adjacency" />
	<region id="Templates">
		<node id="Templates">
			<children>
				<node id="GameObjects">
					<attribute id="MapKey" type="FixedString" value="8e9815d3-b97b-48ce-b2fc-d94095448e9a" />
					<attribute id="Name" type="LSString" value="WALL_City_Castlewall_Foundation_2D_9H_12W_S_Piece_A_Bhaal_A_001" />
					<attribute id="LevelName" type="FixedString" value="procedural2" />
					<attribute id="Type" type="FixedString" value="scenery" />
					<attribute id="TemplateName" type="FixedString" value="17c5529a-a991-415d-9478-52c29dfbaf06" />
					<attribute id="Flag" type="uint8" value="1" />
					<children>
						<node id="Transform">
							<attribute id="Scale" type="float" value="1" />
							<attribute id="Position" type="fvec3" value="10.34 0 9.1212" />
							<attribute id="RotationQuat" type="fvec4" value="0 0 0 1" />
						</node>
						<node id="LayerList">
							<children>
								<node id="Layers">
									<children>
										<node id="Object" key="MapKey">
											<attribute id="MapKey" type="FixedString" value="procedural2" />
										</node>
									</children>
								</node>
							</children>
						</node>
					</children>
				</node>
			</children>
		</node>
	</region>
</save>
"""

_object_names: set[str] = set()

def get_pattern_attribute_xml(attr_id):
    return rf'(<attribute\s+id="{attr_id}"[^>]*\svalue=")([^"]*)(")'


def vector_to_string(v: Optional[Vector3]) -> Optional[str]:
    if v is None:
        return None
    return f"{v.x} {v.y} {v.z}"

def quaternion_to_string(q: Optional[Quaternion]) -> Optional[str]:
    if q is None:
        return None
    # Pyrr Quaternion stores w,x,y,z; rearranged if your XML expects x y z w
    return f"{q.x} {q.y} {q.z} {q.w}"


def replace_attr(xml: str, attr_id: str, new_value: Optional[str]) -> str:
    if new_value is None:
        return xml

    pattern = get_pattern_attribute_xml(attr_id)
    return re.sub(pattern, rf"\g<1>{new_value}\g<3>", xml, count=1)


def replace_all_attr(xml: str, attr_id: str, new_value: Optional[str]) -> str:
    if new_value is None:
        return xml

    pattern = get_pattern_attribute_xml(attr_id)
    return re.sub(pattern, rf"\g<1>{new_value}\g<3>", xml)


def generate_uuid() -> str:
    return str(uuid.uuid4())

def allocate_object_name(base_name: str) -> str:
    if base_name not in _object_names:
        _object_names.add(base_name)
        return base_name
    
    # Remove the _000 if it exists
    base_name = re.sub(r'_\d{3}$','',base_name)
    
    i = 0
    while True:
        candidate = f"{base_name}_{i:03d}"
        if candidate not in _object_names:
            _object_names.add(candidate)
            return candidate
        i += 1

def create_object_xml(
    xml_template: str,
    map_key: Optional[str] = None,
    name: Optional[str] = None,
    level_name: Optional[str] = None,
    template_name: Optional[str] = None,
    position: Optional[Tuple[float, float, float]] = None,
    rotation: Optional[Tuple[float, float, float, float]] = None,
    scale: Optional[float] = None,
) -> str:
    xml = xml_template
    
    if map_key is None:
        map_key = generate_uuid()
    
    # Create an unique name
    name = allocate_object_name(name)

    xml = replace_attr(xml, "MapKey", map_key)
    xml = replace_attr(xml, "Name", name)
    xml = replace_attr(xml, "LevelName", level_name)
    xml = replace_attr(xml, "TemplateName", template_name)

    xml = replace_attr(xml, "Scale", str(scale))
    xml = replace_attr(xml, "Position", vector_to_string(position))
    xml = replace_attr(xml, "RotationQuat", quaternion_to_string(rotation))

    xml = replace_all_attr(xml, "MapKey", level_name)
    
    print("Generating with uuid :",map_key," for object",name)
    return xml

def write_xml_file(xml: str,folder: str) -> str:
    pattern = get_pattern_attribute_xml("MapKey")
    map_key_name = re.search(pattern,xml).groups()[1]
    filename = f"AUTO_{map_key_name}.lsx"

    destination_file = os.path.join(folder,filename)
    with open(destination_file, "w", encoding="utf-8") as f:
        f.write(xml)

    return destination_file

def clear_auto_xml(folder: str) -> None:
    filenames = os.listdir(folder)
    for filename in filenames:
        if not filename.startswith("AUTO_"):
            continue

        path = os.path.join(folder, filename)

        os.remove(path)
    
def create_xml(folder: str,
    map_key: Optional[str] = None,
    name: Optional[str] = None,
    level_name: Optional[str] = None,
    template_name: Optional[str] = None,
    position: Optional[Vector3] = None,
    rotation: Optional[Quaternion] = None,
    scale: Optional[float] = None
    ) -> str:
    xml = create_object_xml(
        XML_TEMPLATE,
        map_key = map_key,
        name = name,
        level_name = level_name,
        template_name = template_name,
        position = position,
        rotation = rotation,
        scale = scale
    )
    destination_path = write_xml_file(xml,folder)
    
    return destination_path
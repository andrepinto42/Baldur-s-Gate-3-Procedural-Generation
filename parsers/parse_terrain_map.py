
import xml.etree.ElementTree as ET
from typing import Tuple

def _parse_and_update_config(path: str, target_width: int, target_height: int) -> Tuple[str, int, int]:
    """
    Parse config and update dimensions to nearest multiple of 64 (rounded up)
    Also centers the terrain by adjusting the Position
    
    Args:
        path: Path to the config XML file
        target_width: Desired width (will be rounded up to nearest multiple of 64)
        target_height: Desired height (will be rounded up to nearest multiple of 64)
    
    Returns:
        Tuple of (map_key, new_width, new_height)
    """
    tree = ET.parse(path)
    root = tree.getroot()
    map_key = root.find(".//attribute[@id='MapKey']").get('value')
    bounds_elem = root.find(".//attribute[@id='BoundsMax']")
    position_elem = root.find(".//attribute[@id='Position']")
    bounds = bounds_elem.get('value').split()
    
    # Find Width and Height attributes
    width_elem = root.find(".//attribute[@id='Width']")
    height_elem = root.find(".//attribute[@id='Height']")
    
    # Get original dimensions
    original_width = int(width_elem.get('value')) if width_elem is not None else target_width
    original_height = int(height_elem.get('value')) if height_elem is not None else target_height
    
    # Calculate new values divisible by 64 (round up)
    new_width = ((target_width + 63) // 64) * 64
    new_height = ((target_height + 63) // 64) * 64
    
    # Update Width and Height in XML
    if width_elem is not None:
        width_elem.set('value', str(new_width))
    if height_elem is not None:
        height_elem.set('value', str(new_height))
    
    # Update BoundsMax to match new Width and Height
    original_bounds_y = float(bounds[1])
    new_bounds_x = float(new_width)
    new_bounds_z = float(new_height)
    
    new_bounds_value = f"{new_bounds_x} {original_bounds_y} {new_bounds_z}"
    bounds_elem.set('value', new_bounds_value)
    
    new_pos_x = - (new_width / 2.0)
    new_pos_z = - (new_height / 2.0)
    new_position_value = f"{new_pos_x} 0.0 {new_pos_z}"
    position_elem.set('value', new_position_value)
    
    # Save the modified XML
    tree.write(path, encoding='utf-8', xml_declaration=True)
    print(f"Updated config saved to: {path}")
    
    return map_key, new_width, new_height
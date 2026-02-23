from typing import Optional, Tuple
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BOUNDS_DIR = os.path.join(SCRIPT_DIR, "data_unpacked/bounds")
class ModelData:
    def __init__(self,uuid, size, center_offset):
        self.uuid: str = uuid
        # Size (dimensions)
        self.offset_x: float = size[0]
        self.offset_y: float = size[1]
        self.offset_z: float = size[2]

        # Center offset (pivot / origin correction)
        self.center_offset_x: float = center_offset[0]
        self.center_offset_y: float = center_offset[1]
        self.center_offset_z: float = center_offset[2]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def json_contains_string(obj, target):
    if isinstance(obj, dict):
        return any(json_contains_string(v, target) for v in obj.values())
    if isinstance(obj, list):
        return any(json_contains_string(i, target) for i in obj)
    if isinstance(obj, str):
        return target in obj
    return False

def find_data(name_search) -> Optional[ModelData]:
    for bounds_file in os.listdir(BOUNDS_DIR):
        if not bounds_file.lower().endswith(".json"):
            continue

        bounds_path = os.path.join(BOUNDS_DIR, bounds_file)

        try:
            bounds_data = load_json(bounds_path)
        except json.JSONDecodeError:
            print(f"⚠️ Invalid bounds JSON: {bounds_file}")
            continue

        
        # Handle both single object and list of objects
        is_list = isinstance(bounds_data, list)
        objects = bounds_data if is_list else [bounds_data]
        for obj in objects:
            if obj["name"] == name_search:
                if obj.get("uuid") == None:
                    print("Failed to find UUID, but did find the object ",name_search)
                    continue

                size = obj["size"]
                center_offset = obj["center_offset"]
                model_data = ModelData(obj["uuid"],size, center_offset)
                return model_data
        
    return None

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BOUNDS_DIR = os.path.join(SCRIPT_DIR, "data_unpacked/bounds")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "data_unpacked/output")


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


# Load all output JSONs once
output_jsons = []
for filename in os.listdir(OUTPUT_DIR):
    if filename.lower().endswith(".json"):
        path = os.path.join(OUTPUT_DIR, filename)
        try:
            data = load_json(path)
            if isinstance(data, list):
                output_jsons.extend(data)
            else:
                output_jsons.append(data)
        except json.JSONDecodeError:
            print(f"⚠️ Skipping invalid JSON: {filename}")

# Create name->uuid lookup
output_dict = {item["name"]: item for item in output_jsons}
bounds_dict = {}

# First pass: build bounds_dict from existing entries
bounds_objects = {}  # Store full objects for reference
for bounds_file in os.listdir(BOUNDS_DIR):
    if not bounds_file.lower().endswith(".json"):
        continue

    bounds_path = os.path.join(BOUNDS_DIR, bounds_file)

    try:
        bounds_data = load_json(bounds_path)
    except json.JSONDecodeError:
        print(f"⚠️ Invalid bounds JSON: {bounds_file}")
        continue

    is_list = isinstance(bounds_data, list)
    objects = bounds_data if is_list else [bounds_data]
    
    for obj in objects:
        bounds_dict[obj["name"]] = True
        bounds_objects[obj["name"]] = obj

# Second pass: find missing objects and add them
missing_objects = []
for a in output_dict.keys():
    if a not in bounds_dict:
        iterate_str = a
        found_parent = None
        
        for _ in range(5):
            splited = str(iterate_str).split('_')
            iterate_str = str.join("_", splited[0:-2])
            if iterate_str == "":
                break
            if iterate_str in bounds_dict:
                print(f"Found the correct name {iterate_str} for the object {a}")
                found_parent = iterate_str
                break
        
        if found_parent:
            # Get the parent object as template
            parent_obj = bounds_objects[found_parent]
            output_obj = output_dict[a]
            
            # Create a new entry based on parent template + output data
            new_entry = {
                "name": a,
                "relative_path": parent_obj["relative_path"],
                "size": parent_obj["size"],
                "center_offset": parent_obj["center_offset"],
                "uuid": output_obj["uuid"],
                "parent": found_parent
            }
            missing_objects.append((found_parent, new_entry))

# Now add the missing objects to the appropriate bounds files
for bounds_file in os.listdir(BOUNDS_DIR):
    if not bounds_file.lower().endswith(".json"):
        continue

    bounds_path = os.path.join(BOUNDS_DIR, bounds_file)

    try:
        bounds_data = load_json(bounds_path)
    except json.JSONDecodeError:
        continue

    is_list = isinstance(bounds_data, list)
    objects = bounds_data if is_list else [bounds_data]
    modified = False
    
    # Check if any missing objects belong in this file
    for parent_name, new_entry in missing_objects:
        # Check if this file contains the parent
        if any(obj.get("name") == parent_name for obj in objects):
            print(f"Adding {new_entry['name']} to {bounds_file}")
            if is_list:
                bounds_data.append(new_entry)
            else:
                # If it's a single object file, convert to list
                bounds_data = [bounds_data, new_entry]
            modified = True
    
    if modified:
        save_json(bounds_path, bounds_data)
        print(f"✅ Saved {bounds_file}")

print("\n✅ All bounds files updated!")
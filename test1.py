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
output_dict = {item["name"]: item["uuid"] for item in output_jsons}

results = {}
missing = []

for bounds_file in os.listdir(BOUNDS_DIR):
    if not bounds_file.lower().endswith(".json"):
        continue

    bounds_path = os.path.join(BOUNDS_DIR, bounds_file)

    try:
        bounds_data = load_json(bounds_path)
    except json.JSONDecodeError:
        print(f"⚠️ Invalid bounds JSON: {bounds_file}")
        continue

    # Track if any modifications were made to this file
    modified = False

    # Handle both single object and list of objects
    is_list = isinstance(bounds_data, list)
    objects = bounds_data if is_list else [bounds_data]
    
    for obj in objects:
        name = str(obj.get("name")).replace(".dae", "")
        obj["name"] = name
        # if name in output_dict:
        #     uuid = output_dict[name]
        #     print(f"Found it: {name} -> {uuid}")
            
        #     # INSERT YOUR NEW DATA HERE
        #     obj["uuid"] = uuid  # Example: add the UUID to the bounds object
        #     # Or add other fields:
        #     # obj["matched"] = True
        #     # obj["output_uuid"] = uuid
            
        #     modified = True
    modified = True
    
    # Save the bounds file if it was modified
    if modified:
        save_json(bounds_path, bounds_data)
        print(f"✅ Saved {bounds_data}")

print("\n✅ All bounds files updated!")
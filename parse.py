import os
import re
from typing import Dict
import json
from collections import defaultdict

UUID_PATTERN = re.compile(
    r'<attribute id="MapKey".*?value="([0-9a-fA-F-]{36})"[.\s\S]*?' +
    r'<attribute id="Name".*?value="(.*?)"[.\s\S]*?' +
    r'<attribute id="Type".*?value="(.*?)"'
)


grouped: dict[str, list[dict[str, str]]] = defaultdict(list)

def insert_attributes_into_dict(xml: str) -> None:

    for match in UUID_PATTERN.finditer(xml):
        uuid = match.group(1)
        name = match.group(2)
        type_object = match.group(3)

        grouped[type_object].append({
            "name": name,
            "uuid": uuid,
        })


def main() -> None:
    base_dir = "data_unpacked"

    for filename in os.listdir(base_dir):
        if not filename.lower().endswith(".lsx"):
            continue

        path = os.path.join(base_dir, filename)

        with open(path, "r", encoding="utf-8") as file:
            xml = file.read()
        
        insert_attributes_into_dict(xml)
    
    for type_object, entries in grouped.items():
        output_path = os.path.join(base_dir, f"output/{type_object}.json")

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(entries, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
import json
import os

folder_path = "data_unpacked/bounds"

# Check if folder exists
if not os.path.exists(folder_path):
    print(f"Error: Folder '{folder_path}' not found!")
else:
    # Get all JSON files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    # Group files by base name
    file_pairs = {}
    for filename in files:
        if filename.endswith('_objects.json'):
            base_name = filename.replace('_objects.json', '')
            if base_name not in file_pairs:
                file_pairs[base_name] = {}
            file_pairs[base_name]['objects'] = filename
        else:
            base_name = filename.replace('.json', '')
            if base_name not in file_pairs:
                file_pairs[base_name] = {}
            file_pairs[base_name]['base'] = filename
    
    # Process each pair
    combined_count = 0
    for base_name, pair in file_pairs.items():
        # Check if we have both files
        if 'objects' in pair and 'base' in pair:
            objects_file = os.path.join(folder_path, pair['objects'])
            base_file = os.path.join(folder_path, pair['base'])
            output_file = objects_file  # Save as _objects.json
            
            print(f"\nCombining: {pair['objects']} + {pair['base']}")
            
            # Read both files
            with open(objects_file, 'r', encoding='utf-8') as f:
                data1 = json.load(f)
            
            with open(base_file, 'r', encoding='utf-8') as f:
                data2 = json.load(f)
            
            # Combine the data
            if isinstance(data1, list) and isinstance(data2, list):
                combined_data = data1 + data2
            
            # Write combined data
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            # Delete the base file (keep only _objects.json)
            os.remove(base_file)
            
            print(f"  ✓ Combined into: {pair['objects']}")
            print(f"  ✓ Deleted: {pair['base']}")
            combined_count += 1
    
    print(f"\n{'='*50}")
    print(f"Total pairs combined: {combined_count}")
import os
from pathlib import Path

# Define the folder path
folder_path = "data_unpacked/bounds"

# Check if folder exists
if not os.path.exists(folder_path):
    print(f"Error: Folder '{folder_path}' not found!")
else:
    # Get all files in the folder
    files = os.listdir(folder_path)
    
    # Counter for renamed files
    count = 0
    
    # Process each file
    for filename in files:
        # Check if filename starts with "my_"
        if filename.startswith("my_"):
            # Remove "my_" prefix
            new_name = filename[3:]  # Remove first 3 characters
            
            # Add .json extension if it doesn't already have it
            if not new_name.endswith(".json"):
                new_name = new_name + ".json"
            
            # Create full paths
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_name.lower())
            
            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name.lower()}")
            count += 1
    
    print(f"\nTotal files renamed: {count}")
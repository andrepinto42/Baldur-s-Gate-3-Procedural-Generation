import os
from pathlib import Path

def find_files_in_folders(txt_file_path, folders):
    """
    Reads filenames from a text file and searches for them in specified folders.
    
    Args:
        txt_file_path: Path to the .txt file containing filenames (one per line)
        folders: List of folder paths to search in
    """
    
    # Read all lines from the text file
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            filenames = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{txt_file_path}' not found!")
        return
    
    print(f"Searching for {len(filenames)} filenames in {len(folders)} folders...\n")
    
    # Track results
    found_files = []
    not_found = []
    with open("another.txt", 'w', encoding='utf-8') as f2:
        for folder in folders:
                if not os.path.exists(folder):
                    continue
                    
                # Walk through the folder and all subdirectories
                for root, dirs, files in os.walk(folder):
                    for a in files:
                        found_files.append(str(a).upper())
                        f2.write(str(a)+"\n")
                
    # Search for each filename
    for filename in filenames:
        if not filename.replace(".dae",".GR2").upper() in found_files:
            print("not Found ",filename)
        
    # NAT_Bhaal_Cliff_Spire_A_Wall_A_Base
folders = [
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Effects",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\_PROP_ANIM",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Vista",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Splines",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Characters",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Doors",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Tools",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Weapons",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Tilesets",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Puzzle",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Nature",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Loot",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Lightsources",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Laboratory",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Furniture",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Equipment",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Decoration",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Containers",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Decals",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Buildings",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Books",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\_Helpers",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Quest",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\TerrainDecals",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\TerrainTextures",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Throwables",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Tool",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\UI",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\InstancePaint",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Consumables",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\Atmospheres",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\_Reference",
    r"c:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\Shared\Assets\MusicalInstruments",
]

find_files_in_folders("file_list.txt",folders)
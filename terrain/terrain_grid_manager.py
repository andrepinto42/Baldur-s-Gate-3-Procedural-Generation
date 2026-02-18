import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import xml.etree.ElementTree as ET
import numpy as np
from typing import Tuple
from convert import convert_one_file
from terrain.terrain_patch_writer import TerrainPatchWriter

class TerrainOrchestrator:
    def __init__(self, config_path: str, max_patch_res: int):
        self.max_patch_res = max_patch_res  # Maximum resolution per patch
        self.map_key, self.max_x, self.max_z = self._parse_config(config_path)
        
        # Calculate how many patches we need in each direction
        print("Here",self.max_x, self.max_z )
        self.grid_count_x = int(np.ceil(self.max_x / self.max_patch_res))
        self.grid_count_z = int(np.ceil(self.max_z / self.max_patch_res))
        
        # Calculate actual terrain dimensions (matches max_x and max_z)
        self.world_w = int(self.max_x) + 1 + 1  # +1 for the final vertex
        self.world_h = int(self.max_z) + 1 + 1  # +1 for the final vertex
        
        self.master_buffer = np.zeros((self.world_h, self.world_w), dtype=np.float32)

        print(f"Terrain dimensions: {self.max_x} x {self.max_z}")
        print(f"Master buffer: {self.world_w} x {self.world_h} vertices")
        print(f"Patch grid layout: {self.grid_count_x} x {self.grid_count_z} patches")
        print(f"Max patch resolution: {self.max_patch_res} x {self.max_patch_res}")

    def _parse_config(self, path: str) -> Tuple[str, float, float]:
        tree = ET.parse(path)
        root = tree.getroot()
        map_key = root.find(".//attribute[@id='MapKey']").get('value')
        bounds = root.find(".//attribute[@id='BoundsMax']").get('value').split()
        return map_key, float(bounds[0]), float(bounds[2])

    def apply_test_pattern(self):
        """Creates a diagonal ramp across the WHOLE map to verify tiling."""
        rows, cols = self.master_buffer.shape
        for r in range(rows):
            for c in range(cols):
                # Height increases as we move away from (0,0)
                self.master_buffer[r, c] = 1 + r / 10.0

    def generate_patches(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for z_idx in range(self.grid_count_z):
            for x_idx in range(self.grid_count_x):
                # Calculate the start position for this patch
                x_start = x_idx * self.max_patch_res
                z_start = z_idx * self.max_patch_res
                
                # Calculate how much terrain is left in this direction
                x_remaining = self.world_w - x_start
                z_remaining = self.world_h - z_start
                
                # Actual patch size is min of (max_patch_res, remaining terrain)
                patch_width = min(self.max_patch_res, x_remaining)
                patch_height = min(self.max_patch_res, z_remaining)
                
                # Extract the slice from master buffer
                x_end = x_start + patch_width
                z_end = z_start + patch_height
                
                tile_data = np.copy(self.master_buffer[z_start:z_end, x_start:x_end])
                
                print(f"Patch ({x_idx},{z_idx}): [{z_start}:{z_end}, {x_start}:{x_end}] = {tile_data.shape}")

                filename = f"{self.map_key}_{x_idx}_{z_idx}.patch"
                writer = TerrainPatchWriter(
                    width=patch_width,      # Actual extracted width
                    height=patch_height,    # Actual extracted height
                    patch_x=x_idx, 
                    patch_z=z_idx,
                    max_width=self.world_w-1,
                    max_height=self.world_h -1
                )
                writer.grid = tile_data  # Use the actual extracted data, no padding
                writer.write(os.path.join(output_dir, filename))
                    
        print(f"\nPatches generated. Coordinate (0,0) is in {self.map_key}_0_0.patch")

if __name__ == "__main__":
    CONFIG = r"E:\Games\Baldurs Gate 3\Data\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains\c8e19eb6-c009-4041-87df-4f3cde9822d1.lsx"
    convert_one_file(CONFIG.replace(".lsx",".lsf"),CONFIG)
    
    OUT = r"E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains"
    
    orch = TerrainOrchestrator(CONFIG, max_patch_res=65)
    orch.apply_test_pattern()
    orch.generate_patches(OUT)
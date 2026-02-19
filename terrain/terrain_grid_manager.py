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
    def __init__(self, config_path: str,width: int,height: int):
        self.max_patch_res = 65
        self.map_key, self.max_x, self.max_z = self._parse_and_update_config(config_path,width,height)
        
        # Calculate how many patches we need in each direction
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

    def _parse_and_update_config(self, path: str, target_width: int, target_height: int) -> Tuple[str, int, int]:
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
        
        # Calculate how much we've expanded
        width_increase = new_width - original_width
        height_increase = new_height - original_height
        
        print(f"Adjusting dimensions to be divisible by 64:")
        print(f"  Width: {target_width} → {new_width} (increased by {width_increase})")
        print(f"  Height: {target_height} → {new_height} (increased by {height_increase})")
        
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
        
        new_pos_x = - (width_increase / 2.0)
        new_pos_z = - (height_increase / 2.0)
        new_position_value = f"{0.0} 0.0 {0.0}"
        position_elem.set('value', new_position_value)
        
        # Save the modified XML
        tree.write(path, encoding='utf-8', xml_declaration=True)
        print(f"Updated config saved to: {path}")
        
        return map_key, new_width, new_height

    def apply_test_pattern(self):
        """Creates a diagonal ramp across the WHOLE map to verify tiling."""
        rows, cols = self.master_buffer.shape
        for r in range(rows):
            for c in range(cols):
                # Height increases as we move away from (0,0)
                self.master_buffer[r, c] = 0

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
                
                print(f"Patch_{x_idx}_{z_idx} width {patch_width} height {patch_height}")

                filename = f"{self.map_key}_{x_idx}_{z_idx}.patch"
                writer = TerrainPatchWriter(
                    width=patch_width,
                    height=patch_height,
                    patch_x=x_idx, 
                    patch_z=z_idx,
                    max_width=self.world_w,
                    max_height=self.world_h
                )
                writer.grid = tile_data 
                writer.write(os.path.join(output_dir, filename))
                    
        print(f"\nPatches generated. Coordinate (0,0) is in {self.map_key}_0_0.patch")

if __name__ == "__main__":
    CONFIG = r"E:\Games\Baldurs Gate 3\Data\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains\c8e19eb6-c009-4041-87df-4f3cde9822d1.lsx"
    CONFIG_BINARY = CONFIG.replace(".lsx",".lsf")
    OUT = r"E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains"

    convert_one_file(CONFIG_BINARY,CONFIG)    
    
    orch = TerrainOrchestrator(CONFIG,128,128)
    convert_one_file(CONFIG,CONFIG_BINARY)

    orch.apply_test_pattern()
    orch.generate_patches(OUT)
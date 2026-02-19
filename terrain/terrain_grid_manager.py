import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import xml.etree.ElementTree as ET
import numpy as np
from typing import Tuple
from convert import convert_one_file
from terrain.terrain_patch_writer import TerrainPatchWriter
from parsers.parse_terrain_map import _parse_and_update_config

class TerrainGridManager:
    def __init__(self, map_key: str,width: int,height: int):
        self.max_patch_res = 65
        self.map_key = map_key
        
        # Calculate how many patches we need in each direction
        self.grid_count_x = int(np.ceil(width / self.max_patch_res))
        self.grid_count_z = int(np.ceil(height / self.max_patch_res))
        
        # Calculate actual terrain dimensions (matches max_x and max_z)
        self.world_w = int(width) + 1 + 1  # +1 for the final vertex
        self.world_h = int(height) + 1 + 1  # +1 for the final vertex
        
        self.master_buffer = np.zeros((self.world_h, self.world_w), dtype=np.float32)

        print(f"Terrain dimensions: {width} x {height}")
        print(f"Master buffer: {self.world_w} x {self.world_h} vertices")
        print(f"Patch grid layout: {self.grid_count_x} x {self.grid_count_z} patches")
        print(f"Max patch resolution: {self.max_patch_res} x {self.max_patch_res}")

    def apply_test_pattern(self):
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


if __name__ == "__main__":
    CONFIG = r"E:\Games\Baldurs Gate 3\Data\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains\c8e19eb6-c009-4041-87df-4f3cde9822d1.lsx"
    CONFIG_BINARY = CONFIG.replace(".lsx",".lsf")
    OUT = r"E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains"

    convert_one_file(CONFIG_BINARY,CONFIG)    
    map_key, total_width, total_height = _parse_and_update_config(CONFIG,256,256)
    convert_one_file(CONFIG,CONFIG_BINARY)
    
    orch = TerrainGridManager(map_key,total_width,total_height)

    orch.apply_test_pattern()
    orch.generate_patches(OUT)
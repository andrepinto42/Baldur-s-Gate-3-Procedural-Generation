import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import xml.etree.ElementTree as ET
import numpy as np
import re
from typing import Tuple
from terrain.terrain_patch_writer import TerrainPatchWriter
from parsers.parse_terrain_map import _parse_and_update_config
from terrain_modify_height import modify_terrain

class TerrainGridManager:
    def __init__(self, map_key: str,width: int,height: int):
        self.max_patch_res = 65
        self.map_key = map_key
        
        # Calculate how many patches we need in each direction
        self.grid_count_x = int(np.ceil(width / self.max_patch_res))
        self.grid_count_z = int(np.ceil(height / self.max_patch_res))
        
        # Calculate actual terrain dimensions (matches max_x and max_z)
        self.world_w = int(width) + 1  # +1 for the final vertex
        self.world_h = int(height) + 1  # +1 for the final vertex
        
        self.master_buffer = np.zeros((self.world_h, self.world_w), dtype=np.float32)

        print(f"Terrain dimensions: {width} x {height}")
        print(f"Master buffer: {self.world_w} x {self.world_h} vertices")
        print(f"Patch grid layout: {self.grid_count_x} x {self.grid_count_z} patches")
        print(f"Max patch resolution: {self.max_patch_res} x {self.max_patch_res}")

    def generate_patches(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Remove existing .patch files with the same map_key and ending in _\d+_\d+.patch
        pattern = re.compile(rf"^{re.escape(self.map_key)}_\d+_\d+\.patch$")
        for existing_file in Path(output_dir).glob("*.patch"):
            if pattern.match(existing_file.name):
                existing_file.unlink()

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
                    max_width=self.world_w - self.grid_count_x,
                    max_height=self.world_h - self.grid_count_z
                )
                writer.grid = tile_data 
                writer.write(os.path.join(output_dir, filename))
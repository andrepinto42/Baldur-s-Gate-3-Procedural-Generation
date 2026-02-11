import os
import re
import struct
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, List, Any

class TerrainStitcher:
    def __init__(self, directory: str):
        self.directory: str = directory
        self.master_grid: Optional[np.ndarray] = None

    def _get_tile_indices(self, filename: str) -> Optional[Tuple[int, int]]:
        match = re.search(r'(\d+)_(\d+)\.patch$', filename)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None

    def read_patch(self, filepath: str) -> np.ndarray:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        metadata = struct.unpack('<7I', raw_data[12:40])
        
        # Handle binary vs ASCII-padded dimensions
        tile_width = metadata[1] if metadata[1] < 0xFFFF else raw_data[16]
        tile_height = metadata[2] if metadata[2] < 0xFFFF else raw_data[20]
        
        vertex_count = tile_width * tile_height
        height_values = np.frombuffer(raw_data[88:], dtype='<f4')[:vertex_count].copy()
        
        # Clean invalid data
        cleaned_heights = np.where(
            np.isnan(height_values) | (np.abs(height_values) > 20000), 
            0.0, 
            height_values
        )
        
        if cleaned_heights.size < vertex_count:
            cleaned_heights = np.pad(cleaned_heights, (0, vertex_count - cleaned_heights.size))
            
        return cleaned_heights.reshape((tile_height, tile_width))

    def stitch(self) -> np.ndarray:
        patch_files = [f for f in os.listdir(self.directory) if f.endswith('.patch')]
        tile_manifest: List[Tuple[int, int, str]] = []
        max_x, max_y = 0, 0

        for filename in patch_files:
            coords = self._get_tile_indices(filename)
            if coords:
                x, y = coords
                tile_manifest.append((x, y, filename))
                max_x, max_y = max(max_x, x), max(max_y, y)

        # Determine uniform tile size from the first patch
        sample_path = os.path.join(self.directory, tile_manifest[0][2])
        sample_tile = self.read_patch(sample_path)
        t_rows, t_cols = sample_tile.shape
        
        total_rows = (max_y + 1) * t_rows
        total_cols = (max_x + 1) * t_cols
        self.master_grid = np.zeros((total_rows, total_cols), dtype=np.float32)

        for x, y, filename in tile_manifest:
            try:
                path = os.path.join(self.directory, filename)
                tile_data = self.read_patch(path)
                
                rows, cols = tile_data.shape
                row_start, col_start = y * t_rows, x * t_cols
                
                self.master_grid[row_start : row_start + rows, 
                                 col_start : col_start + cols] = tile_data
                                 
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        return self.master_grid

    def visualize_3d(self, exaggeration: float = 0.5, downsample: int = 1) -> None:
        if self.master_grid is None:
            return

        display_data = self.master_grid[::downsample, ::downsample]
        rows, cols = display_data.shape

        x_coords = np.arange(0, cols)
        y_coords = np.arange(0, rows)
        x_mesh, y_mesh = np.meshgrid(x_coords, y_coords)

        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')

        surface = ax.plot_surface(
            x_mesh, y_mesh, display_data, 
            cmap='terrain',
            linewidth=0, 
            antialiased=True,
            rcount=150, 
            ccount=150
        )

        ax.set_box_aspect((cols, rows, cols * exaggeration)) 
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Height')
        
        fig.colorbar(surface, ax=ax, shrink=0.5, aspect=10)
        ax.view_init(elev=35, azim=-45)
        plt.show()

if __name__ == "__main__":
    DATA_PATH = r"E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains"
    stitcher = TerrainStitcher(DATA_PATH)
    
    stitcher.stitch()
    stitcher.visualize_3d(exaggeration=0.01, downsample=1)
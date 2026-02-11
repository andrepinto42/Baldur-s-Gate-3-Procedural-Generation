#!/usr/bin/env python3
"""
Terrain Patch class for reading .patch files
"""

import struct
import numpy as np
from typing import Dict, Optional
import numpy.typing as npt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class TerrainPatchReader:
    """Class to handle terrain patch file parsing and visualization"""
    
    def __init__(self, filepath: str) -> None:
        """
        Initialize a terrain patch reader
        
        Args:
            filepath: Path to the .patch file to read
        """
        self.filepath: str = filepath
        self.magic: Optional[str] = None
        self.version: Optional[int] = None
        self.metadata: Dict[str, int] = {}
        self.grid_width: int = 0
        self.grid_height: int = 0
        self.heights: list[float] = []
        self.grid: Optional[npt.NDArray[np.float32]] = None
        
    def read(self) -> 'TerrainPatchReader':
        """
        Read and parse the terrain patch file
        
        Returns:
            Self for method chaining
        """
        with open(self.filepath, 'rb') as f:
            data = f.read()
        
        offset = 0
        
        # Read magic/version string (8 bytes)
        self.magic = data[offset:offset+8].decode('ascii')
        offset += 8
        
        # Read version number (4 bytes, little-endian unsigned int)
        self.version = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Read metadata values
        metadata_values: list[int] = []
        for i in range(7):
            val = struct.unpack('<I', data[offset:offset+4])[0]
            metadata_values.append(val)
            offset += 4
        
        # Parse dimensions
        self.metadata = {
            'value_0': metadata_values[0],
            'grid_width': metadata_values[1],
            'grid_height': metadata_values[2],
            'value_3': metadata_values[3],
            'value_4': metadata_values[4],
            'value_5': metadata_values[5],
            'value_6': metadata_values[6],
        }
        
        self.grid_width = self.metadata['grid_width']
        self.grid_height = self.metadata['grid_height']
        
        print(f"Magic: {self.magic}")
        print(f"Version: {self.version}")
        print(f"Grid dimensions: {self.grid_width} x {self.grid_height}")
        print(f"Data starts at offset: {offset}")
        
        # Skip to actual grid data (starts at offset 88)
        offset = 88
        
        # Read height data (32-bit floats)
        self.heights = []
        for i in range(offset, len(data), 4):
            if i + 4 <= len(data):
                val_bytes = data[i:i+4]
                try:
                    val = struct.unpack('<f', val_bytes)[0]
                    # Filter out NaN and unrealistic values
                    if np.isnan(val) or abs(val) > 10000:
                        val = 0.0
                    self.heights.append(val)
                except:
                    break
        
        print(f"Read {len(self.heights)} height values")
        
        # Convert to numpy array and reshape into grid
        # Take the first grid_width * grid_height values
        grid_size = self.grid_width * self.grid_height
        if len(self.heights) >= grid_size:
            grid_heights = np.array(self.heights[:grid_size], dtype=np.float32)
            self.grid = grid_heights.reshape((self.grid_height, self.grid_width))
        else:
            print(f"Warning: Not enough height data. Expected {grid_size}, got {len(self.heights)}")
            # Pad with zeros if needed
            padded = self.heights + [0.0] * (grid_size - len(self.heights))
            self.grid = np.array(padded, dtype=np.float32).reshape((self.grid_height, self.grid_width))
        
        return self
    

    def get_statistics(self) -> Optional[Dict[str, float]]:
        """
        Get statistics about the terrain
        
        Returns:
            Dictionary containing terrain statistics or None if no grid data
        """
        if self.grid is None:
            return None
        
        stats = {
            'min_height': float(np.min(self.grid)),
            'max_height': float(np.max(self.grid)),
            'mean_height': float(np.mean(self.grid)),
            'std_dev': float(np.std(self.grid)),
            'total_vertices': float(self.grid.size),
            'zero_vertices': float(np.sum(np.abs(self.grid) < 0.001)),
            'non_zero_vertices': float(np.sum(np.abs(self.grid) >= 0.001)),
        }
        
        stats['zero_percent'] = (stats['zero_vertices'] / stats['total_vertices']) * 100
        stats['non_zero_percent'] = (stats['non_zero_vertices'] / stats['total_vertices']) * 100
        
        return stats
    
    def print_statistics(self) -> None:
        """Print terrain statistics to console"""
        stats = self.get_statistics()
        if stats:
            print("\n=== Terrain Statistics ===")
            print(f"Height range: {stats['min_height']:.3f} to {stats['max_height']:.3f}")
            print(f"Mean height: {stats['mean_height']:.3f}")
            print(f"Std deviation: {stats['std_dev']:.3f}")
            print(f"Total vertices: {int(stats['total_vertices'])}")
            print(f"Flat (zero) vertices: {int(stats['zero_vertices'])} ({stats['zero_percent']:.1f}%)")
            print(f"Non-zero vertices: {int(stats['non_zero_vertices'])} ({stats['non_zero_percent']:.1f}%)")
    
    
    def visualize_3d_surface(self):
        """Create a 3D surface plot with corrected aspect ratio"""
        if self.grid is None:
            print("No grid data to visualize")
            return
        
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create coordinate grids
        x = np.arange(0, self.grid_width)
        y = np.arange(0, self.grid_height)
        X, Y = np.meshgrid(x, y)
        
        # Plot surface
        surf = ax.plot_surface(X, Y, self.grid, cmap='terrain', 
                               linewidth=0, antialiased=True, alpha=0.9)
        
        z_min, z_max = np.min(self.grid), np.max(self.grid)
        z_range = z_max - z_min
        
        # Avoid division by zero/Singular Matrix if terrain is flat
        display_z_range = max(z_range, 1.0)
        
        # Balanced Aspect: This keeps X and Y large and clear.
        # Format: (width_scale, height_scale, vertical_exaggeration)
        # 1, 1, 0.4 means the box is a flat-ish rectangle.
        ax.set_box_aspect((1, 1, 0.4))
        # ----------------
        
        # Add contour lines at the base
        ax.contour(X, Y, self.grid, zdir='z', offset=np.min(self.grid), 
                  cmap='terrain', alpha=0.5)
        
        # Labels and title
        ax.set_xlabel('X coordinate')
        ax.set_ylabel('Y coordinate')
        ax.set_zlabel('Height (m)')
        ax.set_title(f'3D Terrain Surface - {self.grid_width}x{self.grid_height}')
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Height (m)')
        
        plt.show()
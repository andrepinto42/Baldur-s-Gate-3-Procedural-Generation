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
    def find_steep_differences(self, filepath: str, threshold: float = 1.0) -> None:
        """Find vertices where height differs significantly from neighbors"""
        grid = self.read_patch(filepath)
        rows, cols = grid.shape
        
        steep_locations = []
        
        for y in range(rows):
            for x in range(cols):
                current = grid[y, x]
                max_diff = 0
                
                # Check all 4 neighbors (up, down, left, right)
                neighbors = []
                if y > 0:  # up
                    neighbors.append(grid[y-1, x])
                if y < rows - 1:  # down
                    neighbors.append(grid[y+1, x])
                if x > 0:  # left
                    neighbors.append(grid[y, x-1])
                if x < cols - 1:  # right
                    neighbors.append(grid[y, x+1])
                
                # Also check diagonals for thoroughness
                if y > 0 and x > 0:  # top-left
                    neighbors.append(grid[y-1, x-1])
                if y > 0 and x < cols - 1:  # top-right
                    neighbors.append(grid[y-1, x+1])
                if y < rows - 1 and x > 0:  # bottom-left
                    neighbors.append(grid[y+1, x-1])
                if y < rows - 1 and x < cols - 1:  # bottom-right
                    neighbors.append(grid[y+1, x+1])
                
                # Find max difference from any neighbor
                if neighbors:
                    max_diff = max(abs(current - n) for n in neighbors)
                    
                    if max_diff > threshold:
                        steep_locations.append((y, x, current, max_diff))
        
        print(f"\nFound {len(steep_locations)} vertices with neighbor difference > {threshold}")
        
        if steep_locations:
            # Sort by difference (largest first)
            steep_locations.sort(key=lambda x: x[3], reverse=True)
            
            print(f"\nTop 20 steepest differences (row, col, height, max_diff):")
            for i, (y, x, height, diff) in enumerate(steep_locations[:20]):
                print(f"  [{y:2d}, {x:2d}]: height={height:6.2f}, max_diff={diff:6.2f}")
            
            # Create a heatmap of differences
            diff_map = np.zeros_like(grid)
            for y, x, _, diff in steep_locations:
                diff_map[y, x] = diff
            
            plt.figure(figsize=(14, 6))
            
            # Original height map
            plt.subplot(1, 2, 1)
            plt.imshow(grid, cmap='terrain', interpolation='nearest')
            plt.colorbar(label='Height')
            plt.title('Original Height Map')
            plt.xlabel('X')
            plt.ylabel('Y')
            
            # Difference map
            plt.subplot(1, 2, 2)
            plt.imshow(diff_map, cmap='hot', interpolation='nearest')
            plt.colorbar(label='Max Difference from Neighbors')
            plt.title(f'Steep Changes (threshold={threshold})')
            plt.xlabel('X')
            plt.ylabel('Y')
            
            # Mark the steepest points
            for y, x, _, _ in steep_locations[:10]:
                plt.scatter(x, y, c='cyan', s=50, marker='x')
            
            plt.tight_layout()
            plt.show()
        
        return steep_locations
    def read_patch(self, filepath: str) -> np.ndarray:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        metadata = struct.unpack('<7I', raw_data[12:40])
        
        # Handle binary vs ASCII-padded dimensions
        tile_width = metadata[1] if metadata[1] < 0xFFFF else raw_data[16]
        tile_height = metadata[2] if metadata[2] < 0xFFFF else raw_data[20]
        
        vertex_count = tile_width * tile_height
        height_values = np.frombuffer(raw_data[92:], dtype='<f4')[:vertex_count].copy()
        # Find NaN and invalid values BEFORE cleaning
        nan_mask = np.isnan(height_values)
        
        nan_count = np.sum(nan_mask)
        
        if nan_count > 0:
            print(f"\n=== INVALID VALUES IN {os.path.basename(filepath)} ===")
            
            if nan_count > 0:
                print(f"\nFound {nan_count} NaN values:")
                nan_indices = np.where(nan_mask)[0]
                for idx in nan_indices[:20]:  # Show first 20
                    byte_offset = 88 + idx * 4
                    row = idx // tile_width
                    col = idx % tile_width
                    print(f"  Index {idx:4d} -> Row {row:2d}, Col {col:2d} | Byte offset: {byte_offset}")
        
        # Clean invalid data
        cleaned_heights = np.where(
            np.isnan(height_values), 
            0.0,  # Changed to 0.0 instead of 20
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
    
    def find_problematic_values(self) -> None:
        """Find and visualize where incorrect values (zeros or anomalies) are located"""
        if self.master_grid is None:
            print("No grid loaded. Run stitch() first.")
            return
        
        # Find zeros
        zero_mask = (self.master_grid == 0)
        zero_count = np.sum(zero_mask)
        zero_positions = np.where(zero_mask)
        
        print(f"Total zeros found: {zero_count} out of {self.master_grid.size} ({100*zero_count/self.master_grid.size:.2f}%)")
        
        # Analyze patch boundaries (assuming 65x65 patches with 64-stride)
        tile_size = 64
        tile_stride = 64
        
        print(f"\n=== PATCH BOUNDARY ANALYSIS ===")
        print(f"Tile size: {tile_size}x{tile_size}, Stride: {tile_stride}")
        
        # Find which rows are patch boundaries
        patch_boundary_rows = []
        for i in range(0, self.master_grid.shape[0], tile_stride):
            patch_boundary_rows.append(i)
        
        print(f"\nPatch boundary rows: {patch_boundary_rows}")
        
        # Find which columns are patch boundaries  
        patch_boundary_cols = []
        for i in range(0, self.master_grid.shape[1], tile_stride):
            patch_boundary_cols.append(i)
        
        print(f"Patch boundary columns: {patch_boundary_cols}")
        
        # Check zeros at each boundary row
        print(f"\n=== ZEROS AT BOUNDARY ROWS ===")
        for row in patch_boundary_rows:
            if row < self.master_grid.shape[0]:
                row_zeros = np.sum(self.master_grid[row, :] == 0)
                if row_zeros > 0:
                    zero_cols = np.where(self.master_grid[row, :] == 0)[0]
                    print(f"Row {row}: {row_zeros} zeros at columns {zero_cols[:20].tolist()}...")
                    
                    # Determine which patch(es) this affects
                    patch_y = row // tile_stride
                    print(f"  → Affects patches in row {patch_y} (top edge of patches)")
        
        # Check zeros at each boundary column
        print(f"\n=== ZEROS AT BOUNDARY COLUMNS ===")
        for col in patch_boundary_cols:
            if col < self.master_grid.shape[1]:
                col_zeros = np.sum(self.master_grid[:, col] == 0)
                if col_zeros > 0:
                    zero_rows = np.where(self.master_grid[:, col] == 0)[0]
                    print(f"Column {col}: {col_zeros} zeros at rows {zero_rows[:20].tolist()}...")
                    
                    # Determine which patch(es) this affects
                    patch_x = col // tile_stride
                    print(f"  → Affects patches in column {patch_x} (left edge of patches)")
        
        # Find zeros that are NOT on patch boundaries
        print(f"\n=== ZEROS NOT ON PATCH BOUNDARIES ===")
        non_boundary_zeros = []
        for i in range(len(zero_positions[0])):
            r, c = zero_positions[0][i], zero_positions[1][i]
            is_boundary = (r in patch_boundary_rows) or (c in patch_boundary_cols)
            if not is_boundary:
                non_boundary_zeros.append((r, c))
        
        if non_boundary_zeros:
            print(f"Found {len(non_boundary_zeros)} zeros NOT on boundaries:")
            for r, c in non_boundary_zeros[:20]:
                # Find which patch this belongs to
                patch_y = r // tile_stride
                patch_x = c // tile_stride
                local_y = r % tile_stride
                local_x = c % tile_stride
                print(f"  Global [{r:4d}, {c:4d}] → Patch ({patch_x},{patch_y}) Local [{local_y:2d},{local_x:2d}]")
        else:
            print("All zeros are on patch boundaries (expected)")
        
        # Find if they form patterns (lines)
        if zero_count > 0:
            # Check for horizontal lines (row-wise zeros)
            print(f"\n=== COMPLETE ZERO ROWS ===")
            for row in range(self.master_grid.shape[0]):
                row_zeros = np.sum(self.master_grid[row, :] == 0)
                if row_zeros > self.master_grid.shape[1] * 0.5:  # More than 50% zeros
                    patch_y = row // tile_stride
                    local_y = row % tile_stride
                    print(f"Row {row} has {row_zeros}/{self.master_grid.shape[1]} zeros")
                    print(f"  → Patch row {patch_y}, Local row {local_y}")
            
            # Check for vertical lines (column-wise zeros)
            print(f"\n=== COMPLETE ZERO COLUMNS ===")
            for col in range(self.master_grid.shape[1]):
                col_zeros = np.sum(self.master_grid[:, col] == 0)
                if col_zeros > self.master_grid.shape[0] * 0.5:  # More than 50% zeros
                    patch_x = col // tile_stride
                    local_x = col % tile_stride
                    print(f"Column {col} has {col_zeros}/{self.master_grid.shape[0]} zeros")
                    print(f"  → Patch column {patch_x}, Local column {local_x}")
            
            # Visualize the zero mask
            plt.figure(figsize=(12, 10))
            plt.imshow(zero_mask, cmap='RdYlGn_r', interpolation='nearest')
            plt.colorbar(label='Zero (red) vs Non-zero (green)')
            plt.title('Zero Value Locations')
            plt.xlabel('Column')
            plt.ylabel('Row')
            
            # Add grid lines at patch boundaries
            for i in patch_boundary_rows:
                plt.axhline(y=i, color='blue', linestyle='--', linewidth=1, alpha=0.7, label='Patch boundary' if i == patch_boundary_rows[0] else '')
            for i in patch_boundary_cols:
                plt.axvline(x=i, color='blue', linestyle='--', linewidth=1, alpha=0.7)
            
            plt.legend()
            plt.tight_layout()
            plt.show()
        
        # Also check for other anomalies
        print(f"\n=== GRID STATISTICS ===")
        print(f"Min: {np.min(self.master_grid):.3f}")
        print(f"Max: {np.max(self.master_grid):.3f}")
        print(f"Mean: {np.mean(self.master_grid):.3f}")
        if np.any(self.master_grid != 0):
            print(f"Mean (non-zero): {np.mean(self.master_grid[self.master_grid != 0]):.3f}")

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
    sample_patch = stitcher.read_patch(r"E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains\c8e19eb6-c009-4041-87df-4f3cde9822d1_0_1.patch")
    print(f"Patch shape: {sample_patch.shape}")
    print(f"Zeros in single patch: {np.sum(sample_patch == 0)}")
    print(f"First row: {sample_patch[0, :10]}")
    print(f"Last row: {sample_patch[-1, :10]}")
    print(f"First col: {sample_patch[:10, 0]}")
    print(f"Last col: {sample_patch[:10, -1]}")
    stitcher.find_problematic_values()
    stitcher.visualize_3d(exaggeration=1, downsample=1)
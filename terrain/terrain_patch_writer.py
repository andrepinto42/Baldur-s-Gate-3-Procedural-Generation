#!/usr/bin/env python3
"""
Terrain Patch Writer class for creating .patch files
"""

import struct
import numpy as np
from typing import Literal
import numpy.typing as npt


class TerrainPatchWriter:
    """Class to create and write terrain patch files"""
    
    def __init__(self, width: int = 65, height: int = 65) -> None:
        """
        Initialize a new terrain patch writer
        
        Args:
            width: Grid width (default 65, common for terrain patches)
            height: Grid height (default 65)
        """
        self.width: int = width
        self.height: int = height
        self.grid: npt.NDArray[np.float32] = np.zeros((height, width), dtype=np.float32)
        
    def set_height(self, x: int, y: int, height: float) -> None:
        """
        Set height at a specific coordinate
        
        Args:
            x: X coordinate
            y: Y coordinate
            height: Height value to set
        """
        if 0 <= y < self.height and 0 <= x < self.width:
            self.grid[y, x] = height
    
    def fill_rectangle(
        self,
        x_start: int,
        y_start: int,
        width: int,
        height: int,
        elevation: float,
        blend_distance: int = 0
    ) -> None:
        """
        Create a rectangular raised area
        
        Args:
            x_start: Starting X coordinate
            y_start: Starting Y coordinate
            width: Rectangle width
            height: Rectangle height
            elevation: Height value
            blend_distance: Optional smoothing distance (0 = no smoothing)
        """
        x_end = min(x_start + width, self.width)
        y_end = min(y_start + height, self.height)
        
        self.grid[y_start:y_end, x_start:x_end] = elevation
        
        print(f"Created rectangle: ({x_start},{y_start}) to ({x_end},{y_end}) at {elevation}m")
        
        if blend_distance > 0:
            self.smooth_edges(
                shape_type='rectangle',
                x_start=x_start,
                y_start=y_start,
                width=width,
                height=height,
                blend_distance=blend_distance
            )
    
    def fill_circle(
        self,
        center_x: int,
        center_y: int,
        radius: int,
        elevation: float,
        blend_distance: int = 0
    ) -> None:
        """
        Create a circular raised area
        
        Args:
            center_x: Circle center X
            center_y: Circle center Y
            radius: Circle radius
            elevation: Height value
            blend_distance: Optional smoothing distance (0 = no smoothing)
        """
        for y in range(self.height):
            for x in range(self.width):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                if dist <= radius:
                    self.grid[y, x] = elevation
        
        print(f"Created circle: center ({center_x},{center_y}), radius {radius}, height {elevation}m")
        
        if blend_distance > 0:
            self.smooth_edges(
                shape_type='circle',
                center_x=center_x,
                center_y=center_y,
                radius=radius,
                blend_distance=blend_distance
            )
    
    def fill_oval(
        self,
        center_x: int,
        center_y: int,
        radius_x: int,
        radius_y: int,
        elevation: float,
        blend_distance: int = 0
    ) -> None:
        """
        Create an oval/ellipse raised area
        
        Args:
            center_x: Oval center X
            center_y: Oval center Y
            radius_x: X-axis radius
            radius_y: Y-axis radius
            elevation: Height value
            blend_distance: Optional smoothing distance (0 = no smoothing)
        """
        for y in range(self.height):
            for x in range(self.width):
                # Ellipse equation: (x-cx)²/rx² + (y-cy)²/ry² <= 1
                normalized = ((x - center_x)**2 / radius_x**2 + 
                            (y - center_y)**2 / radius_y**2)
                if normalized <= 1.0:
                    self.grid[y, x] = elevation
        
        print(f"Created oval: center ({center_x},{center_y}), radii ({radius_x},{radius_y}), height {elevation}m")
        
        if blend_distance > 0:
            self.smooth_edges(
                shape_type='oval',
                center_x=center_x,
                center_y=center_y,
                radius_x=radius_x,
                radius_y=radius_y,
                blend_distance=blend_distance
            )
    
    def add_noise(self, amplitude: float = 0.1) -> None:
        """
        Add random noise to the terrain
        
        Args:
            amplitude: Noise amplitude (±amplitude)
        """
        noise = np.random.uniform(-amplitude, amplitude, self.grid.shape)
        self.grid += noise
        print(f"Added random noise with amplitude ±{amplitude}m")
    
    def add_gradient(
        self,
        direction: Literal['x', 'y'] = 'x',
        start_height: float = 0.0,
        end_height: float = 1.0
    ) -> None:
        """
        Add a linear gradient
        
        Args:
            direction: 'x' or 'y'
            start_height: Height at start
            end_height: Height at end
        """
        if direction == 'x':
            gradient = np.linspace(start_height, end_height, self.width)
            self.grid += gradient[np.newaxis, :]
        elif direction == 'y':
            gradient = np.linspace(start_height, end_height, self.height)
            self.grid += gradient[:, np.newaxis]
        
        print(f"Added {direction}-gradient from {start_height}m to {end_height}m")
    
    def smooth_edges(
        self,
        shape_type: Literal['rectangle', 'circle', 'oval'] = 'rectangle',
        x_start: int = 0,
        y_start: int = 0,
        width: int = 0,
        height: int = 0,
        center_x: int = 0,
        center_y: int = 0,
        radius: int = 0,
        radius_x: int = 0,
        radius_y: int = 0,
        blend_distance: int = 3
    ) -> None:
        """
        Smooth the edges of a raised area with gradual blending
        Blends from full height at the center down to 0 at blend_distance outside the edge
        
        Args:
            shape_type: 'rectangle', 'circle', or 'oval'
            x_start: Rectangle starting X (for rectangle type)
            y_start: Rectangle starting Y (for rectangle type)
            width: Rectangle width (for rectangle type)
            height: Rectangle height (for rectangle type)
            center_x: Circle/oval center X (for circle/oval types)
            center_y: Circle/oval center Y (for circle/oval types)
            radius: Circle radius (for circle type)
            radius_x: Oval X-axis radius (for oval type)
            radius_y: Oval Y-axis radius (for oval type)
            blend_distance: Number of cells to blend over (extends both inside and outside)
        """
        # Store the original height of the raised area
        raised_height: float = 0.0
        
        # Find the raised height
        if shape_type == 'rectangle' and width > 0 and height > 0:
            if y_start < self.height and x_start < self.width:
                # Get height from center of rectangle
                center_y_rect = y_start + height // 2
                center_x_rect = x_start + width // 2
                raised_height = float(self.grid[center_y_rect, center_x_rect])
        elif shape_type == 'circle' and radius > 0:
            if center_y < self.height and center_x < self.width:
                raised_height = float(self.grid[int(center_y), int(center_x)])
        elif shape_type == 'oval':
            if center_y < self.height and center_x < self.width:
                raised_height = float(self.grid[int(center_y), int(center_x)])
        
        # Create new grid for smoothed values
        new_grid: npt.NDArray[np.float32] = np.zeros_like(self.grid)
        
        for y in range(self.height):
            for x in range(self.width):
                # Calculate signed distance from edge
                # Positive = inside shape, Negative = outside shape
                signed_dist: float = 0.0
                
                if shape_type == 'rectangle':
                    # Check if point is inside the rectangle
                    inside_x = x_start <= x < x_start + width
                    inside_y = y_start <= y < y_start + height
                    inside = inside_x and inside_y
                    
                    if inside:
                        # Distance to nearest edge from inside (positive)
                        dist_to_left = x - x_start
                        dist_to_right = (x_start + width - 1) - x
                        dist_to_top = y - y_start
                        dist_to_bottom = (y_start + height - 1) - y
                        signed_dist = float(min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom))
                    else:
                        # Distance from outside (negative)
                        dx = max(0, x_start - x, x - (x_start + width - 1))
                        dy = max(0, y_start - y, y - (y_start + height - 1))
                        signed_dist = -float(max(dx, dy))
                    
                elif shape_type == 'circle':
                    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    signed_dist = radius - dist_from_center
                    
                elif shape_type == 'oval':
                    normalized = np.sqrt((x - center_x)**2 / radius_x**2 + 
                                       (y - center_y)**2 / radius_y**2)
                    # Positive inside, negative outside
                    signed_dist = (1.0 - normalized) * min(radius_x, radius_y)
                
                # Apply blending based on signed distance
                # signed_dist > blend_distance: full height (deep inside)
                # signed_dist = 0: at edge, should be ~50% height
                # signed_dist < -blend_distance: zero height (far outside)
                
                if signed_dist >= blend_distance:
                    # Deep inside - full height
                    new_grid[y, x] = raised_height
                elif signed_dist <= -blend_distance:
                    # Far outside - zero height
                    new_grid[y, x] = 0.0
                else:
                    # In blend zone: interpolate from 0 (at -blend_distance) to full (at +blend_distance)
                    # Map signed_dist from [-blend_distance, +blend_distance] to [0, 1]
                    blend_factor = (signed_dist + blend_distance) / (2 * blend_distance)
                    new_grid[y, x] = raised_height * blend_factor
        
        self.grid = new_grid
        print(f"Smoothed edges with blend distance {blend_distance}")
    
    def write(self, filepath: str) -> None:
        """
        Write the terrain patch to a file
        
        Args:
            filepath: Output .patch file path
        """
        with open(filepath, 'wb') as f:
            # Write header
            f.write(b'PVersion')  # Magic string (8 bytes)
            
            # Write version
            f.write(struct.pack('<I', 8))  # Version 8
            
            # Write metadata (based on observed pattern)
            f.write(struct.pack('<I', 72))  # value_0
            f.write(struct.pack('<I', self.width))  # grid_width
            f.write(struct.pack('<I', self.height))  # grid_height
            f.write(struct.pack('<I', 64))  # value_3
            f.write(struct.pack('<I', 64))  # value_4
            f.write(struct.pack('<I', 320))  # value_5
            f.write(struct.pack('<I', 279))  # value_6
            
            # Write some padding/metadata (observed in original file)
            # These appear to be zeros or specific metadata values
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 4))
            
            # Write some initial pattern (seems to be edge data or metadata)
            # Based on the original file, write some repeated patterns
            for _ in range(8):
                f.write(struct.pack('<I', 0xffffc000))  # Observed pattern (corrected byte order)
            
            # Current position should be at offset 88
            # This is where the actual 65x65 grid data starts
            
            # Write the actual height data (65x65 grid = 4225 floats)
            for y in range(self.height):
                for x in range(self.width):
                    height = self.grid[y, x]
                    f.write(struct.pack('<f', height))
            
            # Pad the rest with the repeating pattern observed in flat areas
            # The original file has additional data after the grid
            remaining_size = 38176 - f.tell()  # Match original file size
            
            if remaining_size > 0:
                # Write repeating pattern
                pattern = struct.pack('<I', 0x00000000)  # Flat terrain pattern
                for _ in range(remaining_size // 4):
                    f.write(pattern)
        
        print(f"\nWrote terrain patch to: {filepath}")
        print(f"Grid size: {self.width}x{self.height}")
        print(f"File size: {38176} bytes")
        print(f"Height range: {np.min(self.grid):.3f} to {np.max(self.grid):.3f}m")
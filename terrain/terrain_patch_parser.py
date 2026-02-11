#!/usr/bin/env python3
"""
Example script demonstrating terrain patch creation and reading
"""

from terrain_patch_writer import TerrainPatchWriter
from terrain_patch_reader import TerrainPatchReader


def read_and_display_terrain(filename: str) -> None:
    """
    Read and display terrain information
    
    Args:
        filename: Path to the .patch file to read
    """
    print(f"\n=== Reading terrain: {filename} ===\n")
    
    terrain = TerrainPatchReader(filename)
    terrain.read()
    terrain.print_statistics()
    terrain.visualize_3d_surface()


def main() -> None:
    """Main function to demonstrate usage"""
    print("=== Terrain Patch Generator ===\n")
    
    terrain = TerrainPatchWriter(65, 65)

    # Create a rectangular bump with smooth edges
    # terrain.fill_rectangle(
    #     x_start=15,
    #     y_start=15,
    #     width=35,
    #     height=25,
    #     elevation=2.5,
    #     blend_distance=7
    # )
    # terrain_name = 'terrain_smooth_rectangle.patch' 
    # terrain.write(terrain_name)
    
    # Read and display one of them
    read_and_display_terrain(r"E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains\c8e19eb6-c009-4041-87df-4f3cde9822d1_4_4.patch")


if __name__ == "__main__":
    main()
import create_lsx
import name_to_uuid
import corridor_generator
import parsers.extract_points_dungeon as extract_points_dungeon
from parsers.parse_terrain_map import _parse_and_update_config
from terrain.terrain_grid_manager import TerrainGridManager
from terrain.terrain_modify_height import modify_terrain
from pyrr import Vector3
from scripts.process_shell_commands import convert_one_file,execute_dungeon_creation,OUTPUT_FOLDER_LSF,MAP_SCENERY_FOLDER
import math

def main() -> None:
    DECREASE_SPACING_OBJECTS = 1
    NAME_OBJECT_WALL = "BLD_Village_Wall_Support_B"
    NAME_FILE_INPUT = r"C:\Users\andre\Downloads\dungeon_complex.ds"

    # Build scenery
    create_lsx.clear_auto_xml(OUTPUT_FOLDER_LSF)
    create_lsx.clear_auto_xml(MAP_SCENERY_FOLDER)
    data_found = name_to_uuid.find_data(NAME_OBJECT_WALL)
    if data_found is None:
        return

    uuid = data_found.uuid
    offset_x = data_found.offset_x * DECREASE_SPACING_OBJECTS

    data_walls, data_inner_walls = extract_points_dungeon.get_points_dungeon(NAME_FILE_INPUT)

    min_x, max_x, min_z, max_z = compute_wall_bounds(data_walls)
    terrain_width  = int(math.ceil(max_x - min_x))
    terrain_height = int(math.ceil(max_z - min_z))

    print(f"Wall bounds: X({min_x:.1f} to {max_x:.1f}), Z({min_z:.1f} to {max_z:.1f})")
    print(f"Required terrain size: {terrain_width} x {terrain_height}")
    
    # Load terrain height map
    CONFIG = r"E:\Games\Baldurs Gate 3\Data\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains\c8e19eb6-c009-4041-87df-4f3cde9822d1.lsx"
    CONFIG_BINARY = CONFIG.replace(".lsx",".lsf")

    convert_one_file(CONFIG_BINARY, CONFIG)
    map_key, total_width, total_height = _parse_and_update_config(CONFIG, terrain_width, terrain_height)
    convert_one_file(CONFIG, CONFIG_BINARY)

    orch = TerrainGridManager(map_key, total_width, total_height)
    modify_terrain(orch.master_buffer)
    
    origin_x, origin_z = orch.master_buffer.shape
    origin_x = (-origin_x / 2) - min_x
    origin_z = (-origin_z / 2) - min_z

    corners = [
        Vector3([min_x, 1, min_z]),
        Vector3([max_x, 1, min_z]),
        Vector3([max_x, 1, max_z]),
        Vector3([min_x, 1, max_z]),
    ]

    for corner in corners:
        corridor_generator.generate_point_helper2(corner)

    build_walls(uuid, offset_x, data_walls, master_buffer=orch.master_buffer, origin_x=origin_x, origin_z=origin_z)

    execute_dungeon_creation()
    
def compute_wall_bounds(data_walls) -> tuple[float, float, float, float]:
    min_x, max_x = float('inf'), float('-inf')
    min_z, max_z = float('inf'), float('-inf')

    for data_polygon in data_walls:
        for line in data_polygon:
            for x, z in line:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_z = min(min_z, z)
                max_z = max(max_z, z)

    return min_x, max_x, min_z, max_z

def build_walls(uuid, offset_x, data_walls, master_buffer, origin_x=0, origin_z=0):
    corridor_generator.generate_point_helper2(Vector3([origin_x, 1,origin_z]))
    for data_polygon in data_walls:
        for line in data_polygon:
            for i in range(len(line) - 1):
                x0, z0 = line[i]
                x1, z1 = line[i + 1]

                dx = x1 - x0
                dz = z1 - z0
                length = math.hypot(dx, dz)
                angle_deg = math.degrees(math.atan2(dz, dx))
                position_iterator = Vector3([x0, 0, z0])
                steps = int(length / offset_x) + 1

                position_iterator = Vector3([x0+origin_x,0,z0+origin_z])

                
                corridor_generator.generate_line(
                    uuid=uuid,
                    position=position_iterator,
                    step=offset_x,
                    angle_deg=angle_deg,
                    length=steps,
                    master_buffer=master_buffer,
                )


if __name__ == "__main__":
    main()

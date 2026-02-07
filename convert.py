import os
import subprocess
import create_lsx
import name_to_uuid
import corridor_generator
import parsers.extract_points_dungeon as extract_points_dungeon
import plot_points
from pyrr import Vector3, Quaternion
import math

DIVINE_EXE = r".\Divine\Divine.exe"
OUTPUT_LSF_TEMP = r"output_lsf_temp"

GAME_ID = "bg3"
ACTION_CONVERT_RESOURCE = "convert-resources"


BG3_MODS_PATH = r"E:\Games\Baldurs Gate 3\Data\Mods"
MOD_ID = "procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068"
LEVEL_PATH = r"Levels\procedural2\Scenery"

OUTPUT_FOLDER_LSF = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    OUTPUT_LSF_TEMP
)
corridor_generator.OUTPUT_FOLDER_LSF = OUTPUT_FOLDER_LSF

MAP_SCENERY_FOLDER = os.path.join(BG3_MODS_PATH, MOD_ID, LEVEL_PATH)



def build_command(divine_exe: str, game_id: str, action: str) -> list[str]:
    return [
        divine_exe,
        "-g", game_id,
        "-a", action,
        "-i", "lsx",
        "-o", "lsf",
        "-s", OUTPUT_FOLDER_LSF,
        "-d", MAP_SCENERY_FOLDER,
    ]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )


def print_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

def main() -> None:
    create_lsx.clear_auto_xml(OUTPUT_FOLDER_LSF)
    create_lsx.clear_auto_xml(MAP_SCENERY_FOLDER)
    data_found = name_to_uuid.find_data("DEC_City_Castlewall_Stone_D")
    if data_found is None:
        return
    
    uuid = data_found.uuid
    offset_x = data_found.offset_x

    data_walls,data_inner_walls = extract_points_dungeon.get_points_dungeon(r"C:\Users\andre\Downloads\dungeon_angled.ds")
    print()
    for a in extract_points_dungeon.dict_ids.values():
        corridor_generator.generate_point_helper(a[1])
    
    # plot_points.construct(data_walls,data_inner_walls)
    build_walls(uuid, offset_x, data_walls)

    command = build_command(DIVINE_EXE, GAME_ID, ACTION_CONVERT_RESOURCE)
    result = run_command(command)
    print_result(result)

def build_walls(uuid, offset_x, data_walls):
    for data_polygon in data_walls:
        for line in data_polygon:
            position_iterator = Vector3([0,0,0])
            
            for i in range(len(line) - 1):
                x0, z0 = line[i]
                x1, z1 = line[i + 1]

                dx = x1 - x0
                dz = z1 - z0

                length = math.hypot(dx, dz)
                angle_deg = math.degrees(math.atan2(dz, dx))
                
                position_iterator = Vector3([x0, 0, z0])
                 
                steps = int(length / offset_x) + 1
                
                
                corridor_generator.generate_line(
                    uuid=uuid,
                    position=position_iterator,
                    step=offset_x,
                    angle_deg=angle_deg,
                    length=steps
                )


if __name__ == "__main__":
    main()

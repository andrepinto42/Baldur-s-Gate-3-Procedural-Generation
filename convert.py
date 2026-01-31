import os
import subprocess
import create_lsx
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
MAP_SCENERY_FOLDER = os.path.join(BG3_MODS_PATH, MOD_ID, LEVEL_PATH)

ITERATIONS = 50

# Base position and offset as Pyrr Vector3
BASE_POSITION = Vector3([0.0, 0.0, 0.0])
OFFSET = Vector3([2.0, 0.0, 2.0])

# Identity quaternion for rotation
IDENTITY_ROTATION = Quaternion()  # defaults to (1,0,0,0) = w,x,y,z


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

TILE_X = 2.0160539150238037
TILE_Z = 0.18953800201416016
# size: [
#       2.3314199447631836,
#       1.4093569871038198,
#       1.4084579944610596
# ],
# "size": [
#       2.0160539150238037,
#       2.964563012123108,
#       
#     ],

WIDTH = 10    # tiles wide
HEIGHT = 8    # tiles tall
import random

TILE = 2.355
CORRIDOR_LENGTH = 50
TURN_CHANCE = 0.3

DIRECTIONS = {
    "E": Vector3([TILE, 0, 0]),
    "W": Vector3([-TILE, 0, 0]),
    "N": Vector3([0, 0, TILE]),
    "S": Vector3([0, 0, -TILE]),
}

PERP = {
    "E": Vector3([0, 0, TILE]),
    "W": Vector3([0, 0, TILE]),
    "N": Vector3([TILE, 0, 0]),
    "S": Vector3([TILE, 0, 0]),
}

def quat_y(deg: float) -> Quaternion:
    return Quaternion.from_y_rotation(math.radians(deg))

ROTATIONS = {
    "N": quat_y(0),
    "S": quat_y(0),
    "E": quat_y(90),
    "W": quat_y(90),
}

def main() -> None:
    create_lsx.clear_auto_xml(OUTPUT_FOLDER_LSF)
    create_lsx.clear_auto_xml(MAP_SCENERY_FOLDER)

    position = BASE_POSITION.copy()

    # Rotation so wall aligns with corridor direction
    wall_rotation = quat_y(90)
    name_uuid = "91ba17fc-e08a-47ee-bbfd-f3f7376dd991"
    for i in range(CORRIDOR_LENGTH):
        # Left wall
        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name=f"WALL_L_{i}",
            template_name=name_uuid,
            position=position + Vector3([TILE_X, 0, 0]),
            rotation=wall_rotation,
            scale=1.0,
        )

        # Right wall
        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name=f"WALL_R_{i}",
            template_name=name_uuid,
            position=position - Vector3([TILE_X, 0, 0]),
            rotation=wall_rotation,
            scale=1.0,
        )

        # Move forward along X
        position += Vector3([0, 0, TILE_X])

    command = build_command(DIVINE_EXE, GAME_ID, ACTION_CONVERT_RESOURCE)
    result = run_command(command)
    print_result(result)


if __name__ == "__main__":
    main()

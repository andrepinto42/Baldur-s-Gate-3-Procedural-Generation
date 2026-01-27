import os
import subprocess
import create_lsx
from pyrr import Vector3, Quaternion

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


def main() -> None:
    position = BASE_POSITION.copy()  # avoid modifying original
    create_lsx.clear_auto_xml(OUTPUT_FOLDER_LSF)

    for _ in range(ITERATIONS):
        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name="MY_CUSTOM_OBJECT_001",
            template_name="af50fe99-a2c4-43fd-8d83-69e3c5781dec",
            position=position,
            rotation=IDENTITY_ROTATION,
            scale=1.0,
        )

        position += Vector3([-0.0527,1.41,1.678])

    command = build_command(DIVINE_EXE, GAME_ID, ACTION_CONVERT_RESOURCE)
    result = run_command(command)
    print_result(result)


if __name__ == "__main__":
    main()

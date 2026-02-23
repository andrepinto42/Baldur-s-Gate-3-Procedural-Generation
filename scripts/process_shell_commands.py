import os
import subprocess
import corridor_generator

###
# E:\Games\Baldurs Gate 3\Data\Editor\Mods\procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068\Levels\procedural2\Terrains
# Folder where it's stored terrain data
##

DIVINE_EXE = r".\Divine\Divine.exe"
OUTPUT_LSF_TEMP = r"..\output_lsf_temp"

GAME_ID = "bg3"
ACTION_CONVERT_RESOURCE = "convert-resources"
ACTION_CONVERT_ONE_RESOURCE = "convert-resource"


BG3_MODS_PATH = r"E:\Games\Baldurs Gate 3\Data\Mods"
MOD_ID = "procedural_ffda7ce9-3f05-0f4a-ee04-84f560c3c068"
NAME_MAP = "procedural2"
LEVEL_PATH = rf"Levels\{NAME_MAP}\Scenery"
OUTPUT_TERRAIN_MAP = rf"E:\Games\Baldurs Gate 3\Data\Editor\Mods\{MOD_ID}\Levels\{NAME_MAP}\Terrains"

OUTPUT_FOLDER_LSF = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    OUTPUT_LSF_TEMP
)
corridor_generator.OUTPUT_FOLDER_LSF = OUTPUT_FOLDER_LSF

MAP_SCENERY_FOLDER = os.path.join(BG3_MODS_PATH, MOD_ID, LEVEL_PATH)

def execute_dungeon_creation():
    command = build_command(DIVINE_EXE, GAME_ID, ACTION_CONVERT_RESOURCE)
    result = run_command(command)
    print_result(result)

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

def convert_one_file(filename_input: str,filename_output: str):
    command = [
        DIVINE_EXE,
        "-g", GAME_ID,
        "-a", ACTION_CONVERT_ONE_RESOURCE,
        "-s", filename_input,
        "-d", filename_output,
    ]
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)


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
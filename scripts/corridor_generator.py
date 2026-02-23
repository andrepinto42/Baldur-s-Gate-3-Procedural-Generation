import create_lsx
from pyrr import Vector3, Quaternion
import math
import random
import numpy as np

OUTPUT_FOLDER_LSF = ""

IDENTITY_ROTATION = Quaternion()
CORRIDOR_LENGTH = 50

def quat_y(deg: float) -> Quaternion:
    return Quaternion.from_y_rotation(-math.radians(deg))

def generate_corridor(uuid: str, position: Vector3, offset_x: float, offset_z: float, angle_deg: float, length: int) -> None:
    rad = math.radians(angle_deg)

    forward = Vector3([
        math.cos(rad) * offset_x,
        0,
        math.sin(rad) * offset_x
    ])

    side = Vector3([
        -math.sin(rad) * offset_x,
        0,
        math.cos(rad) * offset_x
    ])

    rotation = quat_y(angle_deg)

    for i in range(length):
        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name=f"WALL_L_{i}",
            uuid=uuid,
            position=position + side,
            rotation=rotation,
            scale=1.0,
        )

        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name=f"WALL_R_{i}",
            uuid=uuid,
            position=position - side,
            rotation=rotation,
            scale=1.0,
        )

        position += forward


def generate_line(uuid: str, position: Vector3, step: float, angle_deg: float, length: int, master_buffer: np.ndarray) -> None:
    def sample_height(x: float, z: float) -> float:
        rows, cols = master_buffer.shape
        buf_row = int(round(z + rows / 2))
        buf_col = int(round(x + cols / 2))
        
        # Make sure it's not out of bounds
        buf_row = max(0, min(buf_row, rows - 1))
        buf_col = max(0, min(buf_col, cols - 1))
        return float(master_buffer[buf_row, buf_col])

    y_jitter = 0.1
    rot_jitter = 5.0
    base_rad = math.radians(angle_deg)

    forward = Vector3([
        math.cos(base_rad) * step,
        0,
        math.sin(base_rad) * step
    ])

    for _ in range(length):
        y_offset = random.gauss(-y_jitter, y_jitter)
        rot_offset_x = math.radians(random.gauss(0, rot_jitter / 3.0))
        rot_offset_z = math.radians(random.gauss(0, rot_jitter / 3.0))

        terrain_y = sample_height(position.x, position.z)

        pos = Vector3([
            position.x,
            terrain_y + y_offset,
            position.z
        ])

        rotation = Quaternion.from_eulers([rot_offset_x, -math.radians(angle_deg), rot_offset_z])

        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name="SEGMENT",
            uuid=uuid,
            position=pos,
            rotation=rotation,
            scale=1.0,
        )

        position += forward

def generate_point_helper(position: Vector3) -> None:
    create_lsx.create_xml(
        OUTPUT_FOLDER_LSF,
        name="Helper",
        uuid="88f78c11-1f16-4aa2-a1e7-de3b9283a9fe",
        position=position,
        rotation=Quaternion(),
        scale=0.5,
    )

def generate_point_helper2(position: Vector3) -> None:
    create_lsx.create_xml(
        OUTPUT_FOLDER_LSF,
        name="Helper",
        uuid="fa611c6a-9735-4da4-be11-d202e9b1b24b",
        position=position,
        rotation=Quaternion(),
        scale=0.5,
    )
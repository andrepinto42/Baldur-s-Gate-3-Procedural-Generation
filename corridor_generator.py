
import os
import subprocess
import create_lsx
import name_to_uuid
from pyrr import Vector3, Quaternion
import math
import random

OUTPUT_FOLDER_LSF = ""

# Identity quaternion for rotation
IDENTITY_ROTATION = Quaternion()  # defaults to (1,0,0,0) = w,x,y,z
CORRIDOR_LENGTH = 50

def quat_y(deg: float) -> Quaternion:
    return Quaternion.from_y_rotation(-math.radians(deg))

def generate_corridor(uuid,position, offset_x, offset_z,angle_deg,length):
    
    rad = math.radians(angle_deg)

    # Forward direction (corridor direction)
    forward = Vector3([
        math.cos(rad) * offset_x,
        0,
        math.sin(rad) * offset_x
    ])

    # Perpendicular (wall offset)
    side = Vector3([
        -math.sin(rad) * offset_x,
        0,
        math.cos(rad) * offset_x
    ])

    rotation = quat_y(angle_deg)

    for i in range(length):
        # Left wall
        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name=f"WALL_L_{i}",
            uuid=uuid,
            position=position + side,
            rotation=rotation,
            scale=1.0,
        )

        # Right wall
        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name=f"WALL_R_{i}",
            uuid=uuid,
            position=position - side,
            rotation=rotation,
            scale=1.0,
        )

        position += forward

def generate_line(uuid, position, step, angle_deg, length):
    y_jitter=0.1
    rot_jitter=3.0
    base_rad = math.radians(angle_deg)

    # Base forward direction (never randomized)
    forward = Vector3([
        math.cos(base_rad) * step,
        0,
        math.sin(base_rad) * step
    ])

    for _ in range(length):
        # Random offsets
        y_offset = random.gauss(-y_jitter, y_jitter)
        rot_offset = random.uniform(-rot_jitter, rot_jitter)

        # Final position (Y only)
        pos = Vector3([
            position.x,
            position.y + y_offset,
            position.z
        ])

        # Final rotation
        rotation = quat_y(angle_deg + rot_offset)

        create_lsx.create_xml(
            OUTPUT_FOLDER_LSF,
            name="SEGMENT",
            uuid=uuid,
            position=pos,
            rotation=rotation,
            scale=1.0,
        )

        position += forward

def generate_point_helper(position):
    create_lsx.create_xml(
        OUTPUT_FOLDER_LSF,
        name="Helper",
        uuid="88f78c11-1f16-4aa2-a1e7-de3b9283a9fe", # NAT_Underdark_Mushroom_Hat_Small_A
        position=position,
        rotation=Quaternion(),
        scale=0.5,
    )
def generate_point_helper2(position):
    create_lsx.create_xml(
        OUTPUT_FOLDER_LSF,
        name="Helper",
        uuid="fa611c6a-9735-4da4-be11-d202e9b1b24b", #NAT_Underdark_Mushroom_Porcini_Small_C
        position=position,
        rotation=Quaternion(),
        scale=0.5,
    )

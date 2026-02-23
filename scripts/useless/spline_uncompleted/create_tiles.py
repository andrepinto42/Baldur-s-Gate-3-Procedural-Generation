from pyrr import Vector3, Quaternion, vector3, quaternion
import uuid
import math
import plot_points

def parse_vector3(s):
    """Parse space-separated vector string to pyrr Vector3"""
    values = [float(x) for x in s.split()]
    return Vector3(values)

def vector3_to_string(v):
    """Convert pyrr Vector3 to space-separated string"""
    return f"{v[0]} {v[1]} {v[2]}"

def calculate_direction_quaternion(direction):
    """
    Calculate quaternion from direction vector.
    In BG3, this is a Y-axis rotation (horizontal plane).
    Returns quaternion in [x, y, z, w] format.
    """
    direction = vector3.normalize(Vector3([direction[0], 0.0, direction[2]]))
    
    # Calculate angle from forward axis (0, 0, 1)
    angle = math.atan2(direction[0], direction[2])
    
    # Create quaternion from Y rotation
    half_angle = angle / 2.0
    quat = Quaternion([0.0, math.sin(half_angle), 0.0, math.cos(half_angle)])
    
    return quat

def quaternion_to_string(q):
    """Convert quaternion to space-separated string"""
    return f"{q[0]} {q[1]} {q[2]} {q[3]}"

def generate_tiles_from_points(construction_points, path):
    """
    Generate tiles based on construction points and path.
    
    Args:
        construction_points: dict of {id: {position, stretch, helper}}
        path: list of 3 construction point IDs (start, corner, end)
    
    Returns:
        list of tile dictionaries with uuid, translate, rotate, stretchable, tile_guid
    """
    tiles = []
    
    # Tile type GUIDs from your XML
    CORNER_TILE_GUID = "88c8ec1e-dd7b-469c-aefa-af3277e6f6c0"
    STRETCH_TILE_GUID = "21fb351f-b774-461d-a2d2-bd974f4e693f"
    CORNER_INNER_GUID = "6a21259c-ec13-4f00-8afa-f762007c64d2"
    
    # Helper function to find helper point near a construction point
    def find_helper(point_id):
        point_pos = parse_vector3(construction_points[point_id]['position'])
        for helper_id, data in construction_points.items():
            if data['helper']:
                helper_pos = parse_vector3(data['position'])
                dist = vector3.length(helper_pos - point_pos)
                if 0.1 < dist < 2.0:
                    return helper_pos
        return None
    
    # Get the 3 main points
    start_id = path[0]
    corner_id = path[1]
    end_id = path[2]
    
    start_pos = parse_vector3(construction_points[start_id]['position'])
    corner_pos = parse_vector3(construction_points[corner_id]['position'])
    end_pos = parse_vector3(construction_points[end_id]['position'])
    
    # === SEGMENT 1: start -> corner ===
    segment1_vec = corner_pos - start_pos
    segment1_len = vector3.length(segment1_vec)
    segment1_dir = vector3.normalize(segment1_vec)
    
    # Corner tile at start (faces perpendicular using helper)
    helper1 = find_helper(start_id)
    if helper1 is not None:
        helper_dir = helper1 - start_pos
        corner_rot = calculate_direction_quaternion(helper_dir)
    else:
        perp_dir = Vector3([segment1_dir[2], 0.0, -segment1_dir[0]])
        corner_rot = calculate_direction_quaternion(perp_dir)
    
    tiles.append({
        'uuid': str(uuid.uuid4()),
        'tile_guid': CORNER_TILE_GUID,
        'translate': vector3_to_string(start_pos),
        'rotate': quaternion_to_string(corner_rot),
        'stretchable': False,
        'scale_z': 1.0,
        'type': 'corner_start'
    })
    
    # Stretchable tiles along segment 1
    segment1_rot = calculate_direction_quaternion(segment1_dir)
    
    # First stretchable at start position
    tiles.append({
        'uuid': str(uuid.uuid4()),
        'tile_guid': STRETCH_TILE_GUID,
        'translate': vector3_to_string(start_pos),
        'rotate': quaternion_to_string(segment1_rot),
        'stretchable': True,
        'scale_z': 0.9894829,  # From XML
        'type': 'segment1_stretch'
    })
    
    # Additional stretchable tiles at ~4 unit intervals
    current_dist = 4.0
    while current_dist < segment1_len:
        tile_pos = start_pos + segment1_dir * current_dist
        tiles.append({
            'uuid': str(uuid.uuid4()),
            'tile_guid': STRETCH_TILE_GUID,
            'translate': vector3_to_string(tile_pos),
            'rotate': quaternion_to_string(segment1_rot),
            'stretchable': True,
            'scale_z': 0.9894829,
            'type': 'segment1_stretch'
        })
        current_dist += 4.0
    
    # === CORNER POINT ===
    # Inner corner tile at corner position
    tiles.append({
        'uuid': str(uuid.uuid4()),
        'tile_guid': CORNER_INNER_GUID,
        'translate': vector3_to_string(corner_pos),
        'rotate': quaternion_to_string(segment1_rot),
        'stretchable': False,
        'scale_z': 1.0,
        'type': 'corner_inner'
    })
    
    # === SEGMENT 2: corner -> end ===
    segment2_vec = end_pos - corner_pos
    segment2_len = vector3.length(segment2_vec)
    segment2_dir = vector3.normalize(segment2_vec)
    segment2_rot = calculate_direction_quaternion(segment2_dir)
    
    # Stretchable tiles along segment 2
    # Start offset from corner by ~1 unit
    current_dist = 1.0
    while current_dist < segment2_len:
        tile_pos = corner_pos + segment2_dir * current_dist
        tiles.append({
            'uuid': str(uuid.uuid4()),
            'tile_guid': STRETCH_TILE_GUID,
            'translate': vector3_to_string(tile_pos),
            'rotate': quaternion_to_string(segment2_rot),
            'stretchable': True,
            'scale_z': 1.0220633,  # From XML
            'type': 'segment2_stretch'
        })
        current_dist += 4.0
    
    # === END POINT ===
    # Corner tile at end
    helper2 = find_helper(end_id)
    if helper2 is not None:
        # End corner faces along segment direction
        end_corner_rot = calculate_direction_quaternion(segment2_dir)
    else:
        end_corner_rot = calculate_direction_quaternion(segment2_dir)
    
    tiles.append({
        'uuid': str(uuid.uuid4()),
        'tile_guid': CORNER_TILE_GUID,
        'translate': vector3_to_string(end_pos),
        'rotate': quaternion_to_string(end_corner_rot),
        'stretchable': False,
        'scale_z': 1.0,
        'type': 'corner_end'
    })
    
    return tiles

def generate_tiles_from_points(construction_points, path):
    """
    Generate tiles based on construction points and path.
    
    Args:
        construction_points: dict of {id: {position, stretch, helper}}
        path: list of construction point IDs in order (non-helper points only)
    
    Returns:
        list of tile dictionaries with uuid, translate, rotate, stretchable
    """
    tiles = []
    
    # Helper function to find helper point near a construction point
    def find_helper(point_id):
        point_pos = parse_vector3(construction_points[point_id]['position'])
        for helper_id, data in construction_points.items():
            if data['helper']:
                helper_pos = parse_vector3(data['position'])
                dist = vector3.length(helper_pos - point_pos)
                if 0.1 < dist < 2.0:  # Helper is close but not at same position
                    return helper_pos
        return None
    
    # Process each segment
    for i in range(len(path) - 1):
        start_id = path[i]
        end_id = path[i + 1]
        
        start_pos = parse_vector3(construction_points[start_id]['position'])
        end_pos = parse_vector3(construction_points[end_id]['position'])
        
        # Calculate segment direction and length
        segment_vector = end_pos - start_pos
        segment_length = vector3.length(segment_vector)
        segment_dir = vector3.normalize(segment_vector)
        
        # 1. Create corner tile at start point (if it's a stretch point)
        if construction_points[start_id]['stretch']:
            helper_pos = find_helper(start_id)
            
            # Determine rotation
            if helper_pos is not None:
                # Use helper to determine perpendicular direction
                helper_dir = helper_pos - start_pos
                helper_dir = vector3.normalize(helper_dir)
                # Corner faces perpendicular to segment
                corner_rotation = calculate_direction_quaternion(helper_dir)
            else:
                # Rotate 90 degrees from segment direction
                perp_dir = Vector3([-segment_dir[2], 0.0, segment_dir[0]])
                corner_rotation = calculate_direction_quaternion(perp_dir)
            
            tiles.append({
                'uuid': str(uuid.uuid4()),
                'translate': vector3_to_string(start_pos),
                'rotate': quaternion_to_string(corner_rotation),
                'stretchable': False,
                'type': 'corner'
            })
        
        # 2. Create stretchable tiles along segment
        tile_width = 4.0  # Standard tile width
        num_tiles = max(1, int(segment_length / tile_width))
        
        # Calculate rotation for segment tiles (facing along segment)
        segment_rotation = calculate_direction_quaternion(segment_dir)
        
        # Place tiles evenly along segment
        for j in range(num_tiles):
            # Position tiles at regular intervals
            t = (j + 0.5) / num_tiles if num_tiles > 1 else 0.5
            tile_pos = start_pos + segment_vector * t
            
            tiles.append({
                'uuid': str(uuid.uuid4()),
                'translate': vector3_to_string(tile_pos),
                'rotate': quaternion_to_string(segment_rotation),
                'stretchable': True,
                'type': 'segment'
            })
    
    # 3. Create corner tile at end point
    end_id = path[-1]
    end_pos = parse_vector3(construction_points[end_id]['position'])
    
    if construction_points[end_id]['stretch']:
        helper_pos = find_helper(end_id)
        
        # Get direction from previous segment
        prev_start_pos = parse_vector3(construction_points[path[-2]]['position'])
        prev_segment_dir = end_pos - prev_start_pos
        prev_segment_dir = vector3.normalize(prev_segment_dir)
        
        if helper_pos is not None:
            helper_dir = helper_pos - end_pos
            helper_dir = vector3.normalize(helper_dir)
            corner_rotation = calculate_direction_quaternion(helper_dir)
        else:
            # Face opposite to incoming segment
            corner_rotation = calculate_direction_quaternion(-prev_segment_dir)
        
        tiles.append({
            'uuid': str(uuid.uuid4()),
            'translate': vector3_to_string(end_pos),
            'rotate': quaternion_to_string(corner_rotation),
            'stretchable': False,
            'type': 'corner'
        })
    
    return tiles


# Example usage with your data
if __name__ == "__main__":
    construction_points = {
        'ce908085-b558-9148-f463-a5b6d98b8670': {
            'position': '-8.854665 0 66.88342',
            'stretch': True,
            'helper': False
        },
        '55a9b2b1-04d3-4989-8ca3-93f80fded05e': {
            'position': '-8.854665 0 67.88342',
            'stretch': False,
            'helper': True
        },
        '64bc8bc5-5b40-4656-a8de-bb978a7e9907': {
            'position': '1.3218422 0 54.999115',
            'stretch': False,
            'helper': True
        },
        '02122acc-0ff3-fbd3-3cc8-0bebafe5935c': {
            'position': '-8.854664 0 54.99911',
            'stretch': True,
            'helper': False
        },
        'df440b9d-83dd-f7ac-ee64-02809e6f79be': {
            'position': '0.3218422 0 54.999115',
            'stretch': True,
            'helper': False
        }
    }
    
    path = [
        'ce908085-b558-9148-f463-a5b6d98b8670',
        '02122acc-0ff3-fbd3-3cc8-0bebafe5935c',
        'df440b9d-83dd-f7ac-ee64-02809e6f79be'
    ]
    
    tiles = generate_tiles_from_points(construction_points, path)
    
    print("=== GENERATED TILES ===")
    abc = []
    for i, tile in enumerate(tiles):
        lista = tile['translate']
        tuple_a = (lista[0],lista[2])
        abc.append(tuple_a)
        print(f"\nTile {i+1} ({tile['type']}):")
        print(f"  UUID: {tile['uuid']}")
        print(f"  Position: {tile['translate']}")
        print(f"  Rotation: {tile['rotate']}")
        print(f"  Stretchable: {tile['stretchable']}")
    
    lines = plot_points.construction_points_to_polylines(construction_points,path)
    plot_points.draw_polylines(lines)
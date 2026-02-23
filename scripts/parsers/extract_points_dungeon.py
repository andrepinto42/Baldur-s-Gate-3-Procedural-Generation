import re
import json
from pyrr import Vector3, Quaternion
import math
##############################################
# https://www.dungeonscrawl.com/
# Using this website to generate the dungeon
##############################################
dict_ids = {}
SCALE = (26.5 / 953.98) * 2# ≈ 0.02778

def force_better_scale(polygons):
    scaled_polygons = []

    for polygon in polygons:
        scaled_polygon = []

        for x, z in polygon:
            scaled_polygon.append((
                x * SCALE,
                - z * SCALE # Force Z to be inversed so we get a better result in viewing inside the editor
            ))

        scaled_polygons.append(scaled_polygon)

    return scaled_polygons

def get_points_dungeon(filename):
    with open(filename,"r") as f:
        str_found = f.read()
        
    extract_images_objects(str_found)

    match_polygons = re.search(r'\{("polygons":.*?),"polylines":', str_found)
    points = "{" + match_polygons.groups()[0] + "}"

    match_polylines = re.search(r'("polylines":.*?)\}', str_found)
    polylines = "{" + match_polylines.groups()[0] + "}"
    
    data_polygons: list[list[list[tuple[float, float]]]] = json.loads(points)["polygons"]
    data_polylines: list[list[tuple[float, float]]] = json.loads(polylines)["polylines"]
    
    parsed_data_polygons = []
    for a in data_polygons:
        parsed_data_polygons.append(force_better_scale(a))

    parsed_data_polylines = force_better_scale(data_polylines)
    
    return (parsed_data_polygons,parsed_data_polylines)

def extract_images_objects(str_found):
    pattern_id_name = r'"id":"([^"]+)","name":"([^"]+)",([^{]*"dimensions")'
    
    matches = re.findall(pattern_id_name, str_found)
    for assetId, name,_ in matches:
        dict_ids[assetId] = name

    pattern_all_images = r'"name":"([^"]*)"[^}]*'+ \
                         r'"assetId":"([^"]*)"[^}]*'+ \
                         r'"transform":\[([^\]]+)\]'
    
    all_match_transforms = re.findall(pattern_all_images,str_found)
    for nickname,assetId,transform in all_match_transforms:
        if dict_ids[assetId]:
            true_name = dict_ids[assetId]
            a, b, c, d, tx, ty = transform.split(",")
            a = float(a)
            b = float(b)
            tx = float(tx)
            ty = float(ty)
            
            position = Vector3([tx * SCALE, 0, - ty * SCALE])

            angle_radians = math.atan2(b, a)
            rotation = Quaternion.from_y_rotation(angle_radians)
            scale_found = math.sqrt(a*a + b*b)
            
            dict_ids[assetId] = [true_name,position,rotation,scale_found,nickname]
    
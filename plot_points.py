
from typing import Tuple
import matplotlib.pyplot as plt
import re
import json

def parse_vec3_xz(value: str) -> Tuple[float, float]:
    x, _, z = value.split()
    return float(x), float(z)

def build_polylines(
    points: dict,
    paths: list[list[str]]
) -> list[list[tuple[float, float]]]:

    polylines = []

    for path in paths:
        line = []
        for cp_id in path:
            data = points.get(cp_id)
            if not data:
                continue
            pos = data.get("position")
            if not pos:
                continue
            line.append(parse_vec3_xz(pos))

        if len(line) >= 2:
            polylines.append(line)

    return polylines

def build_polylines(data_polygons,data_polylines):
    plot_elements(data_polylines)
    
    for polygon in data_polygons:
        plot_elements(polygon)

def plot_elements(polygon):
    for lines in polygon:
        xs = [p[0] for p in lines]
        ys = [-p[1] for p in lines]

        plt.plot(xs, ys, marker='o')


def construct(data_polygons,data_polylines):
    plt.figure(figsize=(10, 8))

    build_polylines(data_polygons,data_polylines)
    
    plt.axis("equal")
    plt.grid(True)
    plt.xlabel("X")
    plt.ylabel("Z")
    plt.title("Construction Spline (Top-Down)")
    plt.show()


from typing import Tuple
import matplotlib.pyplot as plt

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

def draw_polylines(polylines: list[list[tuple[float, float]]]) -> None:
    plt.figure(figsize=(6, 6))

    for line in polylines:
        xs = [p[0] for p in line]
        ys = [p[1] for p in line]

        plt.plot(xs, ys, marker="o")

    plt.axis("equal")
    plt.grid(True)
    plt.xlabel("X")
    plt.ylabel("Z")
    plt.title("Construction Spline (Top-Down)")
    plt.show()

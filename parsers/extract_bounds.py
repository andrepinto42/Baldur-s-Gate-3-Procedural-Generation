import os
import collada
import numpy as np
import json

ROOT = r"C:\Users\andre\Downloads\bg3-modders-multitool\UnpackedData\Models\Generated\Public\SharedDev\Assets\Output"

OUTPUT_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "data_unpacked",
    "bounds"
)

def analyze_dae(path):
    mins = np.array([np.inf, np.inf, np.inf])
    maxs = np.array([-np.inf, -np.inf, -np.inf])

    dae = collada.Collada(path)

    found = False
    for geom in dae.geometries:
        for prim in geom.primitives:
            if not hasattr(prim, "vertex"):
                continue
            verts = np.asarray(prim.vertex)
            mins = np.minimum(mins, verts.min(axis=0))
            maxs = np.maximum(maxs, verts.max(axis=0))
            found = True

    if not found:
        return None

    size = (maxs - mins).tolist()
    center = ((mins + maxs) * 0.5).tolist()

    return size, center


results = {}

# Find Output* directories
for d in os.listdir(ROOT):
    output_dir = os.path.join(ROOT, d)

    for root, _, files in os.walk(output_dir):
        for file in files:
            if not file.lower().endswith(".dae"):
                continue
            
            dae_path = os.path.join(root, file)

            try:
                analysis = analyze_dae(dae_path)
            except Exception:
                continue

            if analysis is None:
                continue

            size, center = analysis

            # Path after Output*
            relative_path = os.path.relpath(dae_path, ROOT).replace("\\", "/").removeprefix("Output")
            file_name = relative_path.split("/")[0]
            print("Appending to ",file)
            if file_name not in results:
                results[file_name] = []
            
            results[file_name].append({
                "name": file,
                "relative_path": relative_path,
                "size": size,
                "center_offset": center
            })


for key,val in results.items():
    # Write JSON
    with open(os.path.join(OUTPUT_JSON,"my_"+ key), "w", encoding="utf-8") as f:
        json.dump(val, f, indent=2)

    print(f"Wrote {len(results)} entries to {os.path.join(OUTPUT_JSON,"MY",key)}")
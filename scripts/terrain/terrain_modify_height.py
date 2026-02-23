import numpy as np

def modify_terrain(master_buffer: np.ndarray[tuple[int, int], np.dtype[np.float32]]):
    rows, cols = master_buffer.shape
    for r in range(rows):
        for c in range(cols):
            master_buffer[r, c] = np.sin(r / 10.0) * np.cos(c / 10.0) * 5.0
import numpy as np

def modify_terrain(master_buffer: np.ndarray[tuple[int, int], np.dtype[np.float32]]):
    rows, cols = master_buffer.shape
    for r in range(rows):
        for c in range(cols):
            # Height increases as we move away from (0,0)
            master_buffer[r, c] = r/10.0 + c/10.0
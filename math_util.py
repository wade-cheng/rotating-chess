import numpy as np


def point_to_line_distance(
    point: np.ndarray, line_point: np.ndarray, line_vec: np.ndarray
) -> float:
    line_point_to_point: np.ndarray = point - line_point

    parallelogram_area = np.linalg.norm(np.cross(line_vec, line_point_to_point))
    return parallelogram_area / np.linalg.norm(line_vec)


if __name__ == "__main__":
    piece_center = np.array([100, 100])

    # direction <x, y>
    piece_direction_vec = np.array([1, 1])

    cursor_pos = np.array([200, 0])
    print(
        point_to_line_distance(
            point=cursor_pos, line_point=piece_center, line_vec=piece_direction_vec
        )
    )

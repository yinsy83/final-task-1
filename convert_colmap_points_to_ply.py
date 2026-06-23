from pathlib import Path


SRC = Path(
    r"d:\小文件\深度空间作业\期末\task 1\results\A_box\colmap\sparse_txt\points3D.txt"
)
DST = Path(
    r"d:\小文件\深度空间作业\期末\task 1\results\A_box\colmap\sparse_txt\a_box_sparse_points.ply"
)
OBJ_DST = Path(
    r"d:\小文件\深度空间作业\期末\task 1\results\A_box\colmap\sparse_txt\a_box_sparse_cubes.obj"
)
CENTERED_OBJ_DST = Path(
    r"d:\小文件\深度空间作业\期末\task 1\results\A_box\colmap\sparse_txt\a_box_sparse_cubes_centered.obj"
)


def main() -> None:
    points = []
    with SRC.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            x, y, z = map(float, parts[1:4])
            r, g, b = map(int, parts[4:7])
            points.append((x, y, z, r, g, b))

    DST.parent.mkdir(parents=True, exist_ok=True)
    with DST.open("w", encoding="ascii", newline="\n") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for x, y, z, r, g, b in points:
            f.write(f"{x} {y} {z} {r} {g} {b}\n")

    cx = sum(x for x, _, _, _, _, _ in points) / len(points)
    cy = sum(y for _, y, _, _, _, _ in points) / len(points)
    cz = sum(z for _, _, z, _, _, _ in points) / len(points)

    cube_size = 0.01
    half = cube_size / 2.0
    cube_offsets = [
        (-half, -half, -half),
        (half, -half, -half),
        (half, half, -half),
        (-half, half, -half),
        (-half, -half, half),
        (half, -half, half),
        (half, half, half),
        (-half, half, half),
    ]
    cube_faces = [
        (1, 2, 3, 4),
        (5, 6, 7, 8),
        (1, 5, 8, 4),
        (2, 6, 7, 3),
        (4, 3, 7, 8),
        (1, 2, 6, 5),
    ]
    with OBJ_DST.open("w", encoding="ascii", newline="\n") as f:
        f.write("# Sparse COLMAP points as small cubes\n")
        vertex_index = 1
        for i, (x, y, z, _r, _g, _b) in enumerate(points, start=1):
            f.write(f"o point_{i}\n")
            for dx, dy, dz in cube_offsets:
                f.write(f"v {x + dx} {y + dy} {z + dz}\n")
            for a, b, c, d in cube_faces:
                f.write(
                    f"f {vertex_index + a - 1} {vertex_index + b - 1} "
                    f"{vertex_index + c - 1} {vertex_index + d - 1}\n"
                )
            vertex_index += 8

    with CENTERED_OBJ_DST.open("w", encoding="ascii", newline="\n") as f:
        f.write("# Sparse COLMAP points as small cubes centered around origin\n")
        vertex_index = 1
        for i, (x, y, z, _r, _g, _b) in enumerate(points, start=1):
            x -= cx
            y -= cy
            z -= cz
            f.write(f"o point_{i}\n")
            for dx, dy, dz in cube_offsets:
                f.write(f"v {x + dx} {y + dy} {z + dz}\n")
            for a, b, c, d in cube_faces:
                f.write(
                    f"f {vertex_index + a - 1} {vertex_index + b - 1} "
                    f"{vertex_index + c - 1} {vertex_index + d - 1}\n"
                )
            vertex_index += 8

    print(f"saved: {DST}")
    print(f"saved: {OBJ_DST}")
    print(f"saved: {CENTERED_OBJ_DST}")
    print(f"points: {len(points)}")


if __name__ == "__main__":
    main()

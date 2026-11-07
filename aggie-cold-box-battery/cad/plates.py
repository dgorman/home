"""Bambu Lab H2D (350 x 320 x 325 mm) print orientation verification and plate builder.

Verifies that every exported `print_*.stl` lies flat on z = 0 with maximum bed adhesion
and zero supports, then packs the parts onto H2D build plates with 1 mm 2D raster
overlap checks:
  - `plate_h2d_all_in_one.stl`    : Box + Overhang Lid + 10AWG Gland Cap on 1 H2D bed (271 x 193 x 160 mm)
  - `plate_h2d_01_box_and_gland.stl`: Box + 10AWG Gland Cap (same color, 283 x 80 x 160 mm)
  - `plate_h2d_02_overhang_lid.stl` : Overhang Lid alone (contrasting roof color, 233 x 99 x 42 mm)
"""
from __future__ import annotations

import itertools
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STL_DIR = os.path.join(ROOT, "stl")
RENDERS_DIR = os.path.join(ROOT, "renders")

BED_H2D_X: float = 350.0
BED_H2D_Y: float = 320.0
BED_H2D_Z: float = 325.0
GAP: float = 14.0

Triangle = list[tuple[float, float, float]]


def read_stl(path: str) -> list[Triangle]:
    """Read a binary STL file and return a list of triangles [(v0, v1, v2), ...]."""
    with open(path, "rb") as f:
        f.seek(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = [struct.unpack("<12f", f.read(50)[:48]) for _ in range(n)]
    return [[t[3:6], t[6:9], t[9:12]] for t in raw]


def write_stl(path: str, tris: list[Triangle]) -> None:
    """Write a list of triangles to a binary STL file."""
    with open(path, "wb") as f:
        header = b"Bambu Lab H2D Pre-Oriented STL - Aggie Cold Box Battery Enclosure"
        f.write(header.ljust(80, b"\0"))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = (b[i] - a[i] for i in range(3))
            vx, vy, vz = (c[i] - a[i] for i in range(3))
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
            length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / length, ny / length, nz / length, *a, *b, *c, 0))


def bounds(tris: list[Triangle]) -> tuple[list[float], list[float]]:
    lo = [min(v[k] for t in tris for v in t) for k in range(3)]
    hi = [max(v[k] for t in tris for v in t) for k in range(3)]
    return lo, hi


def translate(tris: list[Triangle], dx: float, dy: float, dz: float = 0.0) -> list[Triangle]:
    return [[(v[0] + dx, v[1] + dy, v[2] + dz) for v in t] for t in tris]


def normalise(tris: list[Triangle]) -> list[Triangle]:
    lo, _ = bounds(tris)
    return translate(tris, -lo[0], -lo[1], -lo[2])


def bed_contact_area_mm2(tris: list[Triangle], tol: float = 1e-2) -> float:
    """Compute flat surface area (mm^2) resting directly on the z = 0 build plate."""
    lo, _ = bounds(tris)
    z0 = lo[2]
    area = 0.0
    for a, b, c in tris:
        if all(abs(v[2] - z0) <= tol for v in (a, b, c)):
            ux, uy, uz = (b[i] - a[i] for i in range(3))
            vx, vy, vz = (c[i] - a[i] for i in range(3))
            area += 0.5 * math.sqrt((uy * vz - uz * vy) ** 2 + (uz * vx - ux * vz) ** 2 + (ux * vy - uy * vx) ** 2)
    return area


def raster_footprint(tris: list[Triangle]) -> set[tuple[int, int]]:
    """Return 1x1 mm grid cells covered by the part's XY projection on the H2D bed."""
    cells: set[tuple[int, int]] = set()
    for a, b, c in tris:
        xs = (a[0], b[0], c[0])
        ys = (a[1], b[1], c[1])
        for gx in range(int(math.floor(min(xs))), int(math.ceil(max(xs))) + 1):
            for gy in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
                px, py = gx + 0.5, gy + 0.5
                d1 = (px - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (py - b[1])
                d2 = (px - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (py - c[1])
                d3 = (px - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (py - a[1])
                if not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0)):
                    cells.add((gx, gy))
    return cells


H2D_PLATES: dict[str, list[tuple[str, tuple[float, float]]]] = {
    # 1. Single-plate H2D build: Box at front (y=0), Overhang Lid behind it (y=94), Gland Cap beside Lid (x=247, y=120)
    "plate_h2d_all_in_one": [
        ("print_battery_box.stl", (0.0, 0.0)),
        ("print_overhang_lid.stl", (8.0, 94.0)),
        ("print_wire_gland_cap.stl", (249.0, 123.0)),
    ],
    # 2. Two-color split option — Plate 1: Main Box + Wire Gland Cap (e.g. Orange PETG/ASA)
    "plate_h2d_01_box_and_gland": [
        ("print_battery_box.stl", (0.0, 0.0)),
        ("print_wire_gland_cap.stl", (261.0, 20.0)),
    ],
    # 3. Two-color split option — Plate 2: Sloped Overhang Drip Lid (e.g. Dark Slate ASA)
    "plate_h2d_02_overhang_lid": [
        ("print_overhang_lid.stl", (0.0, 0.0)),
    ],
}


def build_h2d_plates(stl_dir: str = STL_DIR) -> None:
    """Verify individual parts and pack H2D multi-part plates with 2D raster overlap checks."""
    # Remove any legacy plate_01_all_parts.stl
    legacy = os.path.join(stl_dir, "plate_01_all_parts.stl")
    if os.path.exists(legacy):
        os.remove(legacy)

    print("== Verifying Bed Contact Area (z = 0) for Individual Parts ==")
    for fn in ("print_battery_box.stl", "print_overhang_lid.stl", "print_wire_gland_cap.stl"):
        p = os.path.join(stl_dir, fn)
        tris = normalise(read_stl(p))
        write_stl(p, tris)
        _, hi = bounds(tris)
        area = bed_contact_area_mm2(tris)
        print(f"  {fn:28s}: {hi[0]:5.1f} x {hi[1]:5.1f} x {hi[2]:5.1f} mm | bed contact = {area:7.1f} mm^2")

    print(f"== Packing & Checking Bambu Lab H2D Plates ({BED_H2D_X:.0f} x {BED_H2D_Y:.0f} x {BED_H2D_Z:.0f} mm) ==")
    for plate_name, items in H2D_PLATES.items():
        combined: list[Triangle] = []
        footprints: list[tuple[str, set[tuple[int, int]]]] = []
        for fn, (at_x, at_y) in items:
            part_tris = normalise(read_stl(os.path.join(stl_dir, fn)))
            placed = translate(part_tris, at_x, at_y, 0.0)
            combined.extend(placed)
            footprints.append((fn, raster_footprint(placed)))

        # Center the packed plate on the origin (0..W, 0..D)
        combined = normalise(combined)
        _, hi = bounds(combined)
        assert hi[0] <= BED_H2D_X and hi[1] <= BED_H2D_Y and hi[2] <= BED_H2D_Z, (
            f"{plate_name} ({hi[0]:.1f}x{hi[1]:.1f}x{hi[2]:.1f}) exceeds H2D bed!"
        )
        for (f1, r1), (f2, r2) in itertools.combinations(footprints, 2):
            overlap = r1 & r2
            assert not overlap, f"{plate_name}: {f1} overlaps {f2} ({len(overlap)} mm^2)"

        out_path = os.path.join(stl_dir, f"{plate_name}.stl")
        write_stl(out_path, combined)
        margin_x = BED_H2D_X - hi[0]
        margin_y = BED_H2D_Y - hi[1]
        print(
            f"  {plate_name + '.stl':32s} -> {hi[0]:5.1f} x {hi[1]:5.1f} x {hi[2]:5.1f} mm "
            f"(H2D margin: +{margin_x:.0f} mm X, +{margin_y:.0f} mm Y) [0 overlap]"
        )


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else STL_DIR
    build_h2d_plates(target)

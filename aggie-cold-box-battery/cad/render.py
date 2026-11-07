"""Generate shaded 3D orthographic/isometric PNG views and a 2D cross-section diagram."""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import box

COLORS: dict[str, tuple[float, float, float, float]] = {
    "planter_cedar_wall": (0.68, 0.45, 0.26, 0.45),
    "print_battery_box": (0.85, 0.33, 0.12, 1.0),
    "print_overhang_lid": (0.22, 0.26, 0.31, 0.55),
    "battery_mightymax_12v10ah": (0.16, 0.18, 0.21, 0.96),
    "terminal_pos_f2": (0.88, 0.16, 0.16, 1.0),
    "terminal_neg_f2": (0.10, 0.10, 0.12, 1.0),
    "wire_10awg_pos": (0.90, 0.18, 0.18, 1.0),
    "wire_10awg_neg": (0.15, 0.16, 0.18, 1.0),
}
LIGHT = np.array([0.45, 0.65, 0.62])
LIGHT /= np.linalg.norm(LIGHT)


def subdivide(tri: np.ndarray, max_edge: float = 18.0, depth: int = 0) -> np.ndarray:
    """Split large triangles so painter's sort renders clean intersections."""
    if depth > 4 or len(tri) == 0:
        return tri
    e = np.linalg.norm(tri[:, [1, 2, 0]] - tri, axis=2).max(axis=1)
    big, small = tri[e > max_edge], tri[e <= max_edge]
    if len(big) == 0:
        return tri
    a, b, c = big[:, 0], big[:, 1], big[:, 2]
    ab, bc, ca = (a + b) / 2.0, (b + c) / 2.0, (c + a) / 2.0
    kids = np.concatenate(
        [
            np.stack([a, ab, ca], 1),
            np.stack([ab, b, bc], 1),
            np.stack([ca, bc, c], 1),
            np.stack([ab, bc, ca], 1),
        ]
    )
    return np.concatenate([small, subdivide(kids, max_edge, depth + 1)])


_TRIS_CACHE: dict[tuple[int, float], np.ndarray] = {}


def part_tris(shape: object, tol: float = 0.8) -> np.ndarray:
    key = (id(shape), tol)
    if key not in _TRIS_CACHE:
        verts, tris = shape.tessellate(tol, 0.25)  # type: ignore[attr-defined]
        v = np.array([(p.x, p.y, p.z) for p in verts])
        _TRIS_CACHE[key] = subdivide(v[np.array(tris)])
    return _TRIS_CACHE[key]


def collect(
    asm: box.cq.Assembly,
    hide: tuple[str, ...] = (),
    opaque: tuple[str, ...] = (),
) -> tuple[np.ndarray, np.ndarray]:
    polys, cols = [], []
    for child in asm.children:
        if child.name in hide:
            continue
        shape = child.obj.val() if hasattr(child.obj, "val") else child.obj
        tri = part_tris(shape)
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        shade = 0.55 + 0.45 * np.clip(n @ LIGHT, 0.0, 1.0)
        base = np.array(COLORS.get(child.name, (0.8, 0.4, 0.2, 1.0)))
        if child.name in opaque:
            base[3] = 1.0
        c = np.tile(base, (len(tri), 1))
        c[:, :3] *= shade[:, None]
        polys.append(tri)
        cols.append(c)
    return np.concatenate(polys), np.concatenate(cols)


def render_3d(
    asm: box.cq.Assembly,
    path: str,
    elev: float = 26.0,
    azim: float = -52.0,
    hide: tuple[str, ...] = (),
    opaque: tuple[str, ...] = (),
    title: str = "",
) -> None:
    tri, col = collect(asm, hide=hide, opaque=opaque)
    fig = plt.figure(figsize=(13, 8), dpi=130)
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tri, facecolors=col, edgecolors="none", linewidths=0))
    lo, hi = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
    pad = 12.0
    ax.set_xlim(lo[0] - pad, hi[0] + pad)
    ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_zlim(lo[2] - pad, hi[2] + pad)
    ax.set_box_aspect(tuple(hi - lo + 2.0 * pad), zoom=1.14)
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("ortho")
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    if title:
        fig.text(0.02, 0.97, title, fontsize=11.5, fontweight="bold", va="top", family="sans-serif")
    fig.tight_layout(pad=0)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def render_cross_section(path: str) -> None:
    """Draw a 2-panel engineering cross-section: (Left) YZ Side Drip & Gusset Profile, (Right) XZ Front Layout."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.8), dpi=130, gridspec_kw={"width_ratios": [1.0, 1.35]})
    fig.patch.set_facecolor("white")

    # --- Panel 1: YZ Side Cross-Section (Weatherproofing, Overhang Lid, Under-Battery Gusset) ---
    ax1.set_title("A-A Side Cross-Section: Overhang Lid, Labyrinth Seal & Under-Battery Gusset", fontsize=10.5, fontweight="bold", pad=10)
    # Cedar planter back wall (Y = -23 .. -3)
    for z0 in (-55.0, 20.0, 95.0):
        ax1.add_patch(Polygon([(-23, z0), (-3, z0), (-3, z0 + 70), (-23, z0 + 70)], closed=True, facecolor="#b87a4b", edgecolor="#6e4423", alpha=0.65))
    ax1.text(-13, 60, "Aggie Cold Box\nCedar Wall", ha="center", va="center", fontsize=8.5, color="#4a2c14", rotation=90, fontweight="bold")

    # 3 mm Rear Standoff Rib (Y = -3 .. 0, Z = -45 .. 136)
    ax1.add_patch(Polygon([(-3, -45), (0, -45), (0, 136), (-3, 136)], closed=True, facecolor="#f07840", edgecolor="#9e3308", hatch="///", alpha=0.7))

    # Under-Battery Gusset (Y = -3..32..77, Z = -45..0)
    ax1.add_patch(Polygon([(-3, -45), (32, -45), (77, 0), (-3, 0)], closed=True, facecolor="#ea580c", edgecolor="#7a2606", lw=1.3, alpha=0.85))
    ax1.text(28, -22, "5× 6 mm Under-Battery\nGussets (45° Slope)", ha="center", va="center", color="white", fontsize=8.0, fontweight="bold")

    # Lower #10 Screw into Cedar Wall at Z = -26 mm
    ax1.plot([-20, 8], [-26, -26], color="#1e293b", lw=2.6, ls="--")

    # Box Back Wall, Floor, and Front Wall (with Z = 152..160 stepped splash lip)
    box_yz = [
        (0, 0), (77, 0), (77, 152), (74.8, 152), (74.8, 160), (72, 160),
        (72, 5), (5, 5), (5, 160), (0, 160),
    ]
    ax1.add_patch(Polygon(box_yz, closed=True, facecolor="#d9541f", edgecolor="#7a2606", lw=1.4))

    # Floor rib (Y = 8..69, Z = 5..8)
    ax1.add_patch(Polygon([(8, 5), (69, 5), (69, 8), (8, 8)], closed=True, facecolor="#f27441", edgecolor="#7a2606", lw=1.0))

    # Mighty Max 12V 10Ah Battery (Y = 6..71, Z = 8..119) + F2 Terminal (Z = 119..127)
    ax1.add_patch(Polygon([(6, 8), (71, 8), (71, 119), (6, 119)], closed=True, facecolor="#2c3138", edgecolor="#111", lw=1.2))
    ax1.add_patch(Polygon([(52, 119), (62, 119), (62, 127), (52, 127)], closed=True, facecolor="#e02828", edgecolor="#700", lw=1.0))
    ax1.text(38.5, 62, "Mighty Max\n12V 10Ah\n(65 × 111 mm)", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    # Sloped Overhang Lid in YZ Cross-Section (Y = -3..91, Z = 138..179.6, with undercut drip channel at Y = 84.3..87.5, Z = 138..141)
    lid_yz = [
        (-3.0, 179.6), (91.0, 166.4), (91.0, 138.0), (87.5, 138.0),
        (87.5, 141.0), (84.3, 141.0), (84.3, 138.0), (77.6, 138.0),
        (77.6, 152.6), (75.4, 152.6), (75.4, 160.4), (-0.6, 171.0),
        (-0.6, 138.0), (-3.0, 138.0),
    ]
    ax1.add_patch(Polygon(lid_yz, closed=True, facecolor="#38424d", edgecolor="#181d24", lw=1.4, alpha=0.9))

    # Annotations on Panel 1
    ax1.annotate("8° Sloped Roof\n(Snow & Rain Shed)", xy=(45, 173.0), xytext=(22, 192),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax1.annotate("+14 mm Front Eave\n+ Undercut Drip Lip", xy=(88.5, 138.0), xytext=(55, 116),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax1.annotate("8 mm Inner\nLabyrinth Splash Lip", xy=(73.5, 157.0), xytext=(80, 178),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#b91c1c"), fontsize=8.5, fontweight="bold", color="#b91c1c")
    ax1.annotate("Lower #10 Screw\n(Z = -26 mm Support)", xy=(0, -26), xytext=(48, -42),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#7a2606"), fontsize=8.5, fontweight="bold", color="#7a2606")

    ax1.set_xlim(-32, 112)
    ax1.set_ylim(-60, 206)
    ax1.set_aspect("equal")
    ax1.set_xlabel("Y Depth from Planter Wall (mm)")
    ax1.set_ylabel("Z Elevation (mm)")
    ax1.grid(True, linestyle=":", alpha=0.4)

    # --- Panel 2: XZ Front Cross-Section (Battery Bay, Wire Stuffing Bay, Under-Battery Gussets & Direct Wire Holes) ---
    ax2.set_title("B-B Front Cross-Section: Under-Battery Gussets, Extended Mounts & Direct Wire Holes", fontsize=10.5, fontweight="bold", pad=10)

    # Left & Right Mounting Flanges (X = -20..0, 209..229, Z = -45..130)
    ax2.add_patch(Polygon([(-20, -45), (0, -45), (0, 130), (-20, 130)], closed=True, facecolor="#f07840", edgecolor="#7a2606", alpha=0.65))
    ax2.add_patch(Polygon([(209, -45), (229, -45), (229, 130), (209, 130)], closed=True, facecolor="#f07840", edgecolor="#7a2606", alpha=0.65))

    # Lower Back Mounting Apron behind Gussets (X = 0..209, Z = -45..0)
    ax2.add_patch(Polygon([(0, -45), (209, -45), (209, 0), (0, 0)], closed=True, facecolor="#fed7aa", edgecolor="#9a3412", alpha=0.55))

    # 5x 6.0 mm Under-Battery Gussets (Z = -45..0) + 45° Corbel Arches
    gusset_xs = (0.0, 51.0, 103.0, 156.0, 203.0)
    for gx in gusset_xs:
        ax2.add_patch(Polygon([(gx, -45), (gx + 6, -45), (gx + 6, 0), (gx, 0)], closed=True, facecolor="#c2410c", edgecolor="#7a2606", lw=1.2))
    for i in range(4):
        x_l = gusset_xs[i] + 6.0
        x_r = gusset_xs[i + 1]
        xm = 0.5 * (x_l + x_r)
        hw = 0.5 * (x_r - x_l)
        ax2.add_patch(Polygon([(x_l, -hw), (xm, 0), (x_r, -hw), (x_r, 0), (x_l, 0)], closed=True, facecolor="#ea580c", edgecolor="#7a2606", lw=1.0))

    # Main Box XZ Section + 40 mm Cradle Divider at X = 158..162 (No external gland boss/roof!)
    box_xz = [
        (0, 0), (209, 0), (209, 152), (206.8, 152), (206.8, 160), (204, 160), (204, 5),
        (162, 5), (162, 45), (158, 45), (158, 5), (5, 5), (5, 160), (2.2, 160), (2.2, 152), (0, 152),
    ]
    ax2.add_patch(Polygon(box_xz, closed=True, facecolor="#d9541f", edgecolor="#7a2606", lw=1.4))

    # Direct 10 AWG Wire Holes in Right Wall (X = 204..209, Z = 23.1..28.9)
    ax2.add_patch(Polygon([(204, 23.1), (209, 23.1), (209, 28.9), (204, 28.9)], closed=True, facecolor="white", edgecolor="#333", lw=1.0))

    # 3x Floor Ribs (Z = 5..8)
    for rx in (24.0, 81.5, 139.0):
        ax2.add_patch(Polygon([(rx - 4, 5), (rx + 4, 5), (rx + 4, 8), (rx - 4, 8)], closed=True, facecolor="#f27441", edgecolor="#7a2606"))

    # Mighty Max 12V 10Ah Battery (X = 6..157, Z = 8..119) + F2 Terminals
    ax2.add_patch(Polygon([(6, 8), (157, 8), (157, 119), (6, 119)], closed=True, facecolor="#2c3138", edgecolor="#111", lw=1.2))
    ax2.add_patch(Polygon([(138, 119), (148, 119), (148, 127), (138, 127)], closed=True, facecolor="#e02828", edgecolor="#700"))
    ax2.text(81.5, 62, "Mighty Max 12V 10Ah (ML10-12)\n151.0 × 65.0 × 111.0 mm Case\n(153.0 mm Snug Cradle Pocket)", ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")

    # Wire Stuffing Bay Highlight (X = 162..204, Z = 5..160)
    ax2.add_patch(Polygon([(162, 5), (204, 5), (204, 160), (162, 160)], closed=True, facecolor="#fef08a", edgecolor="none", alpha=0.35))
    ax2.text(183, 82, "Excess Wire\n& Fuse Bay\n(42 × 67 × 155 mm)\n+ Zip-Tie Anchors", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#713f12")

    # 2x 10 AWG Wires routing from terminal directly through right-wall holes (Z = 26)
    ax2.plot([143, 185, 185, 224], [126, 126, 26, 26], color="#dc2626", lw=3.2, label="10 AWG +12V")
    ax2.plot([143, 174, 174, 224], [123, 123, 28, 28], color="#1f2937", lw=3.2, label="10 AWG GND")

    # Overhang Lid XZ Section (X = -12..221, Z = 138..174)
    lid_xz = [
        (-12, 174), (221, 174), (221, 138), (217.5, 138), (217.5, 141), (214.3, 141), (214.3, 138),
        (209.6, 138), (209.6, 152.6), (207.4, 152.6), (207.4, 160.4),
        (1.6, 160.4), (1.6, 152.6), (-0.6, 152.6), (-0.6, 138),
        (-5.3, 138), (-5.3, 141), (-8.5, 141), (-8.5, 138), (-12, 138),
    ]
    ax2.add_patch(Polygon(lid_xz, closed=True, facecolor="#38424d", edgecolor="#181d24", lw=1.4, alpha=0.9))

    # Mounting Screw Holes on Flanges & Under-Battery Apron (Z = -26 mm, 35 mm, 96/105 mm keyhole)
    for sx in (-10.0, 219.0):
        ax2.add_patch(Circle((sx, -26.0), 2.6, facecolor="white", edgecolor="#333", lw=1.2))
        ax2.add_patch(Circle((sx, 35.0), 2.6, facecolor="white", edgecolor="#333", lw=1.2))
        ax2.add_patch(Circle((sx, 105.0), 2.6, facecolor="white", edgecolor="#333", lw=1.2))
        ax2.add_patch(Circle((sx, 96.0), 5.2, facecolor="white", edgecolor="#333", lw=1.2))
    for cx_low in (80.0, 132.5):
        ax2.add_patch(Circle((cx_low, -26.0), 2.6, facecolor="white", edgecolor="#333", lw=1.2))

    ax2.annotate("2× Ø5.8 mm Direct\n10 AWG Wire Holes", xy=(209, 26), xytext=(168, -54),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax2.annotate("5× 6 mm Gussets + 4× Lower\n#10 Screws at Z = -26 mm", xy=(80, -26), xytext=(22, -55),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#7a2606"), fontsize=8.5, fontweight="bold", color="#7a2606")
    ax2.annotate("+12 mm Side Overhang\n+ M4 Locking Screw", xy=(-12, 145), xytext=(-28, 188),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")

    ax2.set_xlim(-32, 242)
    ax2.set_ylim(-60, 206)
    ax2.set_aspect("equal")
    ax2.set_xlabel("X Width Across Planter Back (mm)")
    ax2.set_ylabel("Z Elevation (mm)")
    ax2.grid(True, linestyle=":", alpha=0.4)

    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def render_h2d_plate(path: str) -> None:
    """Render a 2-panel Bambu Lab H2D (350 x 320 mm) Build Plate visual guide (3D Iso on Bed + 2D Footprint Map)."""
    import plates

    fig = plt.figure(figsize=(15, 7.2), dpi=130)
    fig.patch.set_facecolor("white")

    # --- Panel 1: 3D Isometric View of `plate_h2d_all_in_one.stl` on the 350 x 320 mm H2D Bed ---
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1.set_title("Bambu Lab H2D (350 × 320 mm Bed) — 2-Part Single-Plate Layout", fontsize=11, fontweight="bold", pad=10)

    # Draw 350 x 320 mm H2D build plate border & 50 mm grid lines at Z = 0 (avoids 3D painter's sort overlap)
    ax1.plot([0, 350, 350, 0, 0], [0, 0, 320, 320, 0], [0, 0, 0, 0, 0], color="#1e293b", lw=2.2)
    for gx in range(50, 350, 50):
        ax1.plot([gx, gx], [0, 320], [0, 0], color="#94a3b8", lw=0.6, ls=":")
    for gy in range(50, 320, 50):
        ax1.plot([0, 350], [gy, gy], [0, 0], color="#94a3b8", lw=0.6, ls=":")

    # Center the 249 x 194.9 mm layout on the 350 x 320 mm H2D bed: offset = (50.5, 62.5)
    off_x, off_y = 50.5, 62.5
    part_specs = [
        ("print_battery_box.stl", (off_x + 0.0, off_y + 0.0), (0.85, 0.33, 0.12, 1.0)),
        ("print_overhang_lid.stl", (off_x + 8.0, off_y + 96.0), (0.28, 0.33, 0.39, 1.0)),
    ]
    for fn, (px, py), rgba in part_specs:
        raw_tris = plates.translate(plates.normalise(plates.read_stl(os.path.join(box.STL_DIR, fn))), px, py, 0.0)
        tri = subdivide(np.array(raw_tris, dtype=float), max_edge=18.0)
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        shade = 0.55 + 0.45 * np.clip(n @ LIGHT, 0.0, 1.0)
        base = np.array(rgba)
        c = np.tile(base, (len(tri), 1))
        c[:, :3] *= shade[:, None]
        ax1.add_collection3d(Poly3DCollection(tri, facecolors=c, edgecolors="none", linewidths=0))

    ax1.set_xlim(-10, 360)
    ax1.set_ylim(-10, 330)
    ax1.set_zlim(0, 215)
    ax1.set_box_aspect((370, 340, 215), zoom=1.08)
    ax1.view_init(elev=30, azim=48)
    ax1.set_proj_type("ortho")
    ax1.set_axis_off()

    # --- Panel 2: 2D Top-Down H2D Build Plate Footprint Map & Slicer Settings ---
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_title("H2D Bed Map (350 × 320 mm) — 100% Support-Free Orientations", fontsize=11, fontweight="bold", pad=10)
    ax2.add_patch(Polygon([(0, 0), (350, 0), (350, 320), (0, 320)], closed=True, facecolor="#1f242b", edgecolor="#0f172a", lw=2.0))

    # Grid lines every 50 mm on the H2D bed
    for gx in range(50, 350, 50):
        ax2.plot([gx, gx], [0, 320], color="#334155", lw=0.7, ls="--")
    for gy in range(50, 320, 50):
        ax2.plot([0, 350], [gy, gy], color="#334155", lw=0.7, ls="--")

    # Part 1: Battery Box (249 x 80 x 205 mm)
    bx0, by0 = off_x, off_y
    ax2.add_patch(Polygon([(bx0, by0), (bx0 + 249, by0), (bx0 + 249, by0 + 80), (bx0, by0 + 80)], closed=True, facecolor="#ea580c", edgecolor="#fdba74", lw=1.6, alpha=0.9))
    ax2.text(bx0 + 124.5, by0 + 40, "1. print_battery_box.stl\n249.0 × 80.0 × 205.0 mm\n(Gusset feet & lower apron on z=0 · 45° corbels · 0 supports)", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")

    # Part 2: Overhang Lid (233 x 98.9 x 41.6 mm)
    lx0, ly0 = off_x + 8.0, off_y + 96.0
    ax2.add_patch(Polygon([(lx0, ly0), (lx0 + 233, ly0), (lx0 + 233, ly0 + 98.9), (lx0, ly0 + 98.9)], closed=True, facecolor="#475569", edgecolor="#cbd5e1", lw=1.6, alpha=0.92))
    ax2.text(lx0 + 116.5, ly0 + 49.5, "2. print_overhang_lid.stl\n233.0 × 98.9 × 41.6 mm\n(Upside-down on sloped roof z=0 · Parallel ceiling z=6.0 · 0 supports)", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")

    ax2.text(175, 18, "Bambu Lab H2D Build Plate: 350 × 320 mm (Packed Envelope: 249 × 195 mm · +101 mm X / +125 mm Y Margin)", ha="center", va="center", color="#94a3b8", fontsize=8.5, fontweight="bold")
    ax2.set_xlim(-10, 360)
    ax2.set_ylim(-10, 330)
    ax2.set_aspect("equal")
    ax2.set_xlabel("H2D Bed X (mm)")
    ax2.set_ylabel("H2D Bed Y (mm)")

    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(box.RENDERS_DIR, exist_ok=True)
    asm = box.build_assembly()

    render_3d(
        asm,
        os.path.join(box.RENDERS_DIR, "iso-assembled.png"),
        elev=24,
        azim=52,
        title="Aggie Cold Box 12V 10Ah Battery Enclosure: Overhang Drip Lid, 5× Under-Battery Gussets & Direct 10AWG Wire Holes",
    )
    render_3d(
        asm,
        os.path.join(box.RENDERS_DIR, "iso-lid-off.png"),
        elev=46,
        azim=52,
        hide=("print_overhang_lid",),
        title="Lid Off: Mighty Max 12V 10Ah in Left Cradle Bay, 42 mm Wire-Stuffing Bay on Right, Under-Battery Gussets & Direct Wire Holes",
    )
    render_3d(
        asm,
        os.path.join(box.RENDERS_DIR, "top-view.png"),
        elev=90,
        azim=-90,
        hide=("print_overhang_lid",),
        title="Top-Down View (Lid Off): 153×67 mm Battery Bay, 42×67 mm Wire Bay, 3 mm Rear Drainage Standoffs & Side Mounting Ears",
    )
    render_3d(
        asm,
        os.path.join(box.RENDERS_DIR, "back-mounting.png"),
        elev=18,
        azim=-60,
        hide=("planter_cedar_wall",),
        opaque=("print_overhang_lid",),
        title="Rear Mounting View: 5× Under-Battery Gussets, Extended Lower #10 Screw Holes (Z = -26 mm) & Upper Drop-On Keyholes",
    )
    render_cross_section(os.path.join(box.RENDERS_DIR, "cross-section-drip.png"))
    render_h2d_plate(os.path.join(box.RENDERS_DIR, "h2d-print-plate.png"))

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
    "print_wire_gland_cap": (0.92, 0.42, 0.18, 1.0),
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
    """Draw a 2-panel engineering cross-section: (Left) YZ Side Drip Profile, (Right) XZ Front Layout."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), dpi=130, gridspec_kw={"width_ratios": [1.0, 1.35]})
    fig.patch.set_facecolor("white")

    # --- Panel 1: YZ Side Cross-Section (Weatherproofing, Overhang Lid & Drip Lip) ---
    ax1.set_title("A-A Side Cross-Section: Snow/Water Overhang & Labyrinth Seal", fontsize=11, fontweight="bold", pad=10)
    # Cedar planter back wall (Y = -23 .. -3)
    for z0 in (-15.0, 53.5, 127.0):
        ax1.add_patch(Polygon([(-23, z0), (-3, z0), (-3, z0 + 70), (-23, z0 + 70)], closed=True, facecolor="#b87a4b", edgecolor="#6e4423", alpha=0.65))
    ax1.text(-13, 90, "Aggie Cold Box\nCedar Wall", ha="center", va="center", fontsize=8.5, color="#4a2c14", rotation=90, fontweight="bold")

    # 3 mm Rear Standoff Rib (Y = -3 .. 0, Z = 0 .. 136)
    ax1.add_patch(Polygon([(-3, 0), (0, 0), (0, 136), (-3, 136)], closed=True, facecolor="#f07840", edgecolor="#9e3308", hatch="///", alpha=0.7))

    # Box Back Wall, Floor, and Front Wall (with Z = 152..162 stepped splash lip)
    box_yz = [
        (0, 0), (77, 0), (77, 152), (74.8, 152), (74.8, 162), (72, 162),
        (72, 5), (5, 5), (5, 162), (0, 162),
    ]
    ax1.add_patch(Polygon(box_yz, closed=True, facecolor="#d9541f", edgecolor="#7a2606", lw=1.4))

    # Floor rib (Y = 8..69, Z = 5..8)
    ax1.add_patch(Polygon([(8, 5), (69, 5), (69, 8), (8, 8)], closed=True, facecolor="#f27441", edgecolor="#7a2606", lw=1.0))

    # Mighty Max 12V 10Ah Battery (Y = 6..71, Z = 8..119) + F2 Terminal (Z = 119..127)
    ax1.add_patch(Polygon([(6, 8), (71, 8), (71, 119), (6, 119)], closed=True, facecolor="#2c3138", edgecolor="#111", lw=1.2))
    ax1.add_patch(Polygon([(52, 119), (62, 119), (62, 127), (52, 127)], closed=True, facecolor="#e02828", edgecolor="#700", lw=1.0))
    ax1.text(38.5, 62, "Mighty Max\n12V 10Ah\n(65 × 111 mm)", ha="center", va="center", color="white", fontsize=9, fontweight="bold")

    # Sloped Overhang Lid in YZ Cross-Section (Y = -3..91, Z = 138..180, with undercut drip channel at Y = 84.3..87.5, Z = 138..141)
    lid_yz = [
        (-3.0, 180.0), (91.0, 167.0), (91.0, 138.0), (87.5, 138.0),
        (87.5, 141.0), (84.3, 141.0), (84.3, 138.0), (77.6, 138.0),
        (77.6, 152.6), (75.4, 152.6), (75.4, 163.0), (-0.6, 163.0),
        (-0.6, 138.0), (-3.0, 138.0),
    ]
    ax1.add_patch(Polygon(lid_yz, closed=True, facecolor="#38424d", edgecolor="#181d24", lw=1.4, alpha=0.9))

    # Annotations on Panel 1
    ax1.annotate("8° Sloped Roof\n(Snow & Rain Shed)", xy=(45, 173.5), xytext=(22, 193),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax1.annotate("+14 mm Front Eave\n+ Undercut Drip Lip", xy=(88.5, 138.0), xytext=(55, 116),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax1.annotate("10 mm Inner\nLabyrinth Splash Lip", xy=(73.5, 158.0), xytext=(82, 178),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#b91c1c"), fontsize=8.5, fontweight="bold", color="#b91c1c")
    ax1.annotate("35 mm Overhead\nWire Clearance", xy=(35, 145), xytext=(10, 142),
                 fontsize=8.5, fontweight="bold", color="#0f5132")
    ax1.annotate("3 mm Drainage\nStandoff Gap", xy=(-1.5, 25), xytext=(-26, -24),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#7a2606"), fontsize=8.5, fontweight="bold", color="#7a2606")

    ax1.set_xlim(-32, 112)
    ax1.set_ylim(-30, 206)
    ax1.set_aspect("equal")
    ax1.set_xlabel("Y Depth from Planter Wall (mm)")
    ax1.set_ylabel("Z Elevation (mm)")
    ax1.grid(True, linestyle=":", alpha=0.4)

    # --- Panel 2: XZ Front Cross-Section (Battery Bay, Wire Stuffing Bay & 2x 10 AWG Gland) ---
    ax2.set_title("B-B Front Cross-Section: Battery Cradle, Wire-Stuffing Bay & 2× 10AWG Gland", fontsize=11, fontweight="bold", pad=10)

    # Left & Right Mounting Flanges (X = -20..0, 209..229, Z = 0..130)
    ax2.add_patch(Polygon([(-20, 0), (0, 0), (0, 130), (-20, 130)], closed=True, facecolor="#f07840", edgecolor="#7a2606", alpha=0.65))
    ax2.add_patch(Polygon([(209, 0), (229, 0), (229, 130), (209, 130)], closed=True, facecolor="#f07840", edgecolor="#7a2606", alpha=0.65))

    # Main Box XZ Section + 40 mm Cradle Divider at X = 158..162 + Right Gland Boss & 45-deg Rain Hood
    box_xz = [
        (0, 0), (209, 0), (209, 6), (218, 15), (218, 37), (225, 37), (225, 41), (209, 55),
        (209, 152), (206.8, 152), (206.8, 162), (204, 162), (204, 5),
        (162, 5), (162, 45), (158, 45), (158, 5), (5, 5), (5, 162), (2.2, 162), (2.2, 152), (0, 152),
    ]
    ax2.add_patch(Polygon(box_xz, closed=True, facecolor="#d9541f", edgecolor="#7a2606", lw=1.4))

    # Gland Cap (X = 218.5 .. 225.5, Z = 15 .. 37)
    ax2.add_patch(Polygon([(218.5, 15), (225.5, 15), (225.5, 37), (218.5, 37)], closed=True, facecolor="#f27441", edgecolor="#7a2606", lw=1.2))

    # 3x Floor Ribs (Z = 5..8)
    for rx in (24.0, 81.5, 139.0):
        ax2.add_patch(Polygon([(rx - 4, 5), (rx + 4, 5), (rx + 4, 8), (rx - 4, 8)], closed=True, facecolor="#f27441", edgecolor="#7a2606"))

    # Mighty Max 12V 10Ah Battery (X = 6..157, Z = 8..119) + F2 Terminals
    ax2.add_patch(Polygon([(6, 8), (157, 8), (157, 119), (6, 119)], closed=True, facecolor="#2c3138", edgecolor="#111", lw=1.2))
    ax2.add_patch(Polygon([(138, 119), (148, 119), (148, 127), (138, 127)], closed=True, facecolor="#e02828", edgecolor="#700"))
    ax2.text(81.5, 62, "Mighty Max 12V 10Ah (ML10-12)\n151.0 × 65.0 × 111.0 mm Case\n(153.0 mm Snug Cradle Pocket)", ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")

    # Wire Stuffing Bay Highlight (X = 162..204, Z = 5..162)
    ax2.add_patch(Polygon([(162, 5), (204, 5), (204, 162), (162, 162)], closed=True, facecolor="#fef08a", edgecolor="none", alpha=0.35))
    ax2.text(183, 82, "Excess Wire\n& Fuse Bay\n(42 × 67 × 157 mm)\n+ Zip-Tie Anchors", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#713f12")

    # 2x 10 AWG Wires routing from terminal to gland (Z = 26)
    ax2.plot([143, 185, 185, 232], [126, 126, 26, 26], color="#dc2626", lw=3.2, label="10 AWG +12V")
    ax2.plot([143, 174, 174, 232], [123, 123, 28, 28], color="#1f2937", lw=3.2, label="10 AWG GND")

    # Overhang Lid XZ Section (X = -12..221, Z = 138..174)
    lid_xz = [
        (-12, 174), (221, 174), (221, 138), (217.5, 138), (217.5, 141), (214.3, 141), (214.3, 138),
        (209.6, 138), (209.6, 152.6), (207.4, 152.6), (207.4, 163),
        (1.6, 163), (1.6, 152.6), (-0.6, 152.6), (-0.6, 138),
        (-5.3, 138), (-5.3, 141), (-8.5, 141), (-8.5, 138), (-12, 138),
    ]
    ax2.add_patch(Polygon(lid_xz, closed=True, facecolor="#38424d", edgecolor="#181d24", lw=1.4, alpha=0.9))

    # Mounting Screw Holes on Flanges
    for sx in (-10.0, 219.0):
        ax2.add_patch(Circle((sx, 28.0), 2.6, facecolor="white", edgecolor="#333"))
        ax2.add_patch(Circle((sx, 105.0), 2.6, facecolor="white", edgecolor="#333"))
        ax2.add_patch(Circle((sx, 96.0), 5.2, facecolor="white", edgecolor="#333"))

    ax2.annotate("2× 10 AWG Split Gland\n+ 45° Rain/Snow Hood", xy=(222, 37), xytext=(175, -22),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax2.annotate("+12 mm Side Overhang\n+ M4 Locking Screw", xy=(-12, 145), xytext=(-28, 190),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#1d4ed8"), fontsize=8.5, fontweight="bold", color="#1d4ed8")
    ax2.annotate("Keyhole Mount\n(#10 Wood Screw)", xy=(-10, 100), xytext=(-28, 60),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#7a2606"), fontsize=8.0, fontweight="bold", color="#7a2606")

    ax2.set_xlim(-32, 242)
    ax2.set_ylim(-30, 206)
    ax2.set_aspect("equal")
    ax2.set_xlabel("X Width Across Planter Back (mm)")
    ax2.set_ylabel("Z Elevation (mm)")
    ax2.grid(True, linestyle=":", alpha=0.4)

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
        title="Aggie Cold Box 12V 10Ah Battery Enclosure: Mounted on Cedar Back Wall (Overhang Drip Lid & 2× 10AWG Gland)",
    )
    render_3d(
        asm,
        os.path.join(box.RENDERS_DIR, "iso-lid-off.png"),
        elev=46,
        azim=52,
        hide=("print_overhang_lid",),
        title="Lid Off: Mighty Max 12V 10Ah in Left Cradle Bay, 42 mm Wire-Stuffing Bay on Right, 10 mm Labyrinth Rim & 10AWG Gland",
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
        title="Rear Mounting View: 4× 3.0 mm Cedar-Wall Drainage Standoffs, Upper Drop-On Keyholes & Lower #10 Screw Holes",
    )
    render_cross_section(os.path.join(box.RENDERS_DIR, "cross-section-drip.png"))

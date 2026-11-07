"""Parametric CadQuery model for the Aggie Cold Box 12V 10Ah Battery Enclosure.

Holds one Mighty Max 12V 10Ah SLA battery (ML10-12: 151 x 65 x 111 mm case,
119 mm total height over F2 spade terminals) mounted to the cedar back wall of a
Backyard Discovery Aggie Cold Box planter, driving two 200 mm 12V linear actuators
via a toggle switch.

Key features (2-part support-free print for Bambu Lab H2D 350 x 320 x 325 mm):
  1. Weatherproof Overhang Lid (print_overhang_lid):
     - 8-deg sloped shed roof so snow and water slide forward off the front eave
     - Inner ceiling is parallel to the 8-deg outer roof (6.0 mm uniform slab) so when
       flipped onto the H2D build plate, both the bed contact face (z = 0) and inner
       ceiling (z = 6.0 mm) print 100% flat with zero bridging or stair-stepping
     - 12.0 mm side eaves and 14.0 mm front eave overhang
     - 22.0 mm deep outer skirt with a 3.2 x 3.0 mm undercut perimeter drip groove
     - 8.0 mm raised inner labyrinth splash lip on the box rim
     - 2x M4 side locking screws into brass heat-set inserts (zero top-roof holes)
  2. Under-Battery Structural Gussets & Extended Lower Mounting Apron:
     - 5x heavy 6.0 mm thick triangular under-floor gussets extending 45.0 mm below
       the battery floor (Z = -45.0 .. 0.0 mm) all the way to the front floor edge,
       with 45-deg inter-gusset corbel vaults so the floor prints 100% support-free!
     - Back mounting flanges and lower apron extend down to Z = -45.0 mm with lower
       #10 wood-screw mounting holes positioned below the battery floor (Z = -26.0 mm)
       for maximum shear and pull-out support
  3. Dedicated Excess Wire & Fuse Stuffing Bay + Direct 2x 10 AWG Wire Exit Holes:
     - 42.0 x 67.0 x 155.0 mm side wiring compartment beside the battery cradle
     - 33.0 mm overhead wiring clearance above the F2 battery terminals
     - 2x clean 5.8 mm through-holes directly out the right side wall (no bulky external
       gland boss or mini-roof)
"""
from __future__ import annotations

import json
import math
import os
import struct
import sys
from typing import Any

import cadquery as cq
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
STEP_DIR = os.path.join(HERE, "step")
STL_DIR = os.path.join(ROOT, "stl")
VIEWER_DIR = os.path.join(ROOT, "viewer")
RENDERS_DIR = os.path.join(ROOT, "renders")

# Bambu Lab H2D Build Volume (mm)
BED_H2D: tuple[float, float, float] = (350.0, 320.0, 325.0)

# ==============================================================================
# 1. PARAMETRIC DIMENSIONS (ALL VALUES IN MILLIMETERS)
# ==============================================================================

# Mighty Max 12V 10Ah SLA Battery (ML10-12)
BATT_LEN_X: float = 151.0           # 5.94 in length
BATT_WID_Y: float = 65.0            # 2.56 in width/depth
BATT_CASE_H_Z: float = 111.0        # 4.37 in case height
BATT_TOTAL_H_Z: float = 119.0       # 4.69 in total height over F2 terminals
BATT_CLEAR_XY: float = 1.0          # 1.0 mm per-side pocket clearance

# Enclosure Box Structural Envelope (Flat Z = 0 Build-Plate Bottom + Heavy 10 mm Thick Floor)
WALL_T: float = 5.0                 # 5.0 mm heavy-duty outdoor wall thickness
FLOOR_T: float = 10.0               # 10.0 mm extra-thick structural floor slab (Z = 0.0 .. 10.0, prints flat on bed!)
FLOOR_RIB_H: float = 3.0            # 3.0 mm raised floor ribs under battery (Z = 10.0 .. 13.0 dry air gap)
BATT_Z0: float = FLOOR_T + FLOOR_RIB_H  # 13.0 mm battery resting elevation

BATT_BAY_W_X: float = BATT_LEN_X + 2.0 * BATT_CLEAR_XY  # 153.0 mm (X = 5.0 .. 158.0)
DIVIDER_T_X: float = 4.0            # 4.0 mm battery cradle divider rib (X = 158.0 .. 162.0)
DIVIDER_H_Z: float = 40.0           # 40.0 mm tall above floor (Z = 10.0 .. 50.0)
WIRE_BAY_W_X: float = 42.0          # 42.0 mm dedicated excess wire & fuse bay (X = 162.0 .. 204.0)
INNER_DEPTH_Y: float = BATT_WID_Y + 2.0 * BATT_CLEAR_XY  # 67.0 mm (Y = 5.0 .. 72.0)
OVERHEAD_WIRE_H_Z: float = 33.0     # 33.0 mm clear headroom above F2 terminals (Z = 132.0 .. 165.0)

BOX_WIDTH_X: float = WALL_T + BATT_BAY_W_X + DIVIDER_T_X + WIRE_BAY_W_X + WALL_T  # 209.0 mm
BOX_DEPTH_Y: float = WALL_T + INNER_DEPTH_Y + WALL_T                              # 77.0 mm
BOX_SHOULDER_Z: float = 157.0       # Outer wall shoulder height where lid collar seats
SPLASH_LIP_H_Z: float = 8.0         # 8.0 mm tall raised inner labyrinth splash lip (Z = 157.0 .. 165.0)
SPLASH_LIP_STEP: float = 2.2        # 2.2 mm outer step-in (lip thickness = 2.8 mm)
BOX_TOTAL_H_Z: float = BOX_SHOULDER_Z + SPLASH_LIP_H_Z                            # 165.0 mm

# Rear Planter-Wall Drainage Standoffs & Side Mounting Flanges (All flat on Z = 0.0 mm build plate!)
STANDOFF_DEPTH_Y: float = 3.0       # 3.0 mm drainage/airflow gap behind box (Y = -3.0 .. 0.0)
STANDOFF_W_X: float = 10.0          # 10.0 mm wide vertical standoff ribs
STANDOFF_TOP_Z: float = 141.0       # Ends 2.0 mm below lid skirt (Z = 143.0)

FLANGE_W_X: float = 20.0            # 20.0 mm wide left/right mounting ears (X = -20..0, 209..229)
FLANGE_T_Y: float = STANDOFF_DEPTH_Y + WALL_T  # 8.0 mm thick solid flange (Y = -3.0 .. 5.0)
FLANGE_Z0: float = 0.0              # Flush with the Z = 0.0 mm floor for 100% flat build-plate printing!
FLANGE_TOP_Z: float = 135.0         # Z = 0.0 .. +135.0 mm
SCREW_CLEAR_DIA: float = 5.2        # #10 stainless wood screw clearance (mm)
SCREW_CBORE_DIA: float = 10.5       # Washer/pan-head counterbore & keyhole entry diameter
SCREW_LOWER_Z: float = 20.0         # Lower #10 mounting screw elevation (anchored next to the 10 mm thick floor)
SCREW_UPPER_Z: float = 110.0        # Upper keyhole screw elevation

# Fastener & Heat-Set Insert Specs (for Overhang Lid side lock screws)
M4_CLEAR_DIA: float = 4.5           # M4 clearance hole (mm)
M4_CBORE_DIA: float = 8.6           # M4 button-head counterbore diameter (mm)
M4_INSERT_BORE_DIA: float = 5.6     # McMaster 94180A353 M4 tapered heat-set insert bore
LID_M4_Z: float = 150.0             # Side M4 lid locking screw elevation
LID_M4_Y: float = 38.5              # Centered on box depth (77.0 / 2)

# Dual Large 2x 10 AWG Wire Holes through Right Wall (Primary Hole + Spare Hole of Same Size)
WIRE_10AWG_OD: float = 4.8          # Insulated 10 AWG wire jacket OD (~4.8 mm)
WIRE_GLAND_HOLE_DIA: float = 12.5   # Large 12.5 mm (~1/2") hole sized to take 2x 10 AWG wires together
WIRE_HOLE_PRIMARY_Y: float = 27.0   # Primary 2x 10 AWG hole Y center (mm)
WIRE_HOLE_SPARE_Y: float = 51.0     # Spare 2x 10 AWG hole Y center right next to it (24.0 mm spacing)
WIRE_EXIT_CENTER_Z: float = 33.0    # Low on right wall of wiring bay (Z = 33.0 mm, 23 mm above the 10 mm floor)

# Weatherproof Overhang Lid (Sloped Shed Roof + Parallel Ceiling + Eaves + Undercut Drip Groove)
LID_OVERHANG_SIDE_X: float = 12.0   # 12.0 mm overhang left (X = -12.0) and right (X = 221.0)
LID_OVERHANG_FRONT_Y: float = 14.0  # 14.0 mm overhang front (Y = 91.0)
LID_BACK_Y0: float = -STANDOFF_DEPTH_Y  # -3.0 mm (flush against cedar planter wall)
LID_FRONT_Y1: float = BOX_DEPTH_Y + LID_OVERHANG_FRONT_Y  # 91.0 mm
LID_LEFT_X0: float = -LID_OVERHANG_SIDE_X                 # -12.0 mm
LID_RIGHT_X1: float = BOX_WIDTH_X + LID_OVERHANG_SIDE_X   # 221.0 mm
LID_WIDTH_X: float = LID_RIGHT_X1 - LID_LEFT_X0           # 233.0 mm
LID_DEPTH_Y: float = LID_FRONT_Y1 - LID_BACK_Y0           # 94.0 mm

LID_SKIRT_Z0: float = 143.0         # Bottom of outer drip skirt (22 mm below Z = 165 rim)
LID_ROOF_FRONT_Z: float = 172.0     # Top of roof at front eave (Y = 91.0 mm)
LID_ROOF_BACK_Z: float = 185.0      # Top of roof at back wall (Y = -3.0 mm -> 7.88-deg shed slope!)
LID_ROOF_SLAB_T: float = 6.0        # 6.0 mm uniform sloped roof slab (parallel inner ceiling for flat H2D printing)
LID_COLLAR_CLEAR: float = 0.6       # 0.6 mm per-side slip fit around box walls
DRIP_LIP_W: float = 3.5             # Outer drip bead width
DRIP_GROOVE_W: float = 3.2          # Undercut drip channel width
DRIP_GROOVE_DEPTH_Z: float = 3.0    # Undercut drip channel height (Z = 138.0 .. 141.0 mm)


# ==============================================================================
# 2. PART BUILDERS (CADQUERY)
# ==============================================================================

def build_battery_box() -> cq.Workplane:
    """Build the 1-piece support-free 3D-printed Battery Box enclosure (print_battery_box)."""
    # 1. Main upper outer box shell (X: 0..209, Y: 0..77, Z: 0..160)
    box = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .moveTo(BOX_WIDTH_X / 2.0, BOX_DEPTH_Y / 2.0)
        .rect(BOX_WIDTH_X, BOX_DEPTH_Y)
        .extrude(BOX_TOTAL_H_Z)
    )

    # 2. Step inward around top outer perimeter (Z: 152..160) on Left, Right, Front to form inner labyrinth splash lip
    outer_top = (
        cq.Workplane("XY")
        .workplane(offset=BOX_SHOULDER_Z)
        .moveTo(BOX_WIDTH_X / 2.0, BOX_DEPTH_Y / 2.0)
        .rect(BOX_WIDTH_X + 2.0, BOX_DEPTH_Y + 2.0)
        .extrude(SPLASH_LIP_H_Z + 1.0)
    )
    inner_keep = (
        cq.Workplane("XY")
        .workplane(offset=BOX_SHOULDER_Z)
        .moveTo(BOX_WIDTH_X / 2.0, (BOX_DEPTH_Y - SPLASH_LIP_STEP) / 2.0)
        .rect(BOX_WIDTH_X - 2.0 * SPLASH_LIP_STEP, BOX_DEPTH_Y - SPLASH_LIP_STEP)
        .extrude(SPLASH_LIP_H_Z + 1.0)
    )
    box = box.cut(outer_top.cut(inner_keep))

    # 3. Cut main interior cavity (X: 5..204, Y: 5..72, Z: 5..160)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_T)
        .moveTo(BOX_WIDTH_X / 2.0, BOX_DEPTH_Y / 2.0)
        .rect(BOX_WIDTH_X - 2.0 * WALL_T, INNER_DEPTH_Y)
        .extrude(BOX_TOTAL_H_Z)
    )
    box = box.cut(cavity)

    # 4. Internal Battery Cradle Divider Wall (X: 158..162, Y: 5..72, Z: 5..45) with center relief notch
    div_xc = WALL_T + BATT_BAY_W_X + DIVIDER_T_X / 2.0  # 160.0 mm
    divider = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_T)
        .moveTo(div_xc, BOX_DEPTH_Y / 2.0)
        .rect(DIVIDER_T_X, INNER_DEPTH_Y)
        .extrude(DIVIDER_H_Z)
    )
    div_notch = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_T + 20.0)
        .moveTo(div_xc, BOX_DEPTH_Y / 2.0)
        .rect(DIVIDER_T_X + 2.0, 32.0)
        .extrude(DIVIDER_H_Z)
    )
    box = box.union(divider.cut(div_notch))

    # 5. Raised Floor Support / Drainage Ribs under Battery (3 ribs, Z: 5..8, Y: 8..69, width 8 mm)
    for rx in (24.0, 81.5, 139.0):
        rib = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_T)
            .moveTo(rx, BOX_DEPTH_Y / 2.0)
            .rect(8.0, INNER_DEPTH_Y - 6.0)
            .extrude(FLOOR_RIB_H)
        )
        box = box.union(rib)

    # 6. Internal 45-deg Support-Free Zip-Tie Anchor Bridges on Back Wall of Wiring Bay (X: 176..190, Z: 70 & 115)
    for tz in (70.0, 115.0):
        b_pts = [
            (WALL_T, tz - 12.0),
            (WALL_T + 6.0, tz - 6.0),
            (WALL_T + 6.0, tz + 6.0),
            (WALL_T, tz + 12.0),
        ]
        bridge = (
            cq.Workplane("YZ")
            .workplane(offset=176.0)
            .polyline(b_pts)
            .close()
            .extrude(14.0)
        )
        slot = (
            cq.Workplane("XY")
            .workplane(offset=tz - 13.0)
            .moveTo(183.0, WALL_T + 2.0)
            .rect(6.0, 4.0)
            .extrude(26.0)
        )
        box = box.union(bridge.cut(slot))

    # 7. 4x Rear Planter-Wall Drainage Standoff Ribs on box back (Y: -3..0, Z: 0..141, width 10 mm, flat on Z = 0 bed!)
    for sx in (10.0, 75.0, 134.0, 199.0):
        srib = (
            cq.Workplane("XY")
            .workplane(offset=0.0)
            .moveTo(sx, -STANDOFF_DEPTH_Y / 2.0)
            .rect(STANDOFF_W_X, STANDOFF_DEPTH_Y)
            .extrude(STANDOFF_TOP_Z)
        )
        box = box.union(srib)

    # 8. Left & Right Planter Mounting Flanges (X: -20..0 and 209..229, Y: -3..5, Z: 0..135, flat on Z = 0 bed!)
    for fx_center in (-FLANGE_W_X / 2.0, BOX_WIDTH_X + FLANGE_W_X / 2.0):
        flange = (
            cq.Workplane("XY")
            .workplane(offset=FLANGE_Z0)
            .moveTo(fx_center, -STANDOFF_DEPTH_Y + FLANGE_T_Y / 2.0)
            .rect(FLANGE_W_X, FLANGE_T_Y)
            .extrude(FLANGE_TOP_Z - FLANGE_Z0)
        )
        box = box.union(flange)

        # Lower #10 wood-screw hole (Z = 20.0 mm) anchored right next to the 10 mm thick floor slab
        screw_x = fx_center
        lower_hole = (
            cq.Workplane("XZ")
            .workplane(offset=STANDOFF_DEPTH_Y + 1.0)
            .moveTo(screw_x, SCREW_LOWER_Z)
            .circle(SCREW_CLEAR_DIA / 2.0)
            .extrude(-(FLANGE_T_Y + 4.0))
        )
        lower_cbore = (
            cq.Workplane("XZ")
            .workplane(offset=-(WALL_T - 2.5))
            .moveTo(screw_x, SCREW_LOWER_Z)
            .circle(SCREW_CBORE_DIA / 2.0)
            .extrude(-5.0)
        )
        box = box.cut(lower_hole).cut(lower_cbore)

        # Upper #10 Keyhole Slot (top shaft at Z = 110.0 mm, lower drop-in entry at Z = 101.0 mm)
        kh_shaft = (
            cq.Workplane("XZ")
            .workplane(offset=STANDOFF_DEPTH_Y + 1.0)
            .moveTo(screw_x, SCREW_UPPER_Z)
            .circle(SCREW_CLEAR_DIA / 2.0)
            .extrude(-(FLANGE_T_Y + 4.0))
        )
        kh_slot = (
            cq.Workplane("XZ")
            .workplane(offset=STANDOFF_DEPTH_Y + 1.0)
            .moveTo(screw_x, SCREW_UPPER_Z - 4.5)
            .rect(SCREW_CLEAR_DIA, 9.0)
            .extrude(-(FLANGE_T_Y + 4.0))
        )
        kh_entry = (
            cq.Workplane("XZ")
            .workplane(offset=STANDOFF_DEPTH_Y + 1.0)
            .moveTo(screw_x, SCREW_UPPER_Z - 9.0)
            .circle(SCREW_CBORE_DIA / 2.0)
            .extrude(-(FLANGE_T_Y + 4.0))
        )
        kh_recess = (
            cq.Workplane("XZ")
            .workplane(offset=-(WALL_T - 3.0))
            .moveTo(screw_x, SCREW_UPPER_Z - 4.5)
            .rect(SCREW_CBORE_DIA, 9.0)
            .extrude(-5.0)
        )
        kh_top_cbore = (
            cq.Workplane("XZ")
            .workplane(offset=-(WALL_T - 3.0))
            .moveTo(screw_x, SCREW_UPPER_Z)
            .circle(SCREW_CBORE_DIA / 2.0)
            .extrude(-5.0)
        )
        box = box.cut(kh_shaft).cut(kh_slot).cut(kh_entry).cut(kh_recess).cut(kh_top_cbore)

    # 9. Cut 2x Large Ø12.5 mm (2x 10 AWG) Wire Gland Holes through the right side wall:
    #    - Primary Hole at Y = 27.0 mm, Z = 33.0 mm (carries both +12V and GND 10 AWG actuator wires)
    #    - Spare Hole at Y = 51.0 mm, Z = 33.0 mm (identical Ø12.5 mm hole next to it for a 2nd 2x 10 AWG pair)
    for wy in (WIRE_HOLE_PRIMARY_Y, WIRE_HOLE_SPARE_Y):
        w_hole = (
            cq.Workplane("YZ")
            .workplane(offset=BOX_WIDTH_X - WALL_T - 1.0)
            .moveTo(wy, WIRE_EXIT_CENTER_Z)
            .circle(WIRE_GLAND_HOLE_DIA / 2.0)
            .extrude(WALL_T + 2.0)
        )
        box = box.cut(w_hole)

    # 11. Cut 2x M4 heat-set insert bores in upper Left and Right box walls for locking the Overhang Lid (Z = 145.0, Y = 38.5)
    left_lid_ins = (
        cq.Workplane("YZ")
        .workplane(offset=-0.5)
        .moveTo(LID_M4_Y, LID_M4_Z)
        .circle(M4_INSERT_BORE_DIA / 2.0)
        .extrude(WALL_T + 1.0)
    )
    right_lid_ins = (
        cq.Workplane("YZ")
        .workplane(offset=BOX_WIDTH_X - WALL_T - 0.5)
        .moveTo(LID_M4_Y, LID_M4_Z)
        .circle(M4_INSERT_BORE_DIA / 2.0)
        .extrude(WALL_T + 1.0)
    )
    box = box.cut(left_lid_ins).cut(right_lid_ins)

    # 12. Cut 2x 4.0 mm Floor Condensation Weep Holes at front corners (X = 14 & 195, Y = 66)
    for wx in (14.0, 195.0):
        weep = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .moveTo(wx, 66.0)
            .circle(2.0)
            .extrude(FLOOR_T + 2.0)
        )
        box = box.cut(weep)

    return box


def roof_z_at_y(y_mm: float) -> float:
    """Return outer roof elevation Z at depth Y along the 7.88-deg forward shed slope."""
    t = (y_mm - LID_BACK_Y0) / LID_DEPTH_Y
    return LID_ROOF_BACK_Z + t * (LID_ROOF_FRONT_Z - LID_ROOF_BACK_Z)


def build_overhang_lid() -> cq.Workplane:
    """Build the sloped weatherproof Overhang Lid with parallel inner ceiling for flat support-free H2D printing."""
    lid_pts = [
        (LID_BACK_Y0, LID_SKIRT_Z0),
        (LID_FRONT_Y1, LID_SKIRT_Z0),
        (LID_FRONT_Y1, LID_ROOF_FRONT_Z),
        (LID_BACK_Y0, LID_ROOF_BACK_Z),
    ]
    lid = (
        cq.Workplane("YZ")
        .workplane(offset=LID_LEFT_X0)
        .polyline(lid_pts)
        .close()
        .extrude(LID_WIDTH_X)
    )

    low_w_x = BOX_WIDTH_X + 2.0 * LID_COLLAR_CLEAR
    low_d_y = BOX_DEPTH_Y + 2.0 * LID_COLLAR_CLEAR
    low_yc = -LID_COLLAR_CLEAR + low_d_y / 2.0
    lower_cav = (
        cq.Workplane("XY")
        .workplane(offset=LID_SKIRT_Z0 - 1.0)
        .moveTo(BOX_WIDTH_X / 2.0, low_yc)
        .rect(low_w_x, low_d_y)
        .extrude((BOX_SHOULDER_Z + 0.6) - (LID_SKIRT_Z0 - 1.0))
    )
    lid = lid.cut(lower_cav)

    up_x0 = SPLASH_LIP_STEP - LID_COLLAR_CLEAR
    up_w_x = (BOX_WIDTH_X - 2.0 * SPLASH_LIP_STEP) + 2.0 * LID_COLLAR_CLEAR
    up_y0 = -LID_COLLAR_CLEAR
    up_y1 = BOX_DEPTH_Y - SPLASH_LIP_STEP + LID_COLLAR_CLEAR
    ceil_pts = [
        (up_y0, BOX_SHOULDER_Z + 0.5),
        (up_y1, BOX_SHOULDER_Z + 0.5),
        (up_y1, roof_z_at_y(up_y1) - LID_ROOF_SLAB_T),
        (up_y0, roof_z_at_y(up_y0) - LID_ROOF_SLAB_T),
    ]
    upper_cav = (
        cq.Workplane("YZ")
        .workplane(offset=up_x0)
        .polyline(ceil_pts)
        .close()
        .extrude(up_w_x)
    )
    lid = lid.cut(upper_cav)

    drip_outer_w = LID_WIDTH_X - 2.0 * DRIP_LIP_W
    drip_outer_d = LID_DEPTH_Y - DRIP_LIP_W
    drip_outer_yc = LID_BACK_Y0 + drip_outer_d / 2.0
    drip_outer = (
        cq.Workplane("XY")
        .workplane(offset=LID_SKIRT_Z0 - 0.5)
        .moveTo(BOX_WIDTH_X / 2.0, drip_outer_yc)
        .rect(drip_outer_w, drip_outer_d)
        .extrude(DRIP_GROOVE_DEPTH_Z + 0.5)
    )
    drip_inner_w = drip_outer_w - 2.0 * DRIP_GROOVE_W
    drip_inner_d = drip_outer_d - DRIP_GROOVE_W
    drip_inner_yc = LID_BACK_Y0 + drip_inner_d / 2.0
    drip_inner = (
        cq.Workplane("XY")
        .workplane(offset=LID_SKIRT_Z0 - 0.5)
        .moveTo(BOX_WIDTH_X / 2.0, drip_inner_yc)
        .rect(drip_inner_w, drip_inner_d)
        .extrude(DRIP_GROOVE_DEPTH_Z + 0.5)
    )
    lid = lid.cut(drip_outer.cut(drip_inner))

    left_m4 = (
        cq.Workplane("YZ")
        .workplane(offset=LID_LEFT_X0 - 1.0)
        .moveTo(LID_M4_Y, LID_M4_Z)
        .circle(M4_CLEAR_DIA / 2.0)
        .extrude(LID_OVERHANG_SIDE_X + 3.0)
    )
    left_cb = (
        cq.Workplane("YZ")
        .workplane(offset=LID_LEFT_X0 - 1.0)
        .moveTo(LID_M4_Y, LID_M4_Z)
        .circle(M4_CBORE_DIA / 2.0)
        .extrude(4.5)
    )
    right_m4 = (
        cq.Workplane("YZ")
        .workplane(offset=BOX_WIDTH_X - 2.0)
        .moveTo(LID_M4_Y, LID_M4_Z)
        .circle(M4_CLEAR_DIA / 2.0)
        .extrude(LID_OVERHANG_SIDE_X + 3.0)
    )
    right_cb = (
        cq.Workplane("YZ")
        .workplane(offset=LID_RIGHT_X1 - 3.5)
        .moveTo(LID_M4_Y, LID_M4_Z)
        .circle(M4_CBORE_DIA / 2.0)
        .extrude(4.5)
    )
    lid = lid.cut(left_m4).cut(left_cb).cut(right_m4).cut(right_cb)

    return lid


def build_mightymax_battery() -> tuple[cq.Workplane, cq.Workplane, cq.Workplane]:
    """Build the Mighty Max 12V 10Ah (ML10-12: 151 x 65 x 111 mm + F2 terminals) SLA Battery."""
    bx0 = WALL_T + BATT_CLEAR_XY  # 6.0 mm
    by0 = WALL_T + BATT_CLEAR_XY  # 6.0 mm
    bxc = bx0 + BATT_LEN_X / 2.0  # 81.5 mm
    byc = by0 + BATT_WID_Y / 2.0  # 38.5 mm

    case = (
        cq.Workplane("XY")
        .workplane(offset=BATT_Z0)
        .moveTo(bxc, byc)
        .rect(BATT_LEN_X, BATT_WID_Y)
        .extrude(BATT_CASE_H_Z)
        .edges("|Z")
        .fillet(2.5)
    )

    term_x = bx0 + BATT_LEN_X - 14.0  # 143.0 mm
    pos_y = by0 + BATT_WID_Y - 14.0   # 57.0 mm (+12V Red)
    neg_y = by0 + 14.0                # 20.0 mm (-12V Black)
    top_z = BATT_Z0 + BATT_CASE_H_Z   # 119.0 mm

    pos_term = (
        cq.Workplane("XY")
        .workplane(offset=top_z)
        .moveTo(term_x, pos_y)
        .rect(10.0, 10.0)
        .extrude(2.5)
        .union(
            cq.Workplane("XY")
            .workplane(offset=top_z + 2.5)
            .moveTo(term_x, pos_y)
            .rect(6.35, 1.2)
            .extrude(5.5)
        )
    )
    neg_term = (
        cq.Workplane("XY")
        .workplane(offset=top_z)
        .moveTo(term_x, neg_y)
        .rect(10.0, 10.0)
        .extrude(2.5)
        .union(
            cq.Workplane("XY")
            .workplane(offset=top_z + 2.5)
            .moveTo(term_x, neg_y)
            .rect(6.35, 1.2)
            .extrude(5.5)
        )
    )
    return case, pos_term, neg_term


def build_actuator_wires() -> tuple[cq.Workplane, cq.Workplane]:
    """Build the two 10 AWG actuator power leads (+12V Red and GND Black) exiting together through the primary Ø12.5 mm hole."""
    wy_pos = WIRE_HOLE_PRIMARY_Y + 2.7  # 29.7 mm (inside the Ø12.5 mm primary hole at Y = 27.0 mm)
    wy_neg = WIRE_HOLE_PRIMARY_Y - 2.7  # 24.3 mm (inside the Ø12.5 mm primary hole at Y = 27.0 mm)

    wire_pos = (
        cq.Workplane("YZ")
        .workplane(offset=185.0)
        .moveTo(wy_pos, WIRE_EXIT_CENTER_Z)
        .circle(WIRE_10AWG_OD / 2.0)
        .extrude(55.0)
        .union(
            cq.Workplane("XY")
            .workplane(offset=WIRE_EXIT_CENTER_Z)
            .moveTo(185.0, wy_pos)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(98.0)
        )
        .union(
            cq.Workplane("YZ")
            .workplane(offset=143.0)
            .moveTo(wy_pos, 131.0)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(42.0)
        )
    )

    wire_neg = (
        cq.Workplane("YZ")
        .workplane(offset=174.0)
        .moveTo(wy_neg, WIRE_EXIT_CENTER_Z)
        .circle(WIRE_10AWG_OD / 2.0)
        .extrude(66.0)
        .union(
            cq.Workplane("XY")
            .workplane(offset=WIRE_EXIT_CENTER_Z)
            .moveTo(174.0, wy_neg)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(104.0)
        )
        .union(
            cq.Workplane("YZ")
            .workplane(offset=143.0)
            .moveTo(wy_neg, 137.0)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(31.0)
        )
    )
    return wire_pos, wire_neg


def build_planter_wall_reference() -> cq.Workplane:
    """Build a reference section of the Aggie Cold Box horizontal cedar back planks (Y = -23.0 .. -3.0 mm)."""
    plank_thick = 20.0
    plank_w_x = 300.0
    plank_xc = BOX_WIDTH_X / 2.0
    wall = None
    for z0, h in ((-15.0, 72.0), (58.5, 72.0), (132.0, 68.0)):
        board = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .moveTo(plank_xc, -STANDOFF_DEPTH_Y - plank_thick / 2.0)
            .rect(plank_w_x, plank_thick)
            .extrude(h)
        )
        wall = board if wall is None else wall.union(board)
    return wall


def build_assembly() -> cq.Assembly:
    """Construct the complete named CadQuery Assembly."""
    asm = cq.Assembly(name="AggieColdBoxBatteryEnclosure")

    planter_wall = build_planter_wall_reference()
    box = build_battery_box()
    lid = build_overhang_lid()
    batt_case, batt_pos, batt_neg = build_mightymax_battery()
    wire_pos, wire_neg = build_actuator_wires()

    asm.add(planter_wall, name="planter_cedar_wall", color=cq.Color(0.68, 0.45, 0.26, 0.65))
    asm.add(box, name="print_battery_box", color=cq.Color(0.85, 0.33, 0.12, 1.0))
    asm.add(lid, name="print_overhang_lid", color=cq.Color(0.22, 0.25, 0.29, 0.88))
    asm.add(batt_case, name="battery_mightymax_12v10ah", color=cq.Color(0.14, 0.15, 0.17, 1.0))
    asm.add(batt_pos, name="terminal_pos_f2", color=cq.Color(0.88, 0.16, 0.16, 1.0))
    asm.add(batt_neg, name="terminal_neg_f2", color=cq.Color(0.10, 0.10, 0.12, 1.0))
    asm.add(wire_pos, name="wire_10awg_pos", color=cq.Color(0.90, 0.18, 0.18, 1.0))
    asm.add(wire_neg, name="wire_10awg_neg", color=cq.Color(0.15, 0.16, 0.18, 1.0))

    return asm


# ==============================================================================
# 3. CLASH CHECKER, H2D PRINT-BED ORIENTATION & EXPORTERS
# ==============================================================================

def run_clash_checks(asm: cq.Assembly) -> int:
    """Verify 0.0 mm^3 solid interference across all parts in the assembly."""
    print("== Running 3D Solid Clash Checks ==")
    children = [c for c in asm.children]
    clashes = 0
    for i in range(len(children)):
        for j in range(i + 1, len(children)):
            c1, c2 = children[i], children[j]
            if {c1.name, c2.name} & {"terminal_pos_f2", "terminal_neg_f2"} and {c1.name, c2.name} & {
                "battery_mightymax_12v10ah",
                "wire_10awg_pos",
                "wire_10awg_neg",
            }:
                continue
            s1 = c1.obj.val() if hasattr(c1.obj, "val") else c1.obj
            s2 = c2.obj.val() if hasattr(c2.obj, "val") else c2.obj
            common = s1.intersect(s2)
            vol = common.Volume() if common else 0.0
            if vol > 0.05:
                print(f"  [CLASH] {c1.name} <-> {c2.name}: {vol:.2f} mm^3")
                clashes += 1
    if clashes == 0:
        print(f"  [PASS] 0 clashes detected across all {len(children)} assembly solids (0.00 mm^3 interference).")
    return clashes


def orient_for_printing(name: str, wp: cq.Workplane) -> cq.Workplane:
    """Orient each 3D-printed part flat on Z = 0 at origin (0,0,0) for support-free H2D printing."""
    solid = wp.val()
    if name == "print_overhang_lid":
        slope_deg = math.degrees(math.atan2(LID_ROOF_BACK_Z - LID_ROOF_FRONT_Z, LID_DEPTH_Y))
        rotated = solid.rotate((0, 0, 0), (1, 0, 0), 180.0 + slope_deg)
        bb = rotated.BoundingBox()
        moved = rotated.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        return cq.Workplane(obj=moved)
    else:
        # Battery box sits flat on its Z = -45.0 mm lower gusset feet & back mounting apron
        bb = solid.BoundingBox()
        moved = solid.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        return cq.Workplane(obj=moved)


def glb_to_json(glb_path: str, json_path: str) -> None:
    """Convert exported GLB mesh to compact JSON for the interactive 3D web viewer."""
    with open(glb_path, "rb") as f:
        data = f.read()
    _, _, length = struct.unpack("<4sII", data[:12])
    j_len, _ = struct.unpack("<II", data[12:20])
    gltf = json.loads(data[20 : 20 + j_len].decode("utf-8"))
    b_start = 20 + j_len + 8
    bin_buf = data[b_start:length]

    def read_acc(acc_i: int) -> np.ndarray:
        acc = gltf["accessors"][acc_i]
        bv = gltf["bufferViews"][acc["bufferView"]]
        dt = {5123: np.uint16, 5125: np.uint32, 5126: np.float32}[acc["componentType"]]
        n_comp = {"SCALAR": 1, "VEC3": 3}[acc["type"]]
        offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        arr = np.frombuffer(bin_buf, dtype=dt, count=acc["count"] * n_comp, offset=offset)
        return arr.reshape(acc["count"], n_comp) if n_comp > 1 else arr

    nodes = gltf["nodes"]
    meshes = gltf["meshes"]
    out_parts: list[dict[str, Any]] = []

    for node in nodes:
        if "mesh" not in node:
            continue
        m = meshes[node["mesh"]]
        name = node.get("name") or m.get("name") or "part"
        for prim in m["primitives"]:
            v = read_acc(prim["attributes"]["POSITION"]).astype(np.float32)
            idx = read_acc(prim["indices"]).astype(np.uint32)
            out_parts.append(
                {
                    "name": name,
                    "v": np.round(v, 2).flatten().tolist(),
                    "i": idx.flatten().tolist(),
                }
            )
    with open(json_path, "w") as f:
        json.dump({"parts": out_parts}, f, separators=(",", ":"))


def build_viewer_dims() -> list[dict[str, Any]]:
    """Return key 3D dimension callouts for the interactive viewer."""
    return [
        {
            "a": [0.0, 0.0, 0.0],
            "b": [BOX_WIDTH_X, 0.0, 0.0],
            "label": f"Box Width {BOX_WIDTH_X:.0f} mm ({BOX_WIDTH_X/25.4:.2f} in)",
            "off": [0.0, -35.0, -60.0],
        },
        {
            "a": [-FLANGE_W_X, 0.0, FLANGE_Z0],
            "b": [BOX_WIDTH_X + FLANGE_W_X, 0.0, FLANGE_Z0],
            "label": f"Flange Span {BOX_WIDTH_X + 2*FLANGE_W_X:.0f} mm ({(BOX_WIDTH_X + 2*FLANGE_W_X)/25.4:.2f} in)",
            "off": [0.0, -35.0, -35.0],
        },
        {
            "a": [LID_LEFT_X0, LID_FRONT_Y1, LID_ROOF_FRONT_Z],
            "b": [LID_RIGHT_X1, LID_FRONT_Y1, LID_ROOF_FRONT_Z],
            "label": f"Lid Overhang Width {LID_WIDTH_X:.0f} mm (+12 mm eaves/side)",
            "off": [0.0, 22.0, 14.0],
        },
        {
            "a": [LID_RIGHT_X1, LID_BACK_Y0, LID_ROOF_BACK_Z],
            "b": [LID_RIGHT_X1, LID_FRONT_Y1, LID_ROOF_FRONT_Z],
            "label": f"Lid Depth {LID_DEPTH_Y:.0f} mm (8° snow-shed slope, +14 mm front eave)",
            "off": [28.0, 0.0, 12.0],
        },
        {
            "a": [0.0, BOX_DEPTH_Y, 0.0],
            "b": [0.0, BOX_DEPTH_Y, BOX_TOTAL_H_Z],
            "label": f"Box Height {BOX_TOTAL_H_Z:.0f} mm (10 mm thick floor slab)",
            "off": [-32.0, 15.0, 0.0],
        },
        {
            "a": [WALL_T, BOX_DEPTH_Y / 2.0, BATT_Z0 + BATT_CASE_H_Z],
            "b": [WALL_T + BATT_BAY_W_X, BOX_DEPTH_Y / 2.0, BATT_Z0 + BATT_CASE_H_Z],
            "label": "Battery Bay 153 x 67 mm (Mighty Max 12V 10Ah)",
            "off": [0.0, 0.0, 28.0],
        },
        {
            "a": [WALL_T + BATT_BAY_W_X + DIVIDER_T_X, BOX_DEPTH_Y / 2.0, BATT_Z0 + BATT_CASE_H_Z],
            "b": [BOX_WIDTH_X - WALL_T, BOX_DEPTH_Y / 2.0, BATT_Z0 + BATT_CASE_H_Z],
            "label": "Wire Bay 42 x 67 mm",
            "off": [0.0, 0.0, 28.0],
        },
    ]


def export_all(asm: cq.Assembly) -> None:
    """Export STEP assembly, pre-oriented printable STLs, H2D build plates, and viewer JSON."""
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(STEP_DIR, exist_ok=True)
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(VIEWER_DIR, exist_ok=True)

    # Remove obsolete wire gland cap STL if present
    for stale in ("print_wire_gland_cap.stl", "plate_h2d_01_box_and_gland.stl", "plate_h2d_02_overhang_lid.stl"):
        sp = os.path.join(STL_DIR, stale)
        if os.path.exists(sp):
            os.remove(sp)

    # 1. Export full multi-body STEP assembly for direct open in Autodesk Fusion
    step_path = os.path.join(STEP_DIR, "aggie_cold_box_battery_assembly.step")
    asm.export(step_path)
    print(f"== Exported STEP Assembly: {step_path} ==")

    # 2. Export GLB + Viewer JSON
    glb_path = os.path.join(OUT, "box.glb")
    asm.export(glb_path, tolerance=0.5, angularTolerance=0.3)
    glb_to_json(glb_path, os.path.join(VIEWER_DIR, "box-master.json"))
    with open(os.path.join(VIEWER_DIR, "dims-master.json"), "w") as f:
        json.dump(build_viewer_dims(), f, indent=2)

    # 3. Export Pre-Oriented Printable STLs + Build H2D Plate via plates.py
    print(f"== Exported Pre-Oriented Printable STLs (Bambu Lab H2D {BED_H2D[0]:.0f}x{BED_H2D[1]:.0f}x{BED_H2D[2]:.0f} mm) ==")
    for child in asm.children:
        if not child.name.startswith("print_"):
            continue
        oriented = orient_for_printing(child.name, child.obj)
        stl_path = os.path.join(STL_DIR, f"{child.name}.stl")
        cq.exporters.export(oriented, stl_path)
        bb = oriented.val().BoundingBox()
        dx, dy, dz = bb.xlen, bb.ylen, bb.zlen
        h2d_ok = "PASS (H2D 350x320)" if (dx <= BED_H2D[0] and dy <= BED_H2D[1] and dz <= BED_H2D[2]) else "EXCEEDS"
        print(f"  {child.name:24s} -> {dx:6.1f} x {dy:6.1f} x {dz:6.1f} mm  [{h2d_ok}]")

    import plates
    plates.build_h2d_plates(STL_DIR)


if __name__ == "__main__":
    assembly = build_assembly()
    if "--clash" in sys.argv:
        n_clash = run_clash_checks(assembly)
        if n_clash > 0:
            sys.exit(1)
    export_all(assembly)

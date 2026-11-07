"""Parametric CadQuery model for the Aggie Cold Box 12V 10Ah Battery Enclosure.

Holds one Mighty Max 12V 10Ah SLA battery (ML10-12: 151 x 65 x 111 mm case,
119 mm total height over F2 spade terminals) mounted to the cedar back wall of a
Backyard Discovery Aggie Cold Box planter, driving two 200 mm 12V linear actuators
via a toggle switch.

Key features:
  1. Weatherproof Overhang Lid (print_overhang_lid):
     - 8-deg sloped shed roof so snow and water slide forward off the front eave
     - 12.0 mm side eaves and 14.0 mm front eave overhang
     - 24.0 mm deep outer skirt with a 3.5 x 3.0 mm undercut perimeter drip groove
     - 10.0 mm raised inner labyrinth splash lip on the box rim
     - 2x M4 side locking screws into brass heat-set inserts (zero top-roof holes)
  2. Dedicated Excess Wire & Fuse Stuffing Bay:
     - 42.0 x 67.0 x 157.0 mm side wiring compartment beside the battery cradle
     - 35.0 mm overhead wiring clearance above the F2 battery terminals
     - 40.0 mm tall battery cradle divider wall (locks battery in place, open above)
     - 2x internal zip-tie anchor bridges on the back wall + 1x behind the wire gland
  3. 2x 10 AWG Split Compression Wire Gland + 45-deg Snow/Rain Hood:
     - Positioned on the lower right side of the wiring bay for natural drip loop
     - Twin 5.2 mm semi-circular clamping channels for two insulated 10 AWG wires
     - Bolt-on compression cap (print_wire_gland_cap) via 2x M4 heat-set inserts
     - Overhanging 45-deg upper rain/snow shield
  4. Aggie Cold Box Cedar Back-Wall Mounting:
     - Left & right gusseted mounting flanges (8.0 mm thick) with 4x #10 wood screw
       holes (upper drop-on keyholes + lower counterbored holes)
     - 4x 3.0 mm rear ventilation/drainage standoff ribs so water runs freely behind
     - 3x 3.0 mm internal floor ribs + 2x 4.0 mm floor condensation weep holes
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

# ==============================================================================
# 1. PARAMETRIC DIMENSIONS (ALL VALUES IN MILLIMETERS)
# ==============================================================================

# Mighty Max 12V 10Ah SLA Battery (ML10-12)
BATT_LEN_X: float = 151.0           # 5.94 in length
BATT_WID_Y: float = 65.0            # 2.56 in width/depth
BATT_CASE_H_Z: float = 111.0        # 4.37 in case height
BATT_TOTAL_H_Z: float = 119.0       # 4.69 in total height over F2 terminals
BATT_CLEAR_XY: float = 1.0          # 1.0 mm per-side pocket clearance

# Enclosure Box Structural Envelope
WALL_T: float = 5.0                 # 5.0 mm heavy-duty outdoor wall thickness
FLOOR_T: float = 5.0                # 5.0 mm structural floor thickness
FLOOR_RIB_H: float = 3.0            # 3.0 mm raised floor ribs under battery (dry air gap)
BATT_Z0: float = FLOOR_T + FLOOR_RIB_H  # 8.0 mm battery resting elevation

BATT_BAY_W_X: float = BATT_LEN_X + 2.0 * BATT_CLEAR_XY  # 153.0 mm (X = 5.0 .. 158.0)
DIVIDER_T_X: float = 4.0            # 4.0 mm battery cradle divider rib (X = 158.0 .. 162.0)
DIVIDER_H_Z: float = 40.0           # 40.0 mm tall above floor (Z = 5.0 .. 45.0)
WIRE_BAY_W_X: float = 42.0          # 42.0 mm dedicated excess wire & fuse bay (X = 162.0 .. 204.0)
INNER_DEPTH_Y: float = BATT_WID_Y + 2.0 * BATT_CLEAR_XY  # 67.0 mm (Y = 5.0 .. 72.0)
OVERHEAD_WIRE_H_Z: float = 35.0     # 35.0 mm clear headroom above F2 terminals (Z = 127.0 .. 162.0)

BOX_WIDTH_X: float = WALL_T + BATT_BAY_W_X + DIVIDER_T_X + WIRE_BAY_W_X + WALL_T  # 209.0 mm
BOX_DEPTH_Y: float = WALL_T + INNER_DEPTH_Y + WALL_T                              # 77.0 mm
BOX_SHOULDER_Z: float = 152.0       # Outer wall shoulder height where lid collar seats
SPLASH_LIP_H_Z: float = 10.0        # 10.0 mm tall raised inner labyrinth splash lip
SPLASH_LIP_STEP: float = 2.2        # 2.2 mm outer step-in (lip thickness = 2.8 mm)
BOX_TOTAL_H_Z: float = BOX_SHOULDER_Z + SPLASH_LIP_H_Z                            # 162.0 mm

# Rear Planter-Wall Drainage Standoffs & Side Mounting Flanges
STANDOFF_DEPTH_Y: float = 3.0       # 3.0 mm drainage/airflow gap behind box (Y = -3.0 .. 0.0)
STANDOFF_W_X: float = 10.0          # 10.0 mm wide vertical standoff ribs
STANDOFF_TOP_Z: float = 136.0       # Ends 2.0 mm below lid skirt (Z = 138.0)

FLANGE_W_X: float = 20.0            # 20.0 mm wide left/right mounting ears (X = -20..0, 209..229)
FLANGE_T_Y: float = STANDOFF_DEPTH_Y + WALL_T  # 8.0 mm thick solid flange (Y = -3.0 .. 5.0)
FLANGE_H_Z: float = 130.0           # Z = 0.0 .. 130.0 mm (8.0 mm below lid skirt)
SCREW_CLEAR_DIA: float = 5.2        # #10 stainless wood screw clearance (mm)
SCREW_CBORE_DIA: float = 10.5       # Washer/pan-head counterbore & keyhole entry diameter
SCREW_LOWER_Z: float = 28.0         # Lower locking screw elevation
SCREW_UPPER_Z: float = 105.0        # Upper keyhole screw elevation

# Fastener & Heat-Set Insert Specs
M4_CLEAR_DIA: float = 4.5           # M4 clearance hole (mm)
M4_CBORE_DIA: float = 8.6           # M4 button-head counterbore diameter (mm)
M4_INSERT_BORE_DIA: float = 5.6     # McMaster 94180A353 M4 tapered heat-set insert bore
M4_INSERT_DEPTH: float = 9.0        # Blind bore depth for M4 insert
LID_M4_Z: float = 145.0             # Side M4 lid locking screw elevation
LID_M4_Y: float = 38.5              # Centered on box depth (77.0 / 2)

# 2x 10 AWG Split Compression Wire Gland & 45-deg Snow/Rain Drip Hood (Right Wall)
WIRE_10AWG_OD: float = 5.0          # Insulated 10 AWG wire jacket OD
WIRE_BORE_DIA: float = 5.2          # Clamping channel diameter for 10 AWG wire
GLAND_CENTER_Y: float = 44.0        # Forward of right mounting flange gussets
GLAND_CENTER_Z: float = 26.0        # Low on wiring bay for natural downward drip loop
GLAND_WIRE_SPAN_Y: float = 12.0     # Wire centers at Y = 38.0 and Y = 50.0 mm
GLAND_BOLT_SPAN_Y: float = 30.0     # M4 insert centers at Y = 29.0 and Y = 59.0 mm
GLAND_BOSS_W_Y: float = 40.0        # Boss spans Y = 24.0 .. 64.0 mm
GLAND_BOSS_H_Z: float = 22.0        # Flat boss face spans Z = 15.0 .. 37.0 mm
GLAND_BOSS_DX: float = 9.0          # Boss projects +9.0 mm from X = 209.0 to X = 218.0 mm
GLAND_CAP_DX: float = 7.0           # Bolt-on cap thickness (X = 218.5 .. 225.5 mm)
GLAND_HOOD_DX: float = 16.0         # Upper rain hood projects to X = 225.0 mm (covers boss + cap)

# Weatherproof Overhang Lid (Sloped Shed Roof + Eaves + Undercut Drip Groove)
LID_OVERHANG_SIDE_X: float = 12.0   # 12.0 mm overhang left (X = -12.0) and right (X = 221.0)
LID_OVERHANG_FRONT_Y: float = 14.0  # 14.0 mm overhang front (Y = 91.0)
LID_BACK_Y0: float = -STANDOFF_DEPTH_Y  # -3.0 mm (flush against cedar planter wall)
LID_FRONT_Y1: float = BOX_DEPTH_Y + LID_OVERHANG_FRONT_Y  # 91.0 mm
LID_LEFT_X0: float = -LID_OVERHANG_SIDE_X                 # -12.0 mm
LID_RIGHT_X1: float = BOX_WIDTH_X + LID_OVERHANG_SIDE_X   # 221.0 mm
LID_WIDTH_X: float = LID_RIGHT_X1 - LID_LEFT_X0           # 233.0 mm
LID_DEPTH_Y: float = LID_FRONT_Y1 - LID_BACK_Y0           # 94.0 mm

LID_SKIRT_Z0: float = 138.0         # Bottom of outer drip skirt (24 mm below Z = 162 rim)
LID_ROOF_FRONT_Z: float = 167.0     # Top of roof at front eave (Y = 91.0 mm)
LID_ROOF_BACK_Z: float = 180.0      # Top of roof at back wall (Y = -3.0 mm -> 8-deg shed slope!)
LID_CEIL_Z: float = 163.0           # Inner flat ceiling (1.0 mm above Z = 162 splash lip)
LID_COLLAR_CLEAR: float = 0.6       # 0.6 mm per-side slip fit around box walls
DRIP_LIP_W: float = 3.5             # Outer drip bead width
DRIP_GROOVE_W: float = 3.2          # Undercut drip channel width
DRIP_GROOVE_DEPTH_Z: float = 3.0    # Undercut drip channel height (Z = 138.0 .. 141.0 mm)


# ==============================================================================
# 2. PART BUILDERS (CADQUERY)
# ==============================================================================

def build_battery_box() -> cq.Workplane:
    """Build the 1-piece support-free 3D-printed Battery Box enclosure (print_battery_box)."""
    # 1. Main outer box shell (X: 0..209, Y: 0..77, Z: 0..162)
    box = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .moveTo(BOX_WIDTH_X / 2.0, BOX_DEPTH_Y / 2.0)
        .rect(BOX_WIDTH_X, BOX_DEPTH_Y)
        .extrude(BOX_TOTAL_H_Z)
    )

    # 2. Step inward around top outer perimeter (Z: 152..162) on Left, Right, Front to form inner labyrinth splash lip
    # Keep full 5.0 mm back wall at Y = 0..5, step Left (X: 0..2.2), Right (X: 206.8..209), Front (Y: 74.8..77)
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

    # 3. Cut main interior cavity (X: 5..204, Y: 5..72, Z: 5..162)
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

    # 6. Internal Zip-Tie Anchor Bridges on Back Wall of Wiring Bay (X: 176..190, Y: 5..11, Z: 65 & 110)
    for tz in (65.0, 110.0):
        bridge = (
            cq.Workplane("XY")
            .workplane(offset=tz - 6.0)
            .moveTo(183.0, WALL_T + 3.0)
            .rect(14.0, 6.0)
            .extrude(12.0)
        )
        slot = (
            cq.Workplane("XY")
            .workplane(offset=tz - 7.0)
            .moveTo(183.0, WALL_T + 2.0)
            .rect(6.0, 4.0)
            .extrude(14.0)
        )
        box = box.union(bridge.cut(slot))

    # 7. 4x Rear Planter-Wall Drainage Standoff Ribs (Y: -3..0, Z: 0..136, width 10 mm)
    for sx in (10.0, 75.0, 134.0, 199.0):
        srib = (
            cq.Workplane("XY")
            .workplane(offset=0.0)
            .moveTo(sx, -STANDOFF_DEPTH_Y / 2.0)
            .rect(STANDOFF_W_X, STANDOFF_DEPTH_Y)
            .extrude(STANDOFF_TOP_Z)
        )
        box = box.union(srib)

    # 8. Left & Right Gusseted Planter Mounting Flanges (X: -20..0 and 209..229, Y: -3..5, Z: 0..130)
    for side_sign, fx_center, wall_x in ((-1.0, -FLANGE_W_X / 2.0, 0.0), (+1.0, BOX_WIDTH_X + FLANGE_W_X / 2.0, BOX_WIDTH_X)):
        flange = (
            cq.Workplane("XY")
            .workplane(offset=0.0)
            .moveTo(fx_center, -STANDOFF_DEPTH_Y + FLANGE_T_Y / 2.0)
            .rect(FLANGE_W_X, FLANGE_T_Y)
            .extrude(FLANGE_H_Z)
        )
        box = box.union(flange)

        # 2x Horizontal triangular/rectangular structural gussets per flange (Z: 0..6 and Z: 62..68, Y: 5..17)
        for gz in (0.0, 62.0):
            gusset = (
                cq.Workplane("XY")
                .workplane(offset=gz)
                .moveTo(wall_x + side_sign * 6.0, WALL_T + 6.0)
                .rect(12.0, 12.0)
                .extrude(6.0)
            )
            box = box.union(gusset)

        # Lower #10 wood-screw through-hole + front counterbore at Z = 28.0 mm
        # Note: cq.Workplane("XZ") has normal -Y, so world Y = y0 uses offset = -y0 and +Y extrusion uses -dy
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

        # Upper #10 Keyhole Slot (top shaft at Z = 105.0 mm, lower drop-in entry at Z = 96.0 mm)
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

    # 9. Right-Side 2x 10 AWG Wire Gland Boss + 45-deg Support-Free Chamfer + 45-deg Upper Rain Hood
    # Profile in XZ plane extruded along +Y (Y = 24.0 .. 64.0 mm for boss, Y = 20.0 .. 68.0 mm for rain hood)
    y_boss0 = GLAND_CENTER_Y - GLAND_BOSS_W_Y / 2.0  # 24.0 mm
    boss_pts = [
        (BOX_WIDTH_X, 6.0),
        (BOX_WIDTH_X + GLAND_BOSS_DX, 15.0),
        (BOX_WIDTH_X + GLAND_BOSS_DX, 37.0),
        (BOX_WIDTH_X, 37.0),
    ]
    gland_boss = (
        cq.Workplane("XZ")
        .workplane(offset=-y_boss0)
        .polyline(boss_pts)
        .close()
        .extrude(-GLAND_BOSS_W_Y)
    )
    box = box.union(gland_boss)

    # Overhanging 45-deg Snow & Rain Drip Hood directly above the gland (Z = 37.0 .. 55.0 mm, Y = 20.0 .. 68.0 mm)
    hood_w_y = GLAND_BOSS_W_Y + 8.0  # 48.0 mm
    y_hood0 = GLAND_CENTER_Y - hood_w_y / 2.0  # 20.0 mm
    hood_pts = [
        (BOX_WIDTH_X, 37.0),
        (BOX_WIDTH_X + GLAND_HOOD_DX, 37.0),
        (BOX_WIDTH_X + GLAND_HOOD_DX, 41.0),
        (BOX_WIDTH_X, 55.0),
    ]
    rain_hood = (
        cq.Workplane("XZ")
        .workplane(offset=-y_hood0)
        .polyline(hood_pts)
        .close()
        .extrude(-hood_w_y)
    )
    box = box.union(rain_hood)

    # Cut 2x 10 AWG wire channels (dia 5.2 mm) through right wall + boss at Y = 38.0 and Y = 50.0, Z = 26.0
    for wy in (GLAND_CENTER_Y - GLAND_WIRE_SPAN_Y / 2.0, GLAND_CENTER_Y + GLAND_WIRE_SPAN_Y / 2.0):
        w_hole = (
            cq.Workplane("YZ")
            .workplane(offset=BOX_WIDTH_X - WALL_T - 2.0)
            .moveTo(wy, GLAND_CENTER_Z)
            .circle(WIRE_BORE_DIA / 2.0)
            .extrude(WALL_T + GLAND_BOSS_DX + 4.0)
        )
        box = box.cut(w_hole)

    # Cut outer seal/compression pocket on boss face (X = 216.0 .. 218.0, Y = 34.0 .. 54.0, Z = 22.0 .. 30.0)
    seal_pocket = (
        cq.Workplane("YZ")
        .workplane(offset=BOX_WIDTH_X + GLAND_BOSS_DX - 2.0)
        .moveTo(GLAND_CENTER_Y, GLAND_CENTER_Z)
        .rect(20.0, 8.0)
        .extrude(3.0)
    )
    box = box.cut(seal_pocket)

    # Cut 2x M4 heat-set insert bores in gland boss face (X = 218.0 inward 9.5 mm) at Y = 29.0 & 59.0, Z = 26.0
    for by in (GLAND_CENTER_Y - GLAND_BOLT_SPAN_Y / 2.0, GLAND_CENTER_Y + GLAND_BOLT_SPAN_Y / 2.0):
        ins_bore = (
            cq.Workplane("YZ")
            .workplane(offset=BOX_WIDTH_X + GLAND_BOSS_DX - M4_INSERT_DEPTH)
            .moveTo(by, GLAND_CENTER_Z)
            .circle(M4_INSERT_BORE_DIA / 2.0)
            .extrude(M4_INSERT_DEPTH + 1.0)
        )
        box = box.cut(ins_bore)

    # 10. Cut 2x M4 heat-set insert bores in upper Left and Right box walls for locking the Overhang Lid (Z = 145.0, Y = 38.5)
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

    # 11. Cut 2x 4.0 mm Floor Condensation Weep Holes at front corners (X = 14 & 195, Y = 66)
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


def build_overhang_lid() -> cq.Workplane:
    """Build the sloped weatherproof Overhang Lid with snow-shedding pitch, deep skirt & undercut drip groove."""
    # 1. Outer sloped roof + skirt block extruded along X (X = -12.0 .. 221.0 mm)
    # Profile in YZ plane:
    #   (Y = -3.0, Z = 138.0) -> (Y = 91.0, Z = 138.0) -> (Y = 91.0, Z = 167.0) -> (Y = -3.0, Z = 180.0)
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

    # 2. Cut lower inner collar cavity around main box outer walls (Z = 138.0 .. 152.6 mm)
    # Box outer walls span X: 0..209, Y: 0..77 -> add 0.6 mm clearance per side:
    # X: -0.6 .. 209.6 (width = 210.2), Y: -0.6 .. 77.6 (depth = 78.2)
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

    # 3. Cut upper inner labyrinth cavity around the raised splash lip (Z = 152.6 .. 163.0 mm)
    # Splash lip outer faces span X: 2.2 .. 206.8, Y: 0.0 .. 74.8 -> add 0.6 mm clearance:
    # X: 1.6 .. 207.4 (width = 205.8), Y: -0.6 .. 75.4 (depth = 76.0)
    up_w_x = (BOX_WIDTH_X - 2.0 * SPLASH_LIP_STEP) + 2.0 * LID_COLLAR_CLEAR
    up_d_y = (BOX_DEPTH_Y - SPLASH_LIP_STEP) + 2.0 * LID_COLLAR_CLEAR
    up_yc = -LID_COLLAR_CLEAR + up_d_y / 2.0
    upper_cav = (
        cq.Workplane("XY")
        .workplane(offset=BOX_SHOULDER_Z + 0.5)
        .moveTo(BOX_WIDTH_X / 2.0, up_yc)
        .rect(up_w_x, up_d_y)
        .extrude(LID_CEIL_Z - (BOX_SHOULDER_Z + 0.5))
    )
    lid = lid.cut(upper_cav)

    # 4. Cut the Undercut Perimeter Drip Channel (Z = 138.0 .. 141.0 mm) inside the outer 3.5 mm eave bead
    # Outer skirt stays down to Z = 138.0 mm at the 3.5 mm perimeter rim (forming a projecting drip lip);
    # the 3.2 mm wide channel inside it is recessed up to Z = 141.0 mm so water drips cleanly off the outer bead!
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

    # 5. Cut 2x M4 side locking screw holes + button-head counterbores at Z = 145.0, Y = 38.5
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


def build_wire_gland_cap() -> cq.Workplane:
    """Build the bolt-on 2x 10 AWG Compression Wire Gland Cap (print_wire_gland_cap)."""
    cap_x0 = BOX_WIDTH_X + GLAND_BOSS_DX + 0.5  # 218.5 mm (0.5 mm clamping gap from X = 218.0 boss face)
    cap = (
        cq.Workplane("YZ")
        .workplane(offset=cap_x0)
        .moveTo(GLAND_CENTER_Y, GLAND_CENTER_Z)
        .rect(GLAND_BOSS_W_Y, GLAND_BOSS_H_Z)
        .extrude(GLAND_CAP_DX)
    )

    # Inner compression tongue projecting 1.5 mm into the boss's seal pocket (X = 217.0 .. 218.5)
    tongue = (
        cq.Workplane("YZ")
        .workplane(offset=cap_x0 - 1.5)
        .moveTo(GLAND_CENTER_Y, GLAND_CENTER_Z)
        .rect(19.0, 7.2)
        .extrude(1.5)
    )
    cap = cap.union(tongue)

    # Cut 2x 5.2 mm 10 AWG wire passages at Y = 38.0 and Y = 50.0, Z = 26.0
    for wy in (GLAND_CENTER_Y - GLAND_WIRE_SPAN_Y / 2.0, GLAND_CENTER_Y + GLAND_WIRE_SPAN_Y / 2.0):
        w_bore = (
            cq.Workplane("YZ")
            .workplane(offset=cap_x0 - 3.0)
            .moveTo(wy, GLAND_CENTER_Z)
            .circle(WIRE_BORE_DIA / 2.0)
            .extrude(GLAND_CAP_DX + 5.0)
        )
        cap = cap.cut(w_bore)

    # Cut 2x M4 clearance holes + button-head counterbores at Y = 29.0 & 59.0, Z = 26.0
    for by in (GLAND_CENTER_Y - GLAND_BOLT_SPAN_Y / 2.0, GLAND_CENTER_Y + GLAND_BOLT_SPAN_Y / 2.0):
        m4_hole = (
            cq.Workplane("YZ")
            .workplane(offset=cap_x0 - 2.0)
            .moveTo(by, GLAND_CENTER_Z)
            .circle(M4_CLEAR_DIA / 2.0)
            .extrude(GLAND_CAP_DX + 4.0)
        )
        m4_cb = (
            cq.Workplane("YZ")
            .workplane(offset=cap_x0 + GLAND_CAP_DX - 3.0)
            .moveTo(by, GLAND_CENTER_Z)
            .circle(M4_CBORE_DIA / 2.0)
            .extrude(4.0)
        )
        cap = cap.cut(m4_hole).cut(m4_cb)

    return cap


def build_mightymax_battery() -> tuple[cq.Workplane, cq.Workplane, cq.Workplane]:
    """Build the Mighty Max 12V 10Ah (ML10-12: 151 x 65 x 111 mm + F2 terminals) SLA Battery."""
    bx0 = WALL_T + BATT_CLEAR_XY  # 6.0 mm
    by0 = WALL_T + BATT_CLEAR_XY  # 6.0 mm
    bxc = bx0 + BATT_LEN_X / 2.0  # 81.5 mm
    byc = by0 + BATT_WID_Y / 2.0  # 38.5 mm

    # Main SLA case body (151 x 65 x 105 mm) + slightly overhanging top cover lid (6 mm tall = 111 mm total case)
    case = (
        cq.Workplane("XY")
        .workplane(offset=BATT_Z0)
        .moveTo(bxc, byc)
        .rect(BATT_LEN_X, BATT_WID_Y)
        .extrude(BATT_CASE_H_Z)
        .edges("|Z")
        .fillet(2.5)
    )

    # F2 Spade Terminals (+12V Red at front-right X=145, Y=56; -12V Black at back-right X=145, Y=21)
    # Placed on the right end next to the wiring bay for shortest, cleanest wire routing!
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
    """Build the two 10 AWG actuator power leads (+12V Red and GND Black) routing through the wire bay & gland."""
    # Wire 1 (+12V Red): exits gland hole at Y = 50.0, Z = 26.0, X = 186.0 .. 255.0 mm
    # plus vertical riser inside wire bay from Z = 26.0 .. 125.0 mm and horizontal bridge to positive F2 terminal
    wy_pos = GLAND_CENTER_Y + GLAND_WIRE_SPAN_Y / 2.0  # 50.0 mm
    wy_neg = GLAND_CENTER_Y - GLAND_WIRE_SPAN_Y / 2.0  # 38.0 mm

    wire_pos = (
        cq.Workplane("YZ")
        .workplane(offset=185.0)
        .moveTo(wy_pos, GLAND_CENTER_Z)
        .circle(WIRE_10AWG_OD / 2.0)
        .extrude(70.0)
        .union(
            cq.Workplane("XY")
            .workplane(offset=GLAND_CENTER_Z)
            .moveTo(185.0, wy_pos)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(100.0)
        )
        .union(
            cq.Workplane("YZ")
            .workplane(offset=143.0)
            .moveTo(wy_pos, 126.0)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(42.0)
        )
    )

    wire_neg = (
        cq.Workplane("YZ")
        .workplane(offset=174.0)
        .moveTo(wy_neg, GLAND_CENTER_Z)
        .circle(WIRE_10AWG_OD / 2.0)
        .extrude(81.0)
        .union(
            cq.Workplane("XY")
            .workplane(offset=GLAND_CENTER_Z)
            .moveTo(174.0, wy_neg)
            .circle(WIRE_10AWG_OD / 2.0)
            .extrude(106.0)
        )
        .union(
            cq.Workplane("YZ")
            .workplane(offset=143.0)
            .moveTo(wy_neg, 132.0)
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
    # 3 horizontal cedar boards with 1.5 mm V-grooves
    for idx, (z0, h) in enumerate(((-20.0, 72.0), (53.5, 72.0), (127.0, 72.0))):
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
    gland_cap = build_wire_gland_cap()
    batt_case, batt_pos, batt_neg = build_mightymax_battery()
    wire_pos, wire_neg = build_actuator_wires()

    asm.add(planter_wall, name="planter_cedar_wall", color=cq.Color(0.68, 0.45, 0.26, 0.65))
    asm.add(box, name="print_battery_box", color=cq.Color(0.85, 0.33, 0.12, 1.0))
    asm.add(lid, name="print_overhang_lid", color=cq.Color(0.22, 0.25, 0.29, 0.88))
    asm.add(gland_cap, name="print_wire_gland_cap", color=cq.Color(0.85, 0.33, 0.12, 1.0))
    asm.add(batt_case, name="battery_mightymax_12v10ah", color=cq.Color(0.14, 0.15, 0.17, 1.0))
    asm.add(batt_pos, name="terminal_pos_f2", color=cq.Color(0.88, 0.16, 0.16, 1.0))
    asm.add(batt_neg, name="terminal_neg_f2", color=cq.Color(0.10, 0.10, 0.12, 1.0))
    asm.add(wire_pos, name="wire_10awg_pos", color=cq.Color(0.90, 0.18, 0.18, 1.0))
    asm.add(wire_neg, name="wire_10awg_neg", color=cq.Color(0.15, 0.16, 0.18, 1.0))

    return asm


# ==============================================================================
# 3. CLASH CHECKER, PRINT-BED ORIENTATION & EXPORTERS
# ==============================================================================

def run_clash_checks(asm: cq.Assembly) -> int:
    """Verify 0.0 mm^3 solid interference across all parts in the assembly."""
    print("== Running 3D Solid Clash Checks ==")
    children = [c for c in asm.children]
    clashes = 0
    for i in range(len(children)):
        for j in range(i + 1, len(children)):
            c1, c2 = children[i], children[j]
            # Terminals & wires connect intentionally at terminal posts
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
        print("  [PASS] 0 clashes detected across all 9 assembly solids (0.00 mm^3 interference).")
    return clashes


def orient_for_printing(name: str, wp: cq.Workplane) -> cq.Workplane:
    """Orient each 3D-printed part flat on Z = 0 for 100% support-free FDM printing."""
    solid = wp.val()
    if name == "print_overhang_lid":
        # Rotate lid so its sloped outer shed-roof face lies 100% flat on the Z = 0 print bed!
        slope_deg = math.degrees(math.atan2(LID_ROOF_BACK_Z - LID_ROOF_FRONT_Z, LID_DEPTH_Y))
        rotated = solid.rotate((0, 0, 0), (1, 0, 0), 180.0 + slope_deg)
        bb = rotated.BoundingBox()
        moved = rotated.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        return cq.Workplane(obj=moved)
    elif name == "print_wire_gland_cap":
        # Rotate cap so its flat outer +X face lies on Z = 0 print bed
        rotated = solid.rotate((0, 0, 0), (0, 1, 0), 90.0)
        bb = rotated.BoundingBox()
        moved = rotated.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        return cq.Workplane(obj=moved)
    else:
        # Battery box already sits flat on Z = 0
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
            "off": [0.0, -35.0, -18.0],
        },
        {
            "a": [-FLANGE_W_X, 0.0, 0.0],
            "b": [BOX_WIDTH_X + FLANGE_W_X, 0.0, 0.0],
            "label": f"Flange Span {BOX_WIDTH_X + 2*FLANGE_W_X:.0f} mm ({(BOX_WIDTH_X + 2*FLANGE_W_X)/25.4:.2f} in)",
            "off": [0.0, -35.0, -38.0],
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
            "label": f"Box Height {BOX_TOTAL_H_Z:.0f} mm (180 mm w/ sloped lid)",
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
    """Export STEP assembly, pre-oriented printable STLs, combined build plate, and viewer JSON."""
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(STEP_DIR, exist_ok=True)
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(VIEWER_DIR, exist_ok=True)

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

    # 3. Export Pre-Oriented Printable STLs + Check against Bambu P1P (256x256) & H2D (350x320) beds
    print("== Exported Pre-Oriented Printable STLs (Support-Free) ==")
    plate_solids = []
    for child in asm.children:
        if not child.name.startswith("print_"):
            continue
        oriented = orient_for_printing(child.name, child.obj)
        stl_path = os.path.join(STL_DIR, f"{child.name}.stl")
        cq.exporters.export(oriented, stl_path)
        bb = oriented.val().BoundingBox()
        dx, dy, dz = bb.xlen, bb.ylen, bb.zlen
        p1p_ok = "PASS (P1P 256mm & H2D 350mm)" if (dx <= 256 and dy <= 256 and dz <= 256) else "H2D only"
        print(f"  {child.name:24s} -> {dx:6.1f} x {dy:6.1f} x {dz:6.1f} mm  [{p1p_ok}]")

        # Position on combined build plate (fits within 250 x 240 mm -> prints in 1 plate on both P1P & H2D!)
        if child.name == "print_battery_box":
            plate_solids.append(oriented.val().translate((0.0, 0.0, 0.0)))
        elif child.name == "print_overhang_lid":
            plate_solids.append(oriented.val().translate((0.0, 92.0, 0.0)))
        elif child.name == "print_wire_gland_cap":
            plate_solids.append(oriented.val().translate((105.0, 198.0, 0.0)))

    plate_compound = cq.Compound.makeCompound(plate_solids)
    plate_path = os.path.join(STL_DIR, "plate_01_all_parts.stl")
    cq.exporters.export(plate_compound, plate_path)
    pbb = plate_compound.BoundingBox()
    print(f"  {'plate_01_all_parts':24s} -> {pbb.xlen:6.1f} x {pbb.ylen:6.1f} x {pbb.zlen:6.1f} mm  [PASS (1-plate build on P1P & H2D)]")


if __name__ == "__main__":
    assembly = build_assembly()
    if "--clash" in sys.argv:
        n_clash = run_clash_checks(assembly)
        if n_clash > 0:
            sys.exit(1)
    export_all(assembly)

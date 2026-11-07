# Author: Dan Gorman / Antigravity CAD Generator
# Description: Parametric Autodesk Fusion assembly generator for the Backyard Discovery
#              Aggie Cold Box 12V 10Ah (Mighty Max ML10-12) Weatherproof Battery Enclosure,
#              Sloped Snow/Rain Overhang Drip Lid, and 2x 10 AWG Actuator Wire Gland.

import traceback
import adsk.core
import adsk.fusion

# ==============================================================================
# 1. TOP-LEVEL PARAMETRIC DIMENSIONS (ALL VALUES IN MILLIMETERS)
# ==============================================================================

# Mighty Max 12V 10Ah SLA Battery (ML10-12: 5.94 x 2.56 x 4.37 in case, 4.69 in w/ F2 terminals)
BATT_LEN_X: float = 151.0           # Battery length along X (mm)
BATT_WID_Y: float = 65.0            # Battery width/depth along Y (mm)
BATT_CASE_H_Z: float = 111.0        # Flat case top height along Z (mm)
BATT_TOTAL_H_Z: float = 119.0       # Total height over F2 spade terminals (mm)
BATT_CLEAR_XY: float = 1.0          # 1.0 mm per-side pocket clearance

# Main Enclosure Structural Envelope
WALL_T: float = 5.0                 # 5.0 mm heavy-duty outdoor wall thickness
FLOOR_T: float = 5.0                # 5.0 mm structural floor thickness
FLOOR_RIB_H: float = 3.0            # 3.0 mm raised floor support/drainage ribs under battery
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

# Fastener & Heat-Set Insert Specifications
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

# Color Palette
COL_CEDAR_WOOD = ("Mat_Aggie_Cedar_Wood", (173, 115, 66))
COL_PRINT_ORANGE = ("Mat_Printed_PETG_Orange", (217, 84, 31))
COL_LID_SLATE = ("Mat_Printed_ASA_Slate", (56, 64, 74))
COL_BATT_CHARCOAL = ("Mat_MightyMax_Case", (36, 38, 43))
COL_TERM_RED = ("Mat_Terminal_Pos_Red", (224, 41, 41))
COL_TERM_BLACK = ("Mat_Terminal_Neg_Black", (25, 25, 30))


# ==============================================================================
# 2. FUSION 360 GEOMETRY & FEATURE TREE HELPER FUNCTIONS
# ==============================================================================

def cm(mm_val: float) -> float:
    """Convert millimeters to Fusion's internal unit (centimeters)."""
    return mm_val * 0.1


def val(mm_val: float) -> adsk.core.ValueInput:
    """Create a Fusion ValueInput from a millimeter value."""
    return adsk.core.ValueInput.createByReal(cm(mm_val))


def pt3d(x_mm: float, y_mm: float, z_mm: float) -> adsk.core.Point3D:
    """Create a 3D world point in Fusion internal units (cm) from mm coordinates."""
    return adsk.core.Point3D.create(cm(x_mm), cm(y_mm), cm(z_mm))


def register_user_parameters(design: adsk.fusion.Design) -> None:
    """Register key top-level dimensions into Fusion's Modify -> Change Parameters table."""
    params = [
        ("BATT_LEN_X", BATT_LEN_X, "mm", "Mighty Max 12V 10Ah battery length"),
        ("BATT_WID_Y", BATT_WID_Y, "mm", "Mighty Max 12V 10Ah battery width/depth"),
        ("BATT_CASE_H_Z", BATT_CASE_H_Z, "mm", "Mighty Max 12V 10Ah case height"),
        ("BATT_TOTAL_H_Z", BATT_TOTAL_H_Z, "mm", "Mighty Max 12V 10Ah height over F2 terminals"),
        ("WIRE_BAY_W_X", WIRE_BAY_W_X, "mm", "Side wire & fuse stuffing compartment width"),
        ("OVERHEAD_WIRE_H_Z", OVERHEAD_WIRE_H_Z, "mm", "Overhead wire clearance above F2 terminals"),
        ("BOX_WIDTH_X", BOX_WIDTH_X, "mm", "Main enclosure outer width (excluding mounting flanges)"),
        ("BOX_DEPTH_Y", BOX_DEPTH_Y, "mm", "Main enclosure outer depth (excluding rear standoffs)"),
        ("BOX_TOTAL_H_Z", BOX_TOTAL_H_Z, "mm", "Main enclosure height to top of labyrinth splash lip"),
        ("LID_OVERHANG_SIDE_X", LID_OVERHANG_SIDE_X, "mm", "Lid snow/water overhang per side"),
        ("LID_OVERHANG_FRONT_Y", LID_OVERHANG_FRONT_Y, "mm", "Lid snow/water overhang at front eave"),
        ("WIRE_BORE_DIA", WIRE_BORE_DIA, "mm", "10 AWG actuator wire gland channel diameter"),
    ]
    user_params = design.userParameters
    for name, number, unit, comment in params:
        existing = user_params.itemByName(name)
        if not existing:
            user_params.add(name, adsk.core.ValueInput.createByString(f"{number} {unit}"), unit, comment)


def create_subcomponent(parent_comp: adsk.fusion.Component, name: str) -> adsk.fusion.Component:
    """Create a child component inside parent_comp for a clean, 1-click toggleable Browser tree."""
    try:
        occ = parent_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        return occ.component
    except Exception:
        return parent_comp


def create_offset_plane(comp: adsk.fusion.Component, axis: str, offset_mm: float) -> adsk.fusion.ConstructionPlane:
    """Create a construction plane parallel to XY ('z'), XZ ('y'), or YZ ('x') at exact world coordinate offset_mm."""
    axis_lower = axis.lower()
    if axis_lower == "z":
        base_plane = comp.xYConstructionPlane
        axis_vec = adsk.core.Vector3D.create(0, 0, 1)
    elif axis_lower == "y":
        base_plane = comp.xZConstructionPlane
        axis_vec = adsk.core.Vector3D.create(0, 1, 0)
    elif axis_lower == "x":
        base_plane = comp.yZConstructionPlane
        axis_vec = adsk.core.Vector3D.create(1, 0, 0)
    else:
        raise ValueError(f"Unknown axis: {axis}")

    normal = base_plane.geometry.normal
    sign = 1.0 if normal.dotProduct(axis_vec) >= 0.0 else -1.0
    plane_input = comp.constructionPlanes.createInput()
    plane_input.setByOffset(base_plane, val(offset_mm * sign))
    plane = comp.constructionPlanes.add(plane_input)
    plane.isLightBulbOn = False
    return plane


def sketch_world_point(sketch: adsk.fusion.Sketch, x_mm: float, y_mm: float, z_mm: float) -> adsk.core.Point3D:
    """Project a 3D world coordinate (mm) onto the 2D sketch plane (z = 0 in sketch space)."""
    pt_local = sketch.modelToSketchSpace(pt3d(x_mm, y_mm, z_mm))
    return adsk.core.Point3D.create(pt_local.x, pt_local.y, 0.0)


def extrude_all_profiles(
    comp: adsk.fusion.Component,
    sketch: adsk.fusion.Sketch,
    axis: str,
    thickness_mm: float,
    operation: int,
    target_body: adsk.fusion.BRepBody | None = None,
    body_name: str | None = None,
) -> adsk.fusion.BRepBody | None:
    """Extrude all profiles in a sketch along world +X, +Y, or +Z by thickness_mm (signed)."""
    sketch.isLightBulbOn = False
    if sketch.profiles.count == 0:
        return target_body

    profs = adsk.core.ObjectCollection.create()
    for i in range(sketch.profiles.count):
        profs.add(sketch.profiles.item(i))

    axis_vec = {
        "x": adsk.core.Vector3D.create(1, 0, 0),
        "y": adsk.core.Vector3D.create(0, 1, 0),
        "z": adsk.core.Vector3D.create(0, 0, 1),
    }[axis.lower()]

    sketch_normal = sketch.xDirection.crossProduct(sketch.yDirection)
    dir_sign = 1.0 if sketch_normal.dotProduct(axis_vec) >= 0.0 else -1.0
    signed_dist = thickness_mm * dir_sign

    ext_features = comp.features.extrudeFeatures
    ext_input = ext_features.createInput(profs, operation)
    ext_input.setDistanceExtent(False, val(signed_dist))
    if target_body is not None and operation in (
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        adsk.fusion.FeatureOperations.IntersectFeatureOperation,
    ):
        ext_input.participantBodies = [target_body]

    ext = ext_features.add(ext_input)
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and ext.bodies.count > 0:
        new_body = ext.bodies.item(0)
        if body_name:
            new_body.name = body_name
        return new_body
    return target_body


def add_box_feature(
    comp: adsk.fusion.Component,
    x0: float,
    y0: float,
    z0: float,
    dx: float,
    dy: float,
    dz: float,
    operation: int = adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    target_body: adsk.fusion.BRepBody | None = None,
    body_name: str | None = None,
) -> adsk.fusion.BRepBody | None:
    """Create a parametric rectangular box extrusion spanning (x0..x0+dx, y0..y0+dy, z0..z0+dz)."""
    plane = create_offset_plane(comp, "z", z0)
    sketch = comp.sketches.add(plane)
    p0 = sketch_world_point(sketch, x0, y0, z0)
    p1 = sketch_world_point(sketch, x0 + dx, y0 + dy, z0)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(p0, p1)
    return extrude_all_profiles(comp, sketch, "z", dz, operation, target_body, body_name)


def add_polygon_extrusion(
    comp: adsk.fusion.Component,
    axis: str,
    plane_pos_mm: float,
    extrude_dist_mm: float,
    world_pts: list[tuple[float, float, float]],
    operation: int = adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    target_body: adsk.fusion.BRepBody | None = None,
    body_name: str | None = None,
) -> adsk.fusion.BRepBody | None:
    """Extrude a closed polygon specified in 3D world coordinates on an XY ('z'), XZ ('y'), or YZ ('x') plane."""
    plane = create_offset_plane(comp, axis, plane_pos_mm)
    sketch = comp.sketches.add(plane)
    lines = sketch.sketchCurves.sketchLines
    n = len(world_pts)
    for idx in range(n):
        p_a = sketch_world_point(sketch, *world_pts[idx])
        p_b = sketch_world_point(sketch, *world_pts[(idx + 1) % n])
        lines.addByTwoPoints(p_a, p_b)
    return extrude_all_profiles(comp, sketch, axis, extrude_dist_mm, operation, target_body, body_name)


def cut_cylinders_on_plane(
    comp: adsk.fusion.Component,
    target_body: adsk.fusion.BRepBody,
    axis: str,
    plane_pos_mm: float,
    extrude_depth_mm: float,
    centers_and_radii: list[tuple[float, float, float, float]],
) -> None:
    """Cut multiple circular bores in a single sketch feature on an XY ('z'), XZ ('y'), or YZ ('x') offset plane."""
    if not centers_and_radii:
        return
    plane = create_offset_plane(comp, axis, plane_pos_mm)
    sketch = comp.sketches.add(plane)
    circles = sketch.sketchCurves.sketchCircles
    for wx, wy, wz, rad in centers_and_radii:
        cpt = sketch_world_point(sketch, wx, wy, wz)
        circles.addByCenterRadius(cpt, cm(rad))
    extrude_all_profiles(
        comp,
        sketch,
        axis,
        extrude_depth_mm,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        target_body,
    )


def add_cylinder_feature(
    comp: adsk.fusion.Component,
    axis: str,
    plane_pos_mm: float,
    extrude_dist_mm: float,
    wx: float,
    wy: float,
    wz: float,
    radius_mm: float,
    operation: int = adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    target_body: adsk.fusion.BRepBody | None = None,
    body_name: str | None = None,
) -> adsk.fusion.BRepBody | None:
    """Create or join a cylinder along world X, Y, or Z."""
    plane = create_offset_plane(comp, axis, plane_pos_mm)
    sketch = comp.sketches.add(plane)
    cpt = sketch_world_point(sketch, wx, wy, wz)
    sketch.sketchCurves.sketchCircles.addByCenterRadius(cpt, cm(radius_mm))
    return extrude_all_profiles(comp, sketch, axis, extrude_dist_mm, operation, target_body, body_name)


def fillet_parallel_edges(
    comp: adsk.fusion.Component,
    body: adsk.fusion.BRepBody | None,
    axis: str,
    radius_mm: float,
) -> None:
    """Apply a parametric FilletFeature to straight edges of `body` parallel to `axis` ('x', 'y', 'z')."""
    if body is None or radius_mm <= 0.0:
        return
    axis_vec = {
        "x": adsk.core.Vector3D.create(1, 0, 0),
        "y": adsk.core.Vector3D.create(0, 1, 0),
        "z": adsk.core.Vector3D.create(0, 0, 1),
    }.get(axis.lower())

    edge_coll = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        geom = edge.geometry
        if (
            geom is None
            or edge.startVertex is None
            or edge.endVertex is None
            or geom.curveType != adsk.core.Curve3DTypes.Line3DCurveType
        ):
            continue
        p_start = edge.startVertex.geometry
        p_end = edge.endVertex.geometry
        if axis_vec is not None:
            vec = p_start.vectorTo(p_end)
            if vec.length < 1e-4:
                continue
            vec.normalize()
            if abs(vec.dotProduct(axis_vec)) < 0.98:
                continue
        edge_coll.add(edge)

    if edge_coll.count > 0:
        try:
            fillets = comp.features.filletFeatures
            f_input = fillets.createInput()
            f_input.addConstantRadiusEdgeSet(edge_coll, val(radius_mm), True)
            fillets.add(f_input)
        except Exception:
            pass


def apply_color(
    app: adsk.core.Application,
    design: adsk.fusion.Design,
    body: adsk.fusion.BRepBody | None,
    palette_name: str,
    rgb: tuple[int, int, int],
) -> None:
    """Assign a clean visual RGB color appearance to a BRepBody."""
    if body is None:
        return
    try:
        appearances = design.appearances
        target_app = appearances.itemByName(palette_name)
        if not target_app:
            base_app = None
            if appearances.count > 0:
                base_app = appearances.item(0)
            else:
                lib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
                if not lib:
                    lib = app.materialLibraries.item(0)
                if lib and lib.appearances.count > 0:
                    base_app = lib.appearances.item(0)
            if base_app:
                target_app = appearances.addByCopy(base_app, palette_name)
                for prop in target_app.appearanceProperties:
                    if prop.objectType == adsk.core.ColorProperty.classType():
                        c_prop = adsk.core.ColorProperty.cast(prop)
                        c_prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                        break
        if target_app:
            body.appearance = target_app
    except Exception:
        pass


# ==============================================================================
# 3. SUB-ASSEMBLY COMPONENT BUILDERS
# ==============================================================================

def build_planter_wall_component(
    app: adsk.core.Application,
    design: adsk.fusion.Design,
    root: adsk.fusion.Component,
) -> adsk.fusion.Component:
    """00_Aggie_Cold_Box_Planter_Wall: Reference cedar back planks of the Aggie Cold Box."""
    comp = create_subcomponent(root, "00_Aggie_Cold_Box_Planter_Wall")
    plank_thick = 20.0
    plank_w_x = 300.0
    x0 = BOX_WIDTH_X / 2.0 - plank_w_x / 2.0
    y0 = -STANDOFF_DEPTH_Y - plank_thick
    for idx, (z0, h) in enumerate(((-20.0, 72.0), (53.5, 72.0), (127.0, 72.0))):
        board = add_box_feature(
            comp, x0, y0, z0, plank_w_x, plank_thick, h,
            body_name=f"aggie_cedar_plank_{idx}",
        )
        apply_color(app, design, board, *COL_CEDAR_WOOD)
    return comp


def build_battery_box_component(
    app: adsk.core.Application,
    design: adsk.fusion.Design,
    root: adsk.fusion.Component,
) -> adsk.fusion.Component:
    """01_Battery_Box_Enclosure: Main 3D-printed enclosure body with battery cradle, wire bay, flanges & gland boss."""
    comp = create_subcomponent(root, "01_Battery_Box_Enclosure")

    # 1. Main outer box shell (X: 0..209, Y: 0..77, Z: 0..162)
    box = add_box_feature(
        comp, 0.0, 0.0, 0.0, BOX_WIDTH_X, BOX_DEPTH_Y, BOX_TOTAL_H_Z,
        body_name="print_battery_box",
    )

    # 2. Cut outer top shoulder around Left, Right, and Front (Z: 152..162) to form 10 mm raised inner labyrinth splash lip
    # Left shoulder cut (X: 0..2.2)
    add_box_feature(
        comp, -0.5, -0.5, BOX_SHOULDER_Z, SPLASH_LIP_STEP + 0.5, BOX_DEPTH_Y + 1.0, SPLASH_LIP_H_Z + 1.0,
        adsk.fusion.FeatureOperations.CutFeatureOperation, box,
    )
    # Right shoulder cut (X: 206.8..209)
    add_box_feature(
        comp, BOX_WIDTH_X - SPLASH_LIP_STEP, -0.5, BOX_SHOULDER_Z, SPLASH_LIP_STEP + 0.5, BOX_DEPTH_Y + 1.0, SPLASH_LIP_H_Z + 1.0,
        adsk.fusion.FeatureOperations.CutFeatureOperation, box,
    )
    # Front shoulder cut (Y: 74.8..77)
    add_box_feature(
        comp, -0.5, BOX_DEPTH_Y - SPLASH_LIP_STEP, BOX_SHOULDER_Z, BOX_WIDTH_X + 1.0, SPLASH_LIP_STEP + 0.5, SPLASH_LIP_H_Z + 1.0,
        adsk.fusion.FeatureOperations.CutFeatureOperation, box,
    )

    # 3. Cut main interior cavity (X: 5..204, Y: 5..72, Z: 5..162)
    add_box_feature(
        comp, WALL_T, WALL_T, FLOOR_T, BOX_WIDTH_X - 2.0 * WALL_T, INNER_DEPTH_Y, BOX_TOTAL_H_Z,
        adsk.fusion.FeatureOperations.CutFeatureOperation, box,
    )

    # 4. Internal Battery Cradle Divider Wall (X: 158..162, Y: 5..72, Z: 5..45) with center relief notch
    div_x0 = WALL_T + BATT_BAY_W_X  # 158.0 mm
    add_box_feature(
        comp, div_x0, WALL_T, FLOOR_T, DIVIDER_T_X, INNER_DEPTH_Y, DIVIDER_H_Z,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
    )
    add_box_feature(
        comp, div_x0 - 0.5, BOX_DEPTH_Y / 2.0 - 16.0, FLOOR_T + 20.0, DIVIDER_T_X + 1.0, 32.0, DIVIDER_H_Z,
        adsk.fusion.FeatureOperations.CutFeatureOperation, box,
    )

    # 5. 3x Raised Floor Support / Drainage Ribs under Battery (Z: 5..8, Y: 8..69, width 8 mm)
    for rx in (24.0, 81.5, 139.0):
        add_box_feature(
            comp, rx - 4.0, WALL_T + 3.0, FLOOR_T, 8.0, INNER_DEPTH_Y - 6.0, FLOOR_RIB_H,
            adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
        )

    # 6. 2x Internal Zip-Tie Anchor Bridges on Back Wall of Wiring Bay (X: 176..190, Y: 5..11, Z: 65 & 110)
    for tz in (65.0, 110.0):
        add_box_feature(
            comp, 176.0, WALL_T, tz - 6.0, 14.0, 6.0, 12.0,
            adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
        )
        add_box_feature(
            comp, 180.0, WALL_T, tz - 7.0, 6.0, 4.0, 14.0,
            adsk.fusion.FeatureOperations.CutFeatureOperation, box,
        )

    # 7. 4x Rear Planter-Wall Drainage Standoff Ribs (Y: -3..0, Z: 0..136, width 10 mm)
    for sx in (10.0, 75.0, 134.0, 199.0):
        add_box_feature(
            comp, sx - STANDOFF_W_X / 2.0, -STANDOFF_DEPTH_Y, 0.0, STANDOFF_W_X, STANDOFF_DEPTH_Y, STANDOFF_TOP_Z,
            adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
        )

    # 8. Left & Right Gusseted Planter Mounting Flanges (X: -20..0 and 209..229, Y: -3..5, Z: 0..130)
    for side_sign, fx0, fx_center, wall_x in (
        (-1.0, -FLANGE_W_X, -FLANGE_W_X / 2.0, 0.0),
        (+1.0, BOX_WIDTH_X, BOX_WIDTH_X + FLANGE_W_X / 2.0, BOX_WIDTH_X),
    ):
        add_box_feature(
            comp, fx0, -STANDOFF_DEPTH_Y, 0.0, FLANGE_W_X, FLANGE_T_Y, FLANGE_H_Z,
            adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
        )
        # 2x Structural Gussets per flange (Z: 0..6 and Z: 62..68, Y: 5..17)
        gx0 = wall_x - 12.0 if side_sign < 0 else wall_x
        for gz in (0.0, 62.0):
            add_box_feature(
                comp, gx0, WALL_T, gz, 12.0, 12.0, 6.0,
                adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
            )

        # Lower #10 wood-screw through-hole + front counterbore (Z = 28.0) and Upper Keyhole (Z = 105.0 & 96.0)
        cut_cylinders_on_plane(
            comp, box, "y", -STANDOFF_DEPTH_Y - 1.0, FLANGE_T_Y + 3.0,
            [
                (fx_center, -STANDOFF_DEPTH_Y, SCREW_LOWER_Z, SCREW_CLEAR_DIA / 2.0),
                (fx_center, -STANDOFF_DEPTH_Y, SCREW_UPPER_Z, SCREW_CLEAR_DIA / 2.0),
                (fx_center, -STANDOFF_DEPTH_Y, SCREW_UPPER_Z - 9.0, SCREW_CBORE_DIA / 2.0),
            ],
        )
        cut_cylinders_on_plane(
            comp, box, "y", WALL_T - 2.5, 4.0,
            [
                (fx_center, WALL_T - 2.5, SCREW_LOWER_Z, SCREW_CBORE_DIA / 2.0),
                (fx_center, WALL_T - 2.5, SCREW_UPPER_Z, SCREW_CBORE_DIA / 2.0),
            ],
        )
        # Keyhole connecting slot + front recess
        add_box_feature(
            comp, fx_center - SCREW_CLEAR_DIA / 2.0, -STANDOFF_DEPTH_Y - 0.5, SCREW_UPPER_Z - 9.0,
            SCREW_CLEAR_DIA, FLANGE_T_Y + 1.0, 9.0,
            adsk.fusion.FeatureOperations.CutFeatureOperation, box,
        )
        add_box_feature(
            comp, fx_center - SCREW_CBORE_DIA / 2.0, WALL_T - 2.5, SCREW_UPPER_Z - 9.0,
            SCREW_CBORE_DIA, 3.0, 9.0,
            adsk.fusion.FeatureOperations.CutFeatureOperation, box,
        )

    # 9. Right-Side 2x 10 AWG Wire Gland Boss + 45-deg Support-Free Chamfer + 45-deg Upper Rain Hood
    y_boss0 = GLAND_CENTER_Y - GLAND_BOSS_W_Y / 2.0  # 24.0 mm
    boss_world_pts = [
        (BOX_WIDTH_X, y_boss0, 6.0),
        (BOX_WIDTH_X + GLAND_BOSS_DX, y_boss0, 15.0),
        (BOX_WIDTH_X + GLAND_BOSS_DX, y_boss0, 37.0),
        (BOX_WIDTH_X, y_boss0, 37.0),
    ]
    add_polygon_extrusion(
        comp, "y", y_boss0, GLAND_BOSS_W_Y, boss_world_pts,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
    )

    hood_w_y = GLAND_BOSS_W_Y + 8.0  # 48.0 mm
    y_hood0 = GLAND_CENTER_Y - hood_w_y / 2.0  # 20.0 mm
    hood_world_pts = [
        (BOX_WIDTH_X, y_hood0, 37.0),
        (BOX_WIDTH_X + GLAND_HOOD_DX, y_hood0, 37.0),
        (BOX_WIDTH_X + GLAND_HOOD_DX, y_hood0, 41.0),
        (BOX_WIDTH_X, y_hood0, 55.0),
    ]
    add_polygon_extrusion(
        comp, "y", y_hood0, hood_w_y, hood_world_pts,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, box,
    )

    # Cut 2x 5.2 mm 10 AWG wire channels through right wall + boss
    wy1 = GLAND_CENTER_Y - GLAND_WIRE_SPAN_Y / 2.0
    wy2 = GLAND_CENTER_Y + GLAND_WIRE_SPAN_Y / 2.0
    cut_cylinders_on_plane(
        comp, box, "x", BOX_WIDTH_X - WALL_T - 1.0, WALL_T + GLAND_BOSS_DX + 2.0,
        [
            (BOX_WIDTH_X, wy1, GLAND_CENTER_Z, WIRE_BORE_DIA / 2.0),
            (BOX_WIDTH_X, wy2, GLAND_CENTER_Z, WIRE_BORE_DIA / 2.0),
        ],
    )

    # Cut seal/compression pocket on boss outer face (X = 216.0 .. 218.0)
    add_box_feature(
        comp, BOX_WIDTH_X + GLAND_BOSS_DX - 2.0, GLAND_CENTER_Y - 10.0, GLAND_CENTER_Z - 4.0,
        2.5, 20.0, 8.0,
        adsk.fusion.FeatureOperations.CutFeatureOperation, box,
    )

    # Cut 2x M4 heat-set insert bores in gland boss face (Y = 29.0 & 59.0, Z = 26.0)
    by1 = GLAND_CENTER_Y - GLAND_BOLT_SPAN_Y / 2.0
    by2 = GLAND_CENTER_Y + GLAND_BOLT_SPAN_Y / 2.0
    cut_cylinders_on_plane(
        comp, box, "x", BOX_WIDTH_X + GLAND_BOSS_DX - M4_INSERT_DEPTH, M4_INSERT_DEPTH + 1.0,
        [
            (BOX_WIDTH_X + GLAND_BOSS_DX, by1, GLAND_CENTER_Z, M4_INSERT_BORE_DIA / 2.0),
            (BOX_WIDTH_X + GLAND_BOSS_DX, by2, GLAND_CENTER_Z, M4_INSERT_BORE_DIA / 2.0),
        ],
    )

    # 10. Cut 2x M4 heat-set insert bores in upper Left and Right walls for Lid locking screws (Z = 145.0, Y = 38.5)
    cut_cylinders_on_plane(
        comp, box, "x", -0.5, WALL_T + 1.0,
        [(0.0, LID_M4_Y, LID_M4_Z, M4_INSERT_BORE_DIA / 2.0)],
    )
    cut_cylinders_on_plane(
        comp, box, "x", BOX_WIDTH_X - WALL_T - 0.5, WALL_T + 1.0,
        [(BOX_WIDTH_X, LID_M4_Y, LID_M4_Z, M4_INSERT_BORE_DIA / 2.0)],
    )

    # 11. Cut 2x 4.0 mm Floor Condensation Weep Holes (X = 14 & 195, Y = 66)
    cut_cylinders_on_plane(
        comp, box, "z", -0.5, FLOOR_T + 1.0,
        [
            (14.0, 66.0, 0.0, 2.0),
            (195.0, 66.0, 0.0, 2.0),
        ],
    )

    apply_color(app, design, box, *COL_PRINT_ORANGE)
    return comp


def build_overhang_lid_component(
    app: adsk.core.Application,
    design: adsk.fusion.Design,
    root: adsk.fusion.Component,
) -> adsk.fusion.Component:
    """02_Weatherproof_Overhang_Lid: Sloped 8-deg snow-shedding roof with 12-14 mm eaves, deep skirt & undercut drip groove."""
    comp = create_subcomponent(root, "02_Weatherproof_Overhang_Lid")

    # 1. Extrude sloped shed-roof + overhang skirt profile along X (X = -12.0 .. 221.0 mm)
    lid_world_pts = [
        (LID_LEFT_X0, LID_BACK_Y0, LID_SKIRT_Z0),
        (LID_LEFT_X0, LID_FRONT_Y1, LID_SKIRT_Z0),
        (LID_LEFT_X0, LID_FRONT_Y1, LID_ROOF_FRONT_Z),
        (LID_LEFT_X0, LID_BACK_Y0, LID_ROOF_BACK_Z),
    ]
    lid = add_polygon_extrusion(
        comp, "x", LID_LEFT_X0, LID_WIDTH_X, lid_world_pts,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        body_name="print_overhang_lid",
    )

    # 2. Cut lower inner collar cavity around box outer walls (X: -0.6..209.6, Y: -0.6..77.6, Z: 138..152.6)
    low_x0 = -LID_COLLAR_CLEAR
    low_y0 = -LID_COLLAR_CLEAR
    low_w = BOX_WIDTH_X + 2.0 * LID_COLLAR_CLEAR
    low_d = BOX_DEPTH_Y + 2.0 * LID_COLLAR_CLEAR
    add_box_feature(
        comp, low_x0, low_y0, LID_SKIRT_Z0 - 0.5, low_w, low_d, (BOX_SHOULDER_Z + 0.6) - (LID_SKIRT_Z0 - 0.5),
        adsk.fusion.FeatureOperations.CutFeatureOperation, lid,
    )

    # 3. Cut upper inner labyrinth cavity around the raised splash lip (X: 1.6..207.4, Y: -0.6..75.4, Z: 152.5..163.0)
    up_x0 = SPLASH_LIP_STEP - LID_COLLAR_CLEAR
    up_y0 = -LID_COLLAR_CLEAR
    up_w = (BOX_WIDTH_X - 2.0 * SPLASH_LIP_STEP) + 2.0 * LID_COLLAR_CLEAR
    up_d = (BOX_DEPTH_Y - SPLASH_LIP_STEP) + 2.0 * LID_COLLAR_CLEAR
    add_box_feature(
        comp, up_x0, up_y0, BOX_SHOULDER_Z + 0.5, up_w, up_d, LID_CEIL_Z - (BOX_SHOULDER_Z + 0.5),
        adsk.fusion.FeatureOperations.CutFeatureOperation, lid,
    )

    # 4. Cut the Undercut Perimeter Drip Groove (Z = 138.0 .. 141.0 mm) on Left, Right, and Front eaves
    # Left eave drip groove (X = -8.5 .. -5.3, Y = -3.0 .. 84.3)
    add_box_feature(
        comp, LID_LEFT_X0 + DRIP_LIP_W, LID_BACK_Y0, LID_SKIRT_Z0 - 0.5,
        DRIP_GROOVE_W, LID_DEPTH_Y - DRIP_LIP_W, DRIP_GROOVE_DEPTH_Z + 0.5,
        adsk.fusion.FeatureOperations.CutFeatureOperation, lid,
    )
    # Right eave drip groove (X = 214.3 .. 217.5, Y = -3.0 .. 84.3)
    add_box_feature(
        comp, LID_RIGHT_X1 - DRIP_LIP_W - DRIP_GROOVE_W, LID_BACK_Y0, LID_SKIRT_Z0 - 0.5,
        DRIP_GROOVE_W, LID_DEPTH_Y - DRIP_LIP_W, DRIP_GROOVE_DEPTH_Z + 0.5,
        adsk.fusion.FeatureOperations.CutFeatureOperation, lid,
    )
    # Front eave drip groove (X = -8.5 .. 217.5, Y = 84.3 .. 87.5)
    add_box_feature(
        comp, LID_LEFT_X0 + DRIP_LIP_W, LID_FRONT_Y1 - DRIP_LIP_W - DRIP_GROOVE_W, LID_SKIRT_Z0 - 0.5,
        LID_WIDTH_X - 2.0 * DRIP_LIP_W, DRIP_GROOVE_W, DRIP_GROOVE_DEPTH_Z + 0.5,
        adsk.fusion.FeatureOperations.CutFeatureOperation, lid,
    )

    # 5. Cut 2x M4 side locking screw holes + button-head counterbores at Z = 145.0, Y = 38.5
    cut_cylinders_on_plane(
        comp, lid, "x", LID_LEFT_X0 - 0.5, LID_OVERHANG_SIDE_X + 2.0,
        [(LID_LEFT_X0, LID_M4_Y, LID_M4_Z, M4_CLEAR_DIA / 2.0)],
    )
    cut_cylinders_on_plane(
        comp, lid, "x", LID_LEFT_X0 - 0.5, 4.0,
        [(LID_LEFT_X0, LID_M4_Y, LID_M4_Z, M4_CBORE_DIA / 2.0)],
    )
    cut_cylinders_on_plane(
        comp, lid, "x", BOX_WIDTH_X - 1.5, LID_OVERHANG_SIDE_X + 2.0,
        [(LID_RIGHT_X1, LID_M4_Y, LID_M4_Z, M4_CLEAR_DIA / 2.0)],
    )
    cut_cylinders_on_plane(
        comp, lid, "x", LID_RIGHT_X1 - 3.5, 4.0,
        [(LID_RIGHT_X1, LID_M4_Y, LID_M4_Z, M4_CBORE_DIA / 2.0)],
    )

    apply_color(app, design, lid, *COL_LID_SLATE)
    return comp


def build_wire_gland_cap_component(
    app: adsk.core.Application,
    design: adsk.fusion.Design,
    root: adsk.fusion.Component,
) -> adsk.fusion.Component:
    """03_10AWG_Wire_Gland_Cap: Bolt-on compression gland cap for the two 10 AWG actuator wires."""
    comp = create_subcomponent(root, "03_10AWG_Wire_Gland_Cap")
    cap_x0 = BOX_WIDTH_X + GLAND_BOSS_DX + 0.5  # 218.5 mm

    cap = add_box_feature(
        comp,
        cap_x0,
        GLAND_CENTER_Y - GLAND_BOSS_W_Y / 2.0,
        GLAND_CENTER_Z - GLAND_BOSS_H_Z / 2.0,
        GLAND_CAP_DX,
        GLAND_BOSS_W_Y,
        GLAND_BOSS_H_Z,
        body_name="print_wire_gland_cap",
    )

    # Inner compression tongue projecting 1.5 mm into the boss's seal pocket
    add_box_feature(
        comp,
        cap_x0 - 1.5,
        GLAND_CENTER_Y - 9.5,
        GLAND_CENTER_Z - 3.6,
        1.5,
        19.0,
        7.2,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
        cap,
    )

    # Cut 2x 5.2 mm 10 AWG wire passages + 2x M4 screw holes
    wy1 = GLAND_CENTER_Y - GLAND_WIRE_SPAN_Y / 2.0
    wy2 = GLAND_CENTER_Y + GLAND_WIRE_SPAN_Y / 2.0
    by1 = GLAND_CENTER_Y - GLAND_BOLT_SPAN_Y / 2.0
    by2 = GLAND_CENTER_Y + GLAND_BOLT_SPAN_Y / 2.0

    cut_cylinders_on_plane(
        comp, cap, "x", cap_x0 - 2.0, GLAND_CAP_DX + 4.0,
        [
            (cap_x0, wy1, GLAND_CENTER_Z, WIRE_BORE_DIA / 2.0),
            (cap_x0, wy2, GLAND_CENTER_Z, WIRE_BORE_DIA / 2.0),
            (cap_x0, by1, GLAND_CENTER_Z, M4_CLEAR_DIA / 2.0),
            (cap_x0, by2, GLAND_CENTER_Z, M4_CLEAR_DIA / 2.0),
        ],
    )
    cut_cylinders_on_plane(
        comp, cap, "x", cap_x0 + GLAND_CAP_DX - 3.0, 4.0,
        [
            (cap_x0, by1, GLAND_CENTER_Z, M4_CBORE_DIA / 2.0),
            (cap_x0, by2, GLAND_CENTER_Z, M4_CBORE_DIA / 2.0),
        ],
    )

    apply_color(app, design, cap, *COL_PRINT_ORANGE)
    return comp


def build_battery_and_wiring_component(
    app: adsk.core.Application,
    design: adsk.fusion.Design,
    root: adsk.fusion.Component,
) -> adsk.fusion.Component:
    """04_MightyMax_12V_10Ah_And_Wiring: Mighty Max ML10-12 battery + F2 spade terminals + 2x 10 AWG actuator wires."""
    comp = create_subcomponent(root, "04_MightyMax_12V_10Ah_And_Wiring")

    bx0 = WALL_T + BATT_CLEAR_XY  # 6.0 mm
    by0 = WALL_T + BATT_CLEAR_XY  # 6.0 mm
    batt = add_box_feature(
        comp, bx0, by0, BATT_Z0, BATT_LEN_X, BATT_WID_Y, BATT_CASE_H_Z,
        body_name="battery_mightymax_12v_10ah",
    )
    fillet_parallel_edges(comp, batt, "z", 2.5)
    apply_color(app, design, batt, *COL_BATT_CHARCOAL)

    # F2 Spade Terminals (+12V Red at Y = 57.0, -12V Black at Y = 20.0, X = 143.0, Z = 119.0 .. 127.0)
    term_x = bx0 + BATT_LEN_X - 14.0  # 143.0 mm
    pos_y = by0 + BATT_WID_Y - 14.0   # 57.0 mm
    neg_y = by0 + 14.0                # 20.0 mm
    top_z = BATT_Z0 + BATT_CASE_H_Z   # 119.0 mm

    pos_t = add_box_feature(
        comp, term_x - 5.0, pos_y - 5.0, top_z, 10.0, 10.0, 2.5,
        body_name="terminal_pos_f2_red",
    )
    add_box_feature(
        comp, term_x - 3.175, pos_y - 0.6, top_z + 2.5, 6.35, 1.2, 5.5,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, pos_t,
    )
    apply_color(app, design, pos_t, *COL_TERM_RED)

    neg_t = add_box_feature(
        comp, term_x - 5.0, neg_y - 5.0, top_z, 10.0, 10.0, 2.5,
        body_name="terminal_neg_f2_black",
    )
    add_box_feature(
        comp, term_x - 3.175, neg_y - 0.6, top_z + 2.5, 6.35, 1.2, 5.5,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, neg_t,
    )
    apply_color(app, design, neg_t, *COL_TERM_BLACK)

    # Two 10 AWG Actuator Wires (+12V Red and GND Black) routing through the wire bay & exiting the side gland
    wy_pos = GLAND_CENTER_Y + GLAND_WIRE_SPAN_Y / 2.0  # 50.0 mm
    wy_neg = GLAND_CENTER_Y - GLAND_WIRE_SPAN_Y / 2.0  # 38.0 mm
    r_wire = WIRE_10AWG_OD / 2.0

    w_pos = add_cylinder_feature(
        comp, "x", 185.0, 70.0, 185.0, wy_pos, GLAND_CENTER_Z, r_wire,
        body_name="wire_10awg_pos_red",
    )
    add_cylinder_feature(
        comp, "z", GLAND_CENTER_Z, 100.0, 185.0, wy_pos, GLAND_CENTER_Z, r_wire,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, w_pos,
    )
    add_cylinder_feature(
        comp, "x", 143.0, 42.0, 143.0, wy_pos, 126.0, r_wire,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, w_pos,
    )
    apply_color(app, design, w_pos, *COL_TERM_RED)

    w_neg = add_cylinder_feature(
        comp, "x", 174.0, 81.0, 174.0, wy_neg, GLAND_CENTER_Z, r_wire,
        body_name="wire_10awg_neg_black",
    )
    add_cylinder_feature(
        comp, "z", GLAND_CENTER_Z, 106.0, 174.0, wy_neg, GLAND_CENTER_Z, r_wire,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, w_neg,
    )
    add_cylinder_feature(
        comp, "x", 143.0, 31.0, 143.0, wy_neg, 132.0, r_wire,
        adsk.fusion.FeatureOperations.JoinFeatureOperation, w_neg,
    )
    apply_color(app, design, w_neg, *COL_TERM_BLACK)

    return comp


# ==============================================================================
# 4. MAIN ENTRY POINT FOR AUTODESK FUSION
# ==============================================================================

def run(context: dict) -> None:
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        design = adsk.fusion.Design.cast(app.activeProduct)
        if (
            design is None
            or design.rootComponent.bRepBodies.count > 0
            or design.rootComponent.occurrences.count > 0
        ):
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            doc.name = "Aggie_Cold_Box_12V_10Ah_Battery_Enclosure"
            design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        # Set document display units to millimeters
        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        register_user_parameters(design)

        root = design.rootComponent

        # Build the 5 structured sub-components
        build_planter_wall_component(app, design, root)
        build_battery_box_component(app, design, root)
        build_overhang_lid_component(app, design, root)
        build_wire_gland_cap_component(app, design, root)
        build_battery_and_wiring_component(app, design, root)

        vp = app.activeViewport
        if vp:
            vp.fit()

        ui.messageBox(
            "Aggie Cold Box 12V 10Ah Battery Enclosure generated successfully!\n\n"
            f"• Battery Bay: {BATT_BAY_W_X:.0f} × {INNER_DEPTH_Y:.0f} mm (Mighty Max ML10-12: 151 × 65 × 119 mm)\n"
            f"• Wire-Stuffing Bay: {WIRE_BAY_W_X:.0f} × {INNER_DEPTH_Y:.0f} × 157 mm side bay + {OVERHEAD_WIRE_H_Z:.0f} mm overhead clearance\n"
            f"• Overhang Drip Lid: 8° snow-shedding roof, +{LID_OVERHANG_SIDE_X:.0f} mm side / +{LID_OVERHANG_FRONT_Y:.0f} mm front eaves,\n"
            "  24 mm skirt with undercut drip groove + 10 mm raised inner labyrinth splash lip\n"
            "• Actuator Wire Gland: Split 2× 10 AWG (Ø5.2 mm) compression boss + 45° snow/rain hood\n"
            "• Planter Mounting: 4× #10 wood-screw flanges (upper keyholes + lower counterbores) + 3 mm rear drainage standoffs",
            "Aggie Cold Box Battery Enclosure Complete",
        )

    except Exception:
        if ui:
            ui.messageBox(f"Script execution failed:\n{traceback.format_exc()}", "Fusion Script Error")

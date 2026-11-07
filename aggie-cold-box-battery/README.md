# Aggie Cold Box 12V 10Ah Battery Enclosure

**Planters:** (3) Backyard Discovery *Aggie Cold Box* Cedar Planters  
**Battery:** (1) Mighty Max `ML10-12` 12V 10Ah SLA Battery (`151.0 × 65.0 × 111.0 mm` case, `119.0 mm` over F2 spade terminals)  
**Load:** (2) `200 mm` 12V RVMARINEPAT Linear Actuators lifting the cold box lid via a toggle switch (`2 × 10 AWG` leads)

| | |
|---|---|
| ![Assembled Isometric](renders/iso-assembled.png) | ![Lid Off Interior](renders/iso-lid-off.png) |
| ![Top-Down Interior](renders/top-view.png) | ![Rear Planter Mounting](renders/back-mounting.png) |

![Engineering Cross-Section](renders/cross-section-drip.png)

---

## 1. Design Highlights & Weatherproofing

| Feature | Engineering Specification |
|---|---|
| **Snow & Rain Overhang Lid (`print_overhang_lid`)** | **8° forward-sloped shed roof** (`Z = 180 mm` at back wall down to `Z = 167 mm` at front eave) so snow and rain slide forward away from the planter. Generous **`+12.0 mm` side eaves** and **`+14.0 mm` front eave overhang** with a **`24.0 mm` deep overlap skirt** (`Z = 138..162 mm`). |
| **Undercut Drip Edge + Labyrinth Splash Lip** | The underside of the lid eave features a continuous **`3.2 × 3.0 mm` undercut perimeter drip groove** inside a `3.5 mm` projecting outer drip bead so water drips cleanly off the bottom rim without wicking inward. Inside the lid, the top rim of the box steps inward to form a **`10.0 mm` tall raised inner labyrinth splash lip** (`Z = 152..162 mm`). |
| **Zero Top-Surface Fasteners** | The lid locks onto the box via **`2 × M4` stainless button-head screws** through the left and right skirt walls (`Z = 145 mm`) into brass heat-set inserts (`McMaster 94180A353`), keeping the sloped top roof 100% free of holes. |
| **Dedicated Excess Wire & Fuse Stuffing Bay** | Alongside the snug **`153.0 × 67.0 mm` Battery Cradle Bay** (which locks the `151 × 65 mm` Mighty Max battery behind a `40 mm` tall internal divider rib so it cannot slide), the right side of the box provides a **`42.0 × 67.0 × 157.0 mm` Wire-Stuffing Bay** (`442 cm³`) plus **`35.0 mm` of full-width overhead headroom** (`466 cm³`) above the F2 terminals and **`2×` internal zip-tie anchor bridges** on the back wall. |
| **Split `2 × 10 AWG` Compression Gland + 45° Rain Hood** | Located low on the right side wall (`Z = 26.0 mm`) for a natural downward drip loop. Two precision **`Ø5.2 mm` clamping channels** (`12.0 mm` apart) accept two insulated `10 AWG` actuator wires (`~5.0 mm` OD) with a recessed seal pocket and bolt-on clamping cap (`print_wire_gland_cap`, `2 × M4` heat-set inserts). Directly above the gland sits an integrated **45° overhanging rain and snow shield**. |
| **Aggie Cold Box Cedar Back-Wall Mounting** | Left and right **`20.0 mm` wide × `8.0 mm` thick gusseted mounting flanges** (`229.0 mm / 9.0 in` horizontal screw spacing, `77.0 mm` vertical spacing) feature **upper drop-on keyhole slots** + **lower counterbored holes** for `4 × #10` stainless wood screws. Four **`3.0 mm` rear drainage standoff ribs** let rain and snowmelt run freely down the cedar planter wall behind the box, while `3.0 mm` internal floor ribs and `2 × Ø4.0 mm` floor weep holes keep the battery dry. |

---

## 2. Reviewing the Model in Autodesk Fusion 360

You can open and review the parametric assembly in **Autodesk Fusion 360** in either of two ways:

### Option A: Run the Native Parametric Fusion Script (Recommended)
1. In Autodesk Fusion, press **`Shift + S`** (*Utilities → Scripts and Add-Ins*).
2. Under **My Scripts**, select **`AggieBatteryBox`** (already linked into your Fusion `API/Scripts` folder, or click **`+`** and select [`cad/AggieBatteryBox`](cad/AggieBatteryBox)) and click **Run**.
3. The script generates a new parametric design (`Aggie_Cold_Box_12V_10Ah_Battery_Enclosure`) in millimeters with **5 toggleable sub-components** in the Browser tree:
   - `00_Aggie_Cold_Box_Planter_Wall` — Cedar back wall planks
   - `01_Battery_Box_Enclosure` — Main 3D-printed enclosure body
   - `02_Weatherproof_Overhang_Lid` — Sloped overhang drip lid
   - `03_10AWG_Wire_Gland_Cap` — Bolt-on 2× 10 AWG wire gland clamping cap
   - `04_MightyMax_12V_10Ah_And_Wiring` — Mighty Max ML10-12 battery, F2 spade terminals, and 2× 10 AWG leads
4. Open **Modify → Change Parameters** in Fusion to inspect all registered user parameters (`BATT_LEN_X`, `WIRE_BAY_W_X`, `OVERHEAD_WIRE_H_Z`, `LID_OVERHANG_SIDE_X`, `LID_OVERHANG_FRONT_Y`, `WIRE_BORE_DIA`, etc.).

### Option B: Open the Multi-Body STEP Assembly Directly
- In Autodesk Fusion, choose **File → Open → Open from my computer** and select:
  - [`cad/step/aggie_cold_box_battery_assembly.step`](cad/step/aggie_cold_box_battery_assembly.step)

---

## 3. Bambu Lab H2D (`350 × 320 × 325 mm`) Print Plates & STLs (`stl/`)

![Bambu Lab H2D Build Plate Layout](renders/h2d-print-plate.png)

All three parts are **100% support-free** (`≤ 45°` overhangs, verified by [`cad/plates.py`](cad/plates.py)) and pre-oriented flat on `Z = 0` for the **Bambu Lab H2D (`350 × 320 × 325 mm` bed)** — load directly into Bambu Studio and slice without rotating or enabling supports:

### H2D Build Plates (Ready to Slice)
| H2D Plate File | Footprint on H2D Bed (`X × Y × Z`) | H2D Bed Margin | What Is on the Plate |
|---|---|---|---|
| **[`stl/plate_h2d_all_in_one.stl`](stl/plate_h2d_all_in_one.stl)** | `271.0 × 192.9 × 160.0 mm` | `+79 mm X`, `+127 mm Y` | **Complete 1-plate print:** Battery Box + Overhang Drip Lid + 2× 10AWG Gland Cap |
| **[`stl/plate_h2d_01_box_and_gland.stl`](stl/plate_h2d_01_box_and_gland.stl)** | `283.0 × 80.0 × 160.0 mm` | `+67 mm X`, `+240 mm Y` | **Two-color Option (Plate 1):** Battery Box + 2× 10AWG Gland Cap (e.g., Orange PETG/ASA) |
| **[`stl/plate_h2d_02_overhang_lid.stl`](stl/plate_h2d_02_overhang_lid.stl)** | `233.0 × 98.9 × 41.6 mm` | `+117 mm X`, `+221 mm Y` | **Two-color Option (Plate 2):** Sloped Overhang Drip Lid (e.g., Dark Slate ASA) |

### Individual Pre-Oriented Part STLs
| Part File | Print Bed Footprint (`X × Y × Z`) | Bed Contact (`Z = 0`) | Support-Free Orientation Details |
|---|---|---|---|
| **[`stl/print_battery_box.stl`](stl/print_battery_box.stl)** | `249.0 × 80.0 × 160.0 mm` | `16,796 mm²` | Upright on flat floor (`Z = 0`). Side mounting flanges and rear standoffs start on the bed; mid-wall flange gussets, internal zip-tie bridges, and the 10AWG gland rain hood all use `45°` support-free bevels. |
| **[`stl/print_overhang_lid.stl`](stl/print_overhang_lid.stl)** | `233.0 × 98.9 × 41.6 mm` | `22,111 mm²` | Flipped upside-down onto its flat sloped outer roof (`Z = 0`). The inner ceiling (`Z = 6.0 mm`) is parallel to the sloped roof so the H2D prints a flat `6.0 mm` solid roof slab with zero bridging or stair-stepping, then grows the labyrinth collar and undercut drip groove straight up. |
| **[`stl/print_wire_gland_cap.stl`](stl/print_wire_gland_cap.stl)** | `22.0 × 40.0 × 8.5 mm` | `721 mm²` | Flat on its outer face (`Z = 0`), with the M4 counterbores and inner compression tongue facing upward. |

- **Recommended Filament:** **ASA** or **PETG** (UV- and weather-resistant for outdoor snow/sun exposure)
- **Bambu Studio H2D Settings:** `0.4 mm` nozzle, `0.20 mm` layer height, **4 wall loops**, **5 top/bottom shell layers**, **25% gyroid infill**, **Supports: OFF**, **Outer Brim: 5 mm** on the box and lid.

---

## 4. Hardware BOM (Per Box)

| Qty | Fastener / Hardware | Location | Notes |
|---|---|---|---|
| `4` | **M4 Tapered Heat-Set Inserts** (`McMaster 94180A353`, `Ø5.6 mm` bore) | `2×` upper box side walls (`Z = 145 mm`), `2×` right wire gland boss (`Z = 26 mm`) | Zero loose nuts |
| `4` | **M4 × 14 mm Stainless Button-Head Screws** (`ISO 7380`) | `2×` Overhang Lid side lock screws, `2×` 10 AWG Wire Gland Cap | 316 or 18-8 stainless |
| `4` | **`#10 × 1"` Stainless Pan-Head Wood Screws** | `2×` upper flange drop-on keyholes, `2×` lower flange counterbores | Threads into Aggie Cold Box cedar back planks (`20 mm` thick) |
| `2–3` | **UV-Black Nylon Zip Ties (`4 mm` wide)** | Internal back-wall zip-tie anchor bridges in the wire-stuffing bay | Secures excess `10 AWG` actuator wire & inline fuse |

---

## 5. Rebuilding CAD, Renders & Interactive 3D Viewer

```bash
cd aggie-cold-box-battery/cad
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Build parametric assembly, run 3D solid clash check (0.00 mm³), export STEP, STLs & viewer JSON:
.venv/bin/python box.py --clash

# Regenerate shaded orthographic/isometric PNGs and cross-section diagram:
MPLCONFIGDIR=/tmp/mpl .venv/bin/python render.py

# Launch interactive 3D web viewer locally at http://localhost:8000:
cd ../viewer && python3 -m http.server 8000
```

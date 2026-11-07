# Home Projects (`home`)

CAD models, 3D printing enclosures, hardware automation, and build documentation for home and garden projects.

## Projects

- **[Aggie Cold Box 12V 10Ah Battery Enclosure (`aggie-cold-box-battery/`)](aggie-cold-box-battery/README.md)** — Weatherproof 3D-printed battery enclosure mounted to the cedar back wall of our three **Backyard Discovery Aggie Cold Box** planters. Houses one **Mighty Max 12V 10Ah (`ML10-12`)** SLA battery driving two **200 mm 12V RVMARINEPAT linear actuators** on a toggle switch to lift the cold box lid.
  - **[Autodesk Fusion 360 Parametric Script (`cad/AggieBatteryBox/`)](aggie-cold-box-battery/cad/AggieBatteryBox/AggieBatteryBox.py)** — Native Fusion 360 script (`Shift+S`) generating the 5-component parametric assembly with `Modify -> Change Parameters` support
  - **[STEP Assembly (`cad/step/aggie_cold_box_battery_assembly.step`)](aggie-cold-box-battery/cad/step/aggie_cold_box_battery_assembly.step)** — Multi-body STEP assembly ready to open directly in Fusion 360
  - **[Support-Free Printable STLs (`stl/`)](aggie-cold-box-battery/stl/)** — Pre-oriented parts (`print_battery_box.stl`, `print_overhang_lid.stl`, `print_wire_gland_cap.stl`, and single-plate `plate_01_all_parts.stl` fitting both Bambu P1P `256×256` and H2D `350×320`)
  - **[Interactive 3D Viewer (`viewer/index.html`)](aggie-cold-box-battery/viewer/index.html)** — Browser-based 3D assembly viewer (`cd aggie-cold-box-battery/viewer && python3 -m http.server`)

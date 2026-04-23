# Soybean Farm — Gazebo World

A small procedurally-generated soybean field for Ignition Gazebo, built from
Helios plant meshes.

## What's here

- `soybean_farm.sdf` — the world file, **5 rows × 8 plants = 40 soybean
  instances** on a ~1.5 m × 3 m field, plus a soil ground plane, directional
  sun, and physics.
- `models/soybean_plant/` — Gazebo model wrapping three Helios-generated
  soybean growth stages (30 d / 40 d / 50 d), decimated in Blender for
  real-time rendering.
- `generate_world.py` — regenerates `soybean_farm.sdf` with a different seed
  or layout.

## Running it

```bash
cd worlds/soybean_farm
ign gazebo soybean_farm.sdf
```

Headless check (parses + simulates a few steps, then exits):

```bash
ign gazebo -s -r --iterations 50 -v 2 soybean_farm.sdf
```

## Regenerate the layout

Edit the constants at the top of `generate_world.py` (`ROWS`, `COLS`,
`ROW_SPACING`, `PLANT_SPACING`, `AGE_WEIGHTS`, random seed) and run:

```bash
python3 generate_world.py
```

## Regenerating the soybean meshes from Helios

1. Build the Helios project (one-time):
   ```bash
   cd /home/hcp4/het_project/next_gen_lab/tools/Helios/projects/soybean_export
   mkdir -p build && cd build
   cmake .. && cmake --build . -j
   ```
2. Run from the Helios root so plugin assets resolve:
   ```bash
   cd /home/hcp4/het_project/next_gen_lab/tools/Helios
   ./projects/soybean_export/build/soybean_export
   ```
   This writes `soybean_30d.obj` … `soybean_70d.obj` into the Helios root,
   each paired with an `.mtl` that references `SoybeanLeaf.png`.
3. Decimate (uses Blender — Helios outputs 20k–130k faces per plant):
   ```bash
   blender -b -P decimate_obj.py -- soybean_30d.obj <output>.obj 0.12
   ```
   Suggested ratios: 0.12 for 30/40 d, 0.08 for 50 d, 0.03 for 60/70 d.
4. Copy decimated OBJ/MTL and `SoybeanLeaf.png` into
   `models/soybean_plant/meshes/`.

## Licensing

- **Helios plant library (source of the meshes):** GPLv2. The output meshes
  themselves are usable under attribution. See
  `/THIRDPARTY.md` at the repo root.
- **Everything else in this folder:** original work, under the same license
  as the rest of `amiga_simulation`.

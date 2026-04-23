# Soybean Farm — Gazebo World

A procedurally-generated soybean farm for Ignition Gazebo, built from Helios
plant meshes with perimeter trees, PBR-textured ground, and dynamic shadows.

![preview](preview.png)

## What's here

- `soybean_farm.sdf` — the world file: **10 rows × 30 plants = 300 soybean
  instances** on a ~5 m × 4.5 m field, 16 perimeter trees (Quaternius), a
  textured soil patch over a large grass plane, directional sun with shadows,
  and a sky.
- `models/soybean_plant/` — three Helios-generated soybean growth stages
  (30 d / 40 d / 50 d), decimated in Blender for real-time rendering
  (~2.5–3.8 k faces each).
- `models/tree_common/`, `tree_pine/`, `tree_birch/`, `tree_willow/` — CC0
  low-poly trees from Quaternius Ultimate Nature Pack.
- `ground/` — CC0 PBR color maps (soil, grass) from Poly Haven.
- `generate_world.py` — regenerate `soybean_farm.sdf` with different row/col
  counts, spacing, tree count, or random seed.
- `render_preview.py` — produce the `preview.png` above via headless Blender.
- `preview.png` — hero render of the scene.

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
`ROW_SPACING`, `PLANT_SPACING`, `NUM_TREES`, `TREE_SCALE_RANGE`,
`AGE_WEIGHTS`, random seed) and run:

```bash
python3 generate_world.py
```

## Re-render the preview

```bash
blender -b -P render_preview.py -- soybean_farm.sdf preview.png
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
3. Decimate (Blender — Helios outputs 20 k–130 k faces per plant, way too
   many for real-time):
   ```bash
   blender -b -P decimate_obj.py -- soybean_30d.obj <output>.obj 0.12
   ```
   Suggested ratios: 0.12 for 30/40 d, 0.08 for 50 d, 0.03 for 60/70 d.
4. Copy decimated OBJ/MTL and `SoybeanLeaf.png` into
   `models/soybean_plant/meshes/`.

## Licensing

- **Helios soybean meshes:** generated from the Helios plant library
  (UC Davis, GPLv2 code). The output geometry is usable under attribution.
- **Quaternius trees + Poly Haven textures:** CC0.
- **Everything original in this folder:** same license as the rest of
  `amiga_simulation`.

See `/THIRDPARTY.md` at the repo root for the full attribution list.

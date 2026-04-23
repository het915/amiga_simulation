# Third-Party Assets & Attributions

This repository bundles or depends on third-party assets and code. Each entry
below lists the source, license, and any modifications made. When adding new
third-party material, append an entry here in the same format.

---

## Vendored Source Code

### virtual_maize_field
- **Path:** `src/virtual_maize_field/`
- **Upstream:** https://github.com/FieldRobotEvent/virtual_maize_field
- **License:** GPL-3.0-or-later (see `src/virtual_maize_field/LICENSE`)
- **Modifications:** Nested `.git` directory removed prior to vendoring.
- **Notes:** GPL-3.0 is copyleft. Derivative works of this package must also
  be released under GPL-3.0-compatible terms. Keep modifications to this
  directory isolated and mirror any changes back upstream where possible.

---

## 3D Assets

### Quaternius — Ultimate Nature Pack (trees only, subset)
- **Paths:** `worlds/soybean_farm/models/tree_common/`, `tree_pine/`,
  `tree_birch/`, `tree_willow/`
- **Source:** https://quaternius.com/packs/ultimatenature.html
- **Author:** Quaternius (@quaternius)
- **License:** CC0 1.0 (public domain)
- **Modifications:** Extracted `CommonTree_1.obj`, `PineTree_1.obj`,
  `BirchTree_1.obj`, `Willow_1.obj` (+ their .mtl files) and renamed
  to `<tree>.obj` / `<tree>.mtl`. Updated `mtllib` line in each OBJ.
- **Notes:** Quaternius OBJs are Y-up; the SDF world rotates them by
  `-pi/2` around X so they stand upright in Gazebo (Z-up).

### Template
```
### <Asset name / pack>
- **Path:** <repo-relative path>
- **Source:** <URL>
- **Author:** <name / handle>
- **License:** <SPDX identifier or name + URL>
- **Modifications:** <describe, or "none">
- **Notes:** <anything a downstream user must know>
```

---

## Textures & Materials

### Poly Haven — brown_mud_leaves_01 (diffuse 1 K)
- **Path:** `worlds/soybean_farm/ground/soil_color_1k.jpg`
- **Source:** https://polyhaven.com/a/brown_mud_leaves_01
- **License:** CC0 1.0 (public domain)
- **Modifications:** None (direct JPG from Poly Haven's CDN).

### Poly Haven — forrest_ground_01 (diffuse 1 K)
- **Path:** `worlds/soybean_farm/ground/grass_color_1k.jpg`
- **Source:** https://polyhaven.com/a/forrest_ground_01
- **License:** CC0 1.0 (public domain)
- **Modifications:** None.

---

## Generated / Procedural Content

### Soybean plant meshes (30 d / 40 d / 50 d)
- **Path:** `worlds/soybean_farm/models/soybean_plant/meshes/soybean_*.obj`
  and `SoybeanLeaf.png`
- **Generator:** Helios plantarchitecture library, UC Davis
- **Generator source:** https://github.com/PlantSimulationLab/Helios
- **Generator license:** GPLv2 (code). The meshes themselves (OBJ geometry +
  UVs) are usable under attribution — GPL attaches to the code, not the
  generated geometry.
- **Modifications:** Decimated in Blender (ratios 0.12 / 0.12 / 0.08) to
  reduce face counts from ~20k–41k to ~2.5k–3.8k per plant for real-time
  rendering. Generator code at `tools/Helios/projects/soybean_export/`.
- **Attribution:** Plants generated using the Helios framework
  (Bailey Lab, UC Davis).

---

## License Compatibility Notes

This repository aims to remain safe for public reuse, including commercial
reuse. When evaluating new third-party material:

- **Preferred:** CC0, MIT, BSD, Apache-2.0
- **Acceptable with attribution:** CC-BY-4.0 (record attribution here)
- **Acceptable but isolated:** CC-BY-SA, GPL, CeCILL-C (keep in a clearly
  separated subdirectory; do not deep-integrate into permissively licensed code)
- **Reject:** CC-BY-NC (non-commercial), CC-BY-ND (no-derivatives),
  TurboSquid / CGTrader "Royalty-Free" (no redistribution), anything labeled
  "free for academic/non-commercial use only", Sketchfab "Free Standard"
  (not a CC license)

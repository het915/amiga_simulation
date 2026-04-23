---
title: "Virtual Maize Field Generator — Complete Reference"
subtitle: "Parameters, Flowcharts, Available Models & Dynamic Fields"
date: "April 2026"
geometry: margin=2.5cm
fontsize: 11pt
toc: true
toc-depth: 3
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{xcolor}
  - \usepackage{colortbl}
  - \usepackage{tikz}
  - \usetikzlibrary{shapes.geometric, arrows.meta, positioning, calc}
  - \definecolor{required}{HTML}{FFE0E0}
  - \definecolor{recommended}{HTML}{FFF3D0}
  - \definecolor{optional}{HTML}{E0FFE0}
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhead[L]{Field Generator Guide}
  - \fancyhead[R]{\thepage}
  - \fancyfoot[C]{}
---

\newpage

# 1. Overview

The field generator creates randomized corn (maize) field worlds for Gazebo simulation. Each field is procedurally generated from a YAML config file with controllable randomness.

**Key workflow:**

\begin{center}
\begin{tikzpicture}[
  node distance=1.2cm,
  box/.style={rectangle, draw, rounded corners, minimum width=3.5cm, minimum height=0.8cm, align=center, font=\small},
  arrow/.style={-{Stealth[length=3mm]}, thick}
]
  \node[box, fill=blue!15] (yaml) {Edit YAML config};
  \node[box, fill=blue!15, right=of yaml] (build) {colcon build};
  \node[box, fill=green!15, right=of build] (gen) {generate\_world};
  \node[box, fill=orange!15, below=of gen] (world) {generated.world\\(SDF file)};
  \node[box, fill=orange!15, left=of world] (map) {gt\_map.png\\(2D minimap)};
  \node[box, fill=red!15, left=of map] (sim) {Launch in\\Gazebo};

  \draw[arrow] (yaml) -- (build);
  \draw[arrow] (build) -- (gen);
  \draw[arrow] (gen) -- (world);
  \draw[arrow] (gen) -- (map);
  \draw[arrow] (world) -- (sim);
\end{tikzpicture}
\end{center}

**Commands:**
```bash
# 1. Edit config
nano src/virtual_maize_field/config/my_field.yaml

# 2. Rebuild (required after editing)
colcon build && source install/setup.bash

# 3. Generate
ros2 run virtual_maize_field generate_world my_field

# 4. Launch
ros2 launch virtual_maize_field simulation.launch.py
```

\newpage

# 2. Parameter Priority Table

Color key: \colorbox{required}{REQUIRED} = you almost always need to set this, \colorbox{recommended}{RECOMMENDED} = set for most use cases, \colorbox{optional}{OPTIONAL} = only for specific scenarios.

\begin{longtable}{p{4.5cm} p{1.5cm} p{1.8cm} p{1cm} p{4.5cm}}
\toprule
\textbf{Parameter} & \textbf{Priority} & \textbf{Default} & \textbf{Type} & \textbf{What it does} \\
\midrule
\endhead

\multicolumn{5}{l}{\textbf{FIELD LAYOUT}} \\
\midrule
\rowcolor{required}
\texttt{row\_length} & Must set & 12.0 & float & Length of each crop row (m) \\
\rowcolor{required}
\texttt{rows\_count} & Must set & 6 & int & Number of parallel rows \\
\rowcolor{recommended}
\texttt{row\_width} & Recommended & 0.75 & float & Gap between rows (m) \\
\rowcolor{required}
\texttt{row\_segments} & Must set & [straight, curved] & list & Row shape types to use \\
\rowcolor{optional}
\texttt{rows\_curve\_budget} & Optional & 1.5708 & float & Max total curvature (rad) \\
\midrule

\multicolumn{5}{l}{\textbf{STRAIGHT SEGMENTS}} \\
\midrule
\rowcolor{optional}
\texttt{row\_segment\_straight\_length\_min} & Optional & 0.5 & float & Min straight length (m) \\
\rowcolor{optional}
\texttt{row\_segment\_straight\_length\_max} & Optional & 1.0 & float & Max straight length (m) \\
\midrule

\multicolumn{5}{l}{\textbf{SINUSOIDAL CURVES}} \\
\midrule
\rowcolor{optional}
\texttt{row\_segment\_sincurved\_offset\_min} & Optional & 0.5 & float & Min lateral offset (m) \\
\rowcolor{optional}
\texttt{row\_segment\_sincurved\_offset\_max} & Optional & 1.5 & float & Max lateral offset (m) \\
\rowcolor{optional}
\texttt{row\_segment\_sincurved\_length\_min} & Optional & 3.0 & float & Min S-curve length (m) \\
\rowcolor{optional}
\texttt{row\_segment\_sincurved\_length\_max} & Optional & 5.0 & float & Max S-curve length (m) \\
\midrule

\multicolumn{5}{l}{\textbf{CURVED SEGMENTS}} \\
\midrule
\rowcolor{optional}
\texttt{row\_segment\_curved\_radius\_min} & Optional & 3.0 & float & Min turn radius (m) \\
\rowcolor{optional}
\texttt{row\_segment\_curved\_radius\_max} & Optional & 10.0 & float & Max turn radius (m) \\
\rowcolor{optional}
\texttt{row\_segment\_curved\_arc\_measure\_min} & Optional & 0.3 & float & Min arc angle (rad) \\
\rowcolor{optional}
\texttt{row\_segment\_curved\_arc\_measure\_max} & Optional & 1.0 & float & Max arc angle (rad) \\
\midrule

\multicolumn{5}{l}{\textbf{ISLAND SEGMENTS}} \\
\midrule
\rowcolor{optional}
\texttt{row\_segment\_island\_radius\_min} & Optional & 1.0 & float & Min island radius (m) \\
\rowcolor{optional}
\texttt{row\_segment\_island\_radius\_max} & Optional & 3.0 & float & Max island radius (m) \\
\midrule

\multicolumn{5}{l}{\textbf{GROUND / TERRAIN}} \\
\midrule
\rowcolor{recommended}
\texttt{ground\_elevation\_max} & Recommended & 0.2 & float & Terrain bumpiness (m). Set 0 for flat. \\
\rowcolor{optional}
\texttt{ground\_resolution} & Optional & 0.02 & float & Heightmap detail (m/pixel) \\
\rowcolor{optional}
\texttt{ground\_headland} & Optional & 2.0 & float & Flat turning area around field (m) \\
\rowcolor{optional}
\texttt{ground\_ditch\_depth} & Optional & 0.3 & float & Ditch depth at edges (m) \\
\midrule

\multicolumn{5}{l}{\textbf{PLANT PROPERTIES}} \\
\midrule
\rowcolor{recommended}
\texttt{plant\_height\_min} & Recommended & 0.3 & float & Shortest corn height (m) \\
\rowcolor{recommended}
\texttt{plant\_height\_max} & Recommended & 0.6 & float & Tallest corn height (m) \\
\rowcolor{optional}
\texttt{plant\_spacing\_min} & Optional & 0.13 & float & Min in-row spacing (m) \\
\rowcolor{optional}
\texttt{plant\_spacing\_max} & Optional & 0.19 & float & Max in-row spacing (m) \\
\rowcolor{optional}
\texttt{plant\_radius} & Optional & 0.3 & float & Collision radius (m) \\
\rowcolor{optional}
\texttt{plant\_radius\_noise} & Optional & 0.05 & float & Radius variation (m) \\
\rowcolor{optional}
\texttt{plant\_placement\_error\_max} & Optional & 0.02 & float & Planting error (m) \\
\rowcolor{optional}
\texttt{plant\_mass} & Optional & 0.3 & float & Plant mass (kg) \\
\midrule

\multicolumn{5}{l}{\textbf{GAPS / HOLES}} \\
\midrule
\rowcolor{recommended}
\texttt{hole\_prob} & Recommended & [0.06,...] & float/list & Gap probability (0--1) per row \\
\rowcolor{recommended}
\texttt{hole\_size\_max} & Recommended & [7,...] & int/list & Max missing plants per gap \\
\midrule

\multicolumn{5}{l}{\textbf{CROP TYPES}} \\
\midrule
\rowcolor{optional}
\texttt{crop\_types} & Optional & [maize\_01, maize\_02] & list & Which corn models to use \\
\midrule

\multicolumn{5}{l}{\textbf{WEEDS}} \\
\midrule
\rowcolor{optional}
\texttt{weeds} & Optional & 0 & int & Number of weed objects \\
\rowcolor{optional}
\texttt{weed\_types} & Optional & [nettle, unknown\_weed, dandelion] & list & Weed models \\
\midrule

\multicolumn{5}{l}{\textbf{LITTER / OBSTACLES}} \\
\midrule
\rowcolor{optional}
\texttt{litters} & Optional & 0 & int & Number of litter objects \\
\rowcolor{optional}
\texttt{litter\_types} & Optional & [ale, beer, coke\_can, retro\_pepsi\_can] & list & Litter models \\
\midrule

\multicolumn{5}{l}{\textbf{SPECIAL}} \\
\midrule
\rowcolor{optional}
\texttt{ghost\_objects} & Optional & false & bool & No-collision objects (vision only) \\
\rowcolor{optional}
\texttt{location\_markers} & Optional & false & bool & Place A/B navigation markers \\
\midrule

\multicolumn{5}{l}{\textbf{REPRODUCIBILITY}} \\
\midrule
\rowcolor{required}
\texttt{seed} & Must set & -1 & int & Random seed. -1 = random, fixed number = reproducible \\
\bottomrule
\end{longtable}

\newpage

# 3. Available 3D Models

## 3.1 Crop Models

\begin{tabular}{lll}
\toprule
\textbf{Model Name} & \textbf{Type} & \textbf{Notes} \\
\midrule
\texttt{maize\_01} & Corn plant variant 1 & Default mesh, randomly scaled per config \\
\texttt{maize\_02} & Corn plant variant 2 & Alternate mesh, mixed with maize\_01 \\
\bottomrule
\end{tabular}

\vspace{0.5cm}

**Only 2 crop models are available.** Both are maize (corn). Other crop types would require adding new 3D model folders to `models/`.

## 3.2 Weed Models

\begin{tabular}{llll}
\toprule
\textbf{Model Name} & \textbf{Config Key} & \textbf{Available} & \textbf{Notes} \\
\midrule
\texttt{nettle} & \texttt{nettle} & Yes & Stinging nettle mesh \\
\texttt{unknown\_weed} & \texttt{unknown\_weed} & Yes & Generic weed mesh \\
\texttt{dandelion\_*} & \texttt{dandelion} & \textbf{NO} & Regex-matched, models not shipped \\
\bottomrule
\end{tabular}

\vspace{0.3cm}

\textbf{Warning:} The \texttt{dandelion} weed type is defined in code but the actual 3D models (\texttt{dandelion\_01}, \texttt{dandelion\_02}, etc.) are \textbf{not included} in the repository. They were only distributed to FRE 2022 competition participants. Using \texttt{dandelion} in your config will cause an error. \textbf{Only use \texttt{nettle} and \texttt{unknown\_weed}.}

## 3.3 Litter Models

\begin{tabular}{lll}
\toprule
\textbf{Model Name} & \textbf{Config Key} & \textbf{Notes} \\
\midrule
\texttt{ale} & \texttt{ale} & Ale bottle, placed on its side \\
\texttt{beer} & \texttt{beer} & Beer bottle, placed on its side \\
\texttt{coke\_can} & \texttt{coke\_can} & Coca-Cola can, slightly raised \\
\texttt{retro\_pepsi\_can} & \texttt{retro\_pepsi\_can} & Retro Pepsi can, slightly raised \\
\bottomrule
\end{tabular}

## 3.4 Obstacle Models (Not configurable via YAML)

\begin{tabular}{ll}
\toprule
\textbf{Model Name} & \textbf{Notes} \\
\midrule
\texttt{stone\_01} & Small stone \\
\texttt{stone\_02} & Large stone \\
\texttt{box} & Generic box obstacle \\
\bottomrule
\end{tabular}

These are defined in code but not exposed as YAML parameters. They could be added with code modification.

## 3.5 Marker Models

\begin{tabular}{ll}
\toprule
\textbf{Model Name} & \textbf{Enabled by} \\
\midrule
\texttt{location\_marker\_a} & \texttt{location\_markers: true} \\
\texttt{location\_marker\_b} & \texttt{location\_markers: true} \\
\bottomrule
\end{tabular}

\newpage

# 4. Row Generation Flowchart

The generator builds each row by chaining random segments until the target `row_length` is reached.

\begin{center}
\begin{tikzpicture}[
  node distance=1cm,
  box/.style={rectangle, draw, rounded corners, minimum width=3cm, minimum height=0.7cm, align=center, font=\footnotesize},
  decision/.style={diamond, draw, aspect=2.5, minimum width=2cm, align=center, font=\footnotesize},
  arrow/.style={-{Stealth[length=2.5mm]}, thick}
]
  \node[box, fill=blue!15] (start) {Start: current\_length = 0};
  \node[decision, fill=yellow!20, below=1.2cm of start] (check) {current\_length\\< row\_length?};
  \node[box, fill=green!15, below=1.5cm of check] (pick) {Pick random segment\\from row\_segments list};
  \node[decision, fill=yellow!20, below=1.2cm of pick] (type) {Segment type?};

  \node[box, fill=orange!15, below left=1.2cm and 2cm of type] (straight) {Straight\\random length\\in [min, max]};
  \node[box, fill=orange!15, below=1.2cm of type] (curved) {Curved\\random radius\\+ arc angle};
  \node[box, fill=orange!15, below right=1.2cm and 2cm of type] (sincurved) {Sincurved\\random offset\\+ length};

  \node[box, fill=blue!10, below=3.5cm of type] (add) {Add segment,\\update current\_length\\+ curve budget};
  \node[box, fill=red!15, right=3cm of check] (done) {Row complete.\\Repeat for\\all rows\_count};

  \draw[arrow] (start) -- (check);
  \draw[arrow] (check) -- node[left] {yes} (pick);
  \draw[arrow] (check) -- node[above] {no} (done);
  \draw[arrow] (pick) -- (type);
  \draw[arrow] (type) -- node[above left, font=\scriptsize] {straight} (straight);
  \draw[arrow] (type) -- node[left, font=\scriptsize] {curved} (curved);
  \draw[arrow] (type) -- node[above right, font=\scriptsize] {sincurved} (sincurved);
  \draw[arrow] (straight) |- (add);
  \draw[arrow] (curved) -- (add);
  \draw[arrow] (sincurved) |- (add);
  \draw[arrow] (add.west) -- ++(-3,0) |- (check.west);
\end{tikzpicture}
\end{center}

After all rows are generated, the generator:
\begin{enumerate}
\item Applies bounded Gaussian noise to plant placements
\item Removes plants to create holes/gaps based on \texttt{hole\_prob}
\item Scatters weeds randomly within the rows
\item Places litter objects randomly in the field
\item Generates terrain heightmap with elevation and ditches
\item Saves the SDF world file
\end{enumerate}

\newpage

# 5. World Generation Pipeline

\begin{center}
\begin{tikzpicture}[
  node distance=0.8cm,
  box/.style={rectangle, draw, rounded corners, minimum width=5cm, minimum height=0.7cm, align=center, font=\footnotesize},
  arrow/.style={-{Stealth[length=2.5mm]}, thick},
  output/.style={rectangle, draw, dashed, minimum width=4cm, minimum height=0.6cm, align=center, font=\footnotesize, fill=gray!10}
]
  \node[box, fill=blue!20] (config) {Load YAML config (or CLI args)};
  \node[box, fill=blue!15, below=of config] (seed) {Initialize RNG with seed};
  \node[box, fill=green!20, below=of seed] (rows) {Generate row segments\\(straight, curved, sincurved, island)};
  \node[box, fill=green!15, below=of rows] (plants) {Place plants along rows\\(spacing, height, radius randomized)};
  \node[box, fill=yellow!20, below=of plants] (holes) {Remove plants for gaps\\(hole\_prob, hole\_size\_max)};
  \node[box, fill=orange!15, below=of holes] (extras) {Add weeds + litter\\(random positions within rows)};
  \node[box, fill=orange!20, below=of extras] (terrain) {Generate heightmap\\(elevation, ditches, headland)};
  \node[box, fill=red!15, below=of terrain] (sdf) {Write SDF world file};

  \node[output, right=2cm of sdf] (o1) {generated.world};
  \node[output, above=0.3cm of o1] (o2) {gt\_map.png};
  \node[output, above=0.3cm of o2] (o3) {gt\_map.csv};
  \node[output, above=0.3cm of o3] (o4) {markers.csv};
  \node[output, above=0.3cm of o4] (o5) {robot\_spawner.launch.py};
  \node[output, above=0.3cm of o5] (o6) {heightmap.png};

  \draw[arrow] (config) -- (seed);
  \draw[arrow] (seed) -- (rows);
  \draw[arrow] (rows) -- (plants);
  \draw[arrow] (plants) -- (holes);
  \draw[arrow] (holes) -- (extras);
  \draw[arrow] (extras) -- (terrain);
  \draw[arrow] (terrain) -- (sdf);
  \draw[arrow] (sdf) -- (o1);
  \draw[arrow, dashed] (sdf.east) ++(0,0.3) -- (o2.west);
  \draw[arrow, dashed] (sdf.east) ++(0,0.6) -- (o3.west);
  \draw[arrow, dashed] (sdf.east) ++(0,0.9) -- (o4.west);
  \draw[arrow, dashed] (sdf.east) ++(0,1.2) -- (o5.west);
  \draw[arrow, dashed] (sdf.east) ++(0,1.5) -- (o6.west);
\end{tikzpicture}
\end{center}

\newpage

# 6. Can Fields Be Dynamic?

\textbf{Short answer: No.} The field is \textbf{static} once generated. Plants do not grow, move, or change during simulation.

## What is Static

| Aspect | Behavior |
|--------|----------|
| Plant positions | Fixed at generation time |
| Plant heights | Fixed at generation time |
| Terrain | Fixed heightmap |
| Weeds/litter | Fixed positions |
| Weather/lighting | Fixed (Gazebo default) |

## How to Simulate "Dynamic" Fields

You can approximate dynamic behavior with these workarounds:

\begin{longtable}{p{4cm} p{9.5cm}}
\toprule
\textbf{Goal} & \textbf{How to achieve} \\
\midrule
Different field each run & Set \texttt{seed: -1} (uses timestamp, unique every time) \\
Growth stages & Create multiple configs with increasing \texttt{plant\_height\_min/max}. Run them in sequence. \\
Seasonal variation & Change \texttt{plant\_height}, \texttt{hole\_prob}, and \texttt{weeds} between configs \\
Field damage & Increase \texttt{hole\_prob} and \texttt{hole\_size\_max} \\
Weather variation & Modify Gazebo world \texttt{<scene>} lighting after generation \\
Multiple trials & Use different fixed seeds: \texttt{seed: 1}, \texttt{seed: 2}, etc. \\
Runtime plant removal & Use Ignition's \texttt{/world/.../remove} service to delete plant entities during simulation \\
Runtime object spawning & Use Ignition's \texttt{/world/.../create} service to add objects during simulation \\
\bottomrule
\end{longtable}

## Adding New Crop/Weed/Litter Models

To add a custom 3D model:

1. Create a folder: \texttt{models/my\_plant/}
2. Add: \texttt{model.config}, \texttt{model.sdf}, and mesh files
3. Register in \texttt{world\_generator/models.py}:
```python
CROP_MODELS = {
    "maize_01": GazeboModel(model_name="maize_01"),
    "maize_02": GazeboModel(model_name="maize_02"),
    "my_plant": GazeboModel(model_name="my_plant"),  # <-- add here
}
```
4. Use in config: \texttt{crop\_types: [maize\_01, my\_plant]}

\newpage

# 7. Minimal Config (Copy-Paste Starter)

You only need 4--5 lines for a working config. Everything else uses defaults.

```yaml
# my_field.yaml — minimal working config
row_length: 10.0
rows_count: 6
row_segments:
  - straight
seed: 42
```

# 8. Template Configs by Use Case

## 8.1 Perception Testing (dense, tall, no gaps)

```yaml
row_length: 12.0
rows_count: 8
row_width: 0.60
row_segments:
  - straight
plant_height_min: 0.5
plant_height_max: 0.8
plant_spacing_min: 0.10
plant_spacing_max: 0.14
hole_prob: 0.0
hole_size_max: 0
ground_elevation_max: 0.0
seed: 100
```

## 8.2 Navigation Challenge (curves + obstacles)

```yaml
row_length: 15.0
rows_count: 10
row_segments:
  - straight
  - curved
  - sincurved
rows_curve_budget: 2.0
weeds: 10
litters: 5
location_markers: true
ground_elevation_max: 0.3
seed: 77
```

## 8.3 Quick Debug (tiny field, fast loading)

```yaml
row_length: 4.0
rows_count: 3
row_segments:
  - straight
ground_elevation_max: 0.0
hole_prob: 0.0
hole_size_max: 0
seed: 1
```

## 8.4 Weed Detection

```yaml
row_length: 10.0
rows_count: 6
row_segments:
  - straight
weeds: 20
weed_types:
  - nettle
  - unknown_weed
hole_prob: 0.02
hole_size_max: 3
seed: 55
```

## 8.5 Litter/Object Detection

```yaml
row_length: 10.0
rows_count: 6
row_segments:
  - straight
litters: 15
litter_types:
  - ale
  - beer
  - coke_can
  - retro_pepsi_can
ghost_objects: true
seed: 88
```

\newpage

# 9. Output Files Reference

\begin{longtable}{p{5cm} p{8.5cm}}
\toprule
\textbf{File} & \textbf{Description} \\
\midrule
\texttt{generated.world} & SDF world file for Ignition Gazebo. Contains all plants, terrain, weeds, litter, markers. \\
\texttt{gt\_map.png} & 2D bird's-eye view minimap showing plant positions, START location, and markers A/B. \\
\texttt{gt\_map.csv} & CSV with columns: X, Y, kind. Every plant, weed, and litter position with its type label. \\
\texttt{markers.csv} & Marker A and B positions (only populated if \texttt{location\_markers: true}). \\
\texttt{robot\_spawner.launch.py} & Auto-generated ROS 2 launch file to spawn a robot at the correct start position and orientation. \\
\texttt{virtual\_maize\_field\_heightmap.png} & Grayscale heightmap image used for terrain generation. \\
\texttt{driving\_pattern.txt} & Text description of the expected robot driving pattern (e.g., ``S -- 1L -- 1R -- ...'') \\
\bottomrule
\end{longtable}

# 10. Quick Command Reference

\begin{longtable}{p{7cm} p{6.5cm}}
\toprule
\textbf{Command} & \textbf{What it does} \\
\midrule
\texttt{ros2 run virtual\_maize\_field generate\_world} & Generate with defaults \\
\texttt{ros2 run virtual\_maize\_field generate\_world my\_field} & Generate from config file \\
\texttt{ros2 run virtual\_maize\_field generate\_world --rows\_count 10} & Override single parameter \\
\texttt{ros2 run virtual\_maize\_field generate\_world my\_field --show\_map} & Generate and display 2D map \\
\texttt{ros2 run virtual\_maize\_field generate\_world --help} & Show all parameters \\
\texttt{./run\_field.sh my\_field} & Convenience: generate + launch \\
\texttt{./run\_field.sh --help} & List all available configs \\
\bottomrule
\end{longtable}

"""Generate soybean_farm.sdf — a 10-row x 30-plant soybean field (300 plants)
with soil ground, surrounding grass, perimeter trees, and a sky.

Run from this directory:  python3 generate_world.py
"""
import random
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "soybean_farm.sdf"

ROWS = 10
COLS = 30
ROW_SPACING = 0.50
PLANT_SPACING = 0.15
XY_JITTER = 0.03
AGES = [30, 40, 50]
AGE_WEIGHTS = [0.15, 0.50, 0.35]

FIELD_W = ROWS * ROW_SPACING    # X direction
FIELD_L = COLS * PLANT_SPACING  # Y direction
SOIL_W = FIELD_W + 2.0
SOIL_L = FIELD_L + 2.0
GRASS_W = 40.0
GRASS_L = 40.0

NUM_TREES = 16  # perimeter props
TREE_MODELS = ["tree_common", "tree_pine", "tree_birch", "tree_willow"]
TREE_SCALE_RANGE = (0.9, 1.3)  # Quaternius trees are already ~2.5-3.5 m tall
# Quaternius OBJs are Y-up; Gazebo expects Z-up -> roll by -90 deg when placed.
TREE_ROLL = -math.pi / 2

random.seed(42)


def plant_instance(i, row, col):
    age = random.choices(AGES, AGE_WEIGHTS)[0]
    x = (row - (ROWS - 1) / 2) * ROW_SPACING + random.uniform(-XY_JITTER, XY_JITTER)
    y = (col - (COLS - 1) / 2) * PLANT_SPACING + random.uniform(-XY_JITTER, XY_JITTER)
    yaw = random.uniform(0, 6.2832)
    return f"""    <model name="soybean_{i:03d}">
      <static>true</static>
      <pose>{x:.3f} {y:.3f} 0 0 0 {yaw:.3f}</pose>
      <link name="base_link">
        <visual name="visual">
          <cast_shadows>true</cast_shadows>
          <geometry>
            <mesh>
              <uri>models/soybean_plant/meshes/soybean_{age}d.obj</uri>
            </mesh>
          </geometry>
        </visual>
      </link>
    </model>"""


def tree_instance(i):
    model = random.choice(TREE_MODELS)
    # Place on a perimeter ring outside the soil patch, spread across 4 sides
    side = ["N", "S", "E", "W"][i % 4]
    ring_margin = random.uniform(3.0, 7.0)
    if side in ("N", "S"):
        x = random.uniform(-SOIL_W / 2 - 5, SOIL_W / 2 + 5)
        y = (SOIL_L / 2 + ring_margin) * (1 if side == "N" else -1)
    else:
        x = (SOIL_W / 2 + ring_margin) * (1 if side == "E" else -1)
        y = random.uniform(-SOIL_L / 2 - 5, SOIL_L / 2 + 5)
    yaw = random.uniform(0, 6.2832)
    scale = random.uniform(*TREE_SCALE_RANGE)
    return f"""    <model name="tree_{i:02d}">
      <static>true</static>
      <pose>{x:.2f} {y:.2f} 0 {TREE_ROLL:.4f} 0 {yaw:.2f}</pose>
      <link name="base_link">
        <visual name="visual">
          <cast_shadows>true</cast_shadows>
          <geometry>
            <mesh>
              <uri>models/{model}/meshes/{model}.obj</uri>
              <scale>{scale:.2f} {scale:.2f} {scale:.2f}</scale>
            </mesh>
          </geometry>
        </visual>
      </link>
    </model>"""


def main():
    plant_blocks = []
    i = 0
    for r in range(ROWS):
        for c in range(COLS):
            plant_blocks.append(plant_instance(i, r, c))
            i += 1
    plants_xml = "\n".join(plant_blocks)

    tree_blocks = [tree_instance(i) for i in range(NUM_TREES)]
    trees_xml = "\n".join(tree_blocks)

    sdf = f"""<?xml version="1.0" ?>
<sdf version="1.9">
  <world name="soybean_farm">

    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <plugin filename="gz-sim-physics-system"
            name="gz::sim::systems::Physics"></plugin>
    <plugin filename="gz-sim-user-commands-system"
            name="gz::sim::systems::UserCommands"></plugin>
    <plugin filename="gz-sim-scene-broadcaster-system"
            name="gz::sim::systems::SceneBroadcaster"></plugin>
    <plugin filename="gz-sim-sensors-system"
            name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <scene>
      <ambient>0.45 0.47 0.52 1</ambient>
      <background>0.68 0.82 0.93 1</background>
      <shadows>true</shadows>
      <sky></sky>
    </scene>

    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>5 5 10 0 0 0</pose>
      <diffuse>1.0 0.98 0.92 1</diffuse>
      <specular>0.4 0.4 0.4 1</specular>
      <direction>-0.5 0.4 -0.85</direction>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>

    <!-- Grass ground (large outer plane) -->
    <model name="grass_ground">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>{GRASS_W} {GRASS_L}</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>{GRASS_W} {GRASS_L}</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.25 0.35 0.18 1</ambient>
            <diffuse>0.45 0.58 0.28 1</diffuse>
            <specular>0.05 0.05 0.05 1</specular>
            <pbr>
              <metal>
                <albedo_map>ground/grass_color_1k.jpg</albedo_map>
                <roughness>0.95</roughness>
                <metalness>0.0</metalness>
              </metal>
            </pbr>
          </material>
        </visual>
      </link>
    </model>

    <!-- Soil field (smaller, on top of grass) -->
    <model name="soil_patch">
      <static>true</static>
      <pose>0 0 0.002 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>{SOIL_W:.2f} {SOIL_L:.2f}</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.22 0.15 0.09 1</ambient>
            <diffuse>0.50 0.35 0.22 1</diffuse>
            <specular>0.05 0.05 0.05 1</specular>
            <pbr>
              <metal>
                <albedo_map>ground/soil_color_1k.jpg</albedo_map>
                <roughness>0.95</roughness>
                <metalness>0.0</metalness>
              </metal>
            </pbr>
          </material>
        </visual>
      </link>
    </model>

    <!-- {NUM_TREES} perimeter trees -->
{trees_xml}

    <!-- {ROWS} rows x {COLS} plants = {ROWS * COLS} soybean instances -->
{plants_xml}

  </world>
</sdf>
"""
    OUT.write_text(sdf)
    print(f"wrote {OUT}  ({ROWS * COLS} plants, {NUM_TREES} trees, {OUT.stat().st_size // 1024} KB)")
    print(f"  field size: {FIELD_W:.1f} m x {FIELD_L:.1f} m")


if __name__ == "__main__":
    main()

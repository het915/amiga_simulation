"""Generate soybean_farm.sdf — a 5x8 soybean field using three Helios
growth-stage meshes (30d, 40d, 50d) placed with random template pick,
small X/Y jitter, and random yaw.

Run from this directory:  python3 generate_world.py
"""
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "soybean_farm.sdf"

ROWS = 5
COLS = 8
ROW_SPACING = 0.76     # meters between rows (standard soybean)
PLANT_SPACING = 0.20   # meters between plants within a row
XY_JITTER = 0.04
AGES = [30, 40, 50]
AGE_WEIGHTS = [0.2, 0.45, 0.35]  # bias toward 40d

random.seed(42)


def plant_instance(i, row, col):
    age = random.choices(AGES, AGE_WEIGHTS)[0]
    x = (col - (COLS - 1) / 2) * PLANT_SPACING + random.uniform(-XY_JITTER, XY_JITTER)
    y = (row - (ROWS - 1) / 2) * ROW_SPACING + random.uniform(-XY_JITTER, XY_JITTER)
    yaw = random.uniform(0, 6.2832)
    return f"""    <model name="soybean_{i:02d}">
      <static>true</static>
      <pose>{x:.3f} {y:.3f} 0 0 0 {yaw:.3f}</pose>
      <link name="base_link">
        <visual name="visual">
          <geometry>
            <mesh>
              <uri>models/soybean_plant/meshes/soybean_{age}d.obj</uri>
            </mesh>
          </geometry>
        </visual>
      </link>
    </model>"""


def main():
    instances = []
    i = 0
    for r in range(ROWS):
        for c in range(COLS):
            instances.append(plant_instance(i, r, c))
            i += 1
    plants_block = "\n".join(instances)

    field_w = COLS * PLANT_SPACING + 1.0
    field_l = ROWS * ROW_SPACING + 1.0

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

    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.95 0.92 0.85 1</diffuse>
      <specular>0.3 0.3 0.3 1</specular>
      <direction>-0.4 0.3 -0.9</direction>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>

    <scene>
      <ambient>0.45 0.45 0.45 1</ambient>
      <background>0.7 0.85 0.95 1</background>
      <grid>false</grid>
    </scene>

    <!-- Soil ground plane (soft brown) -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>{field_w * 2:.1f} {field_l * 2:.1f}</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>{field_w * 2:.1f} {field_l * 2:.1f}</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.32 0.22 0.14 1</ambient>
            <diffuse>0.45 0.30 0.18 1</diffuse>
            <specular>0.05 0.05 0.05 1</specular>
          </material>
        </visual>
      </link>
    </model>

    <!-- {ROWS} rows x {COLS} plants = {ROWS * COLS} soybean instances -->
{plants_block}

  </world>
</sdf>
"""
    OUT.write_text(sdf)
    print(f"wrote {OUT}  ({ROWS * COLS} plants, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

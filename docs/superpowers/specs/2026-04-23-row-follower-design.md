# Row Follower — Design

**Date:** 2026-04-23
**Status:** Approved for planning
**Owner:** het@operationautopilot.com

## Goal

Build a ROS 2 node that lets the Amiga robot autonomously drive down a single corn row in the `virtual_maize_field` Ignition Gazebo simulation, using only the OAK-D top-mounted RGB camera for perception. Stop when the row ends. Record numerical data of the run so accuracy can be evaluated offline.

## Non-Goals (v1)

Explicitly out of scope for this iteration — listed so future-us does not confuse omission with oversight:

- Headland turns / multi-row coverage (mower pattern)
- Inverse-perspective / bird's-eye warp
- Depth fusion using `/oak/depth`
- Obstacle avoidance
- ML-based detection (YOLO, segmentation models)
- Rosbag recording (user can always run `ros2 bag record` alongside)
- Automated Gazebo integration tests in CI

## Environment (ground truth, from codebase exploration)

- **Simulator:** Ignition Gazebo Fortress + ROS 2 Humble
- **Robot:** Amiga diff-drive, OAK-D camera on a mast at `z = 2.112 m` on `base_link`
- **Camera topics:** `/oak/rgb` (640×480 BGR @ 15 Hz), `/oak/depth`, `/oak/camera_info`, `/oak/points`
- **Control:** `/cmd_vel` (`geometry_msgs/Twist`)
- **Odometry:** `/odom` (`nav_msgs/Odometry`) @ 20 Hz, frames `odom` → `base_link`
- **Entry point:** `run_field.sh` (launches sim + robot); a second launch command starts the row follower
- **Workspace style:** colcon / ament_python, Python 3, OpenCV available via `python3-opencv`

## Architecture

One colcon package, one rclpy node. No inter-node timing. The entire data flow is readable top-to-bottom in a single file.

```
/oak/rgb (Image) ──► RowFollower ──► /cmd_vel (Twist)
/odom   (Odom)  ──►               ──► /row_follower/debug_image (Image)
                                  ──► ~/.ros/row_follower/run_<ts>.csv
```

Perception is implemented as **pure functions** in `perception.py` — stateless, take a numpy BGR array in, return detections. This lets them be unit-tested against saved PNG fixtures without a ROS runtime. The node (`follow.py`) owns all state: current mode, CSV writer, rolling buffers.

## Package Layout

```
src/row_follower/
├── package.xml                  ament_python; depends on rclpy, sensor_msgs,
│                                geometry_msgs, nav_msgs, cv_bridge,
│                                python3-opencv, python3-numpy
├── setup.py                     entry_point: row_follower.follow:main
├── setup.cfg
├── resource/row_follower
├── row_follower/
│   ├── __init__.py
│   ├── follow.py                RowFollower node (ROS I/O, state machine,
│   │                            control, logging, debug publishing)
│   └── perception.py            pure functions: hsv_mask, find_centerline,
│                                end_of_row_signal
├── launch/
│   └── follow.launch.py         loads config/default.yaml, starts node
├── config/
│   └── default.yaml             HSV thresholds, ROI, speeds, gains, CSV dir
├── test/
│   ├── test_perception.py       pytest; uses fixtures in test/fixtures/
│   ├── test_node.py             smoke test: inject Image, expect Twist
│   └── fixtures/                3–4 PNGs: good_row, end_of_row, empty
└── README.md                    5-line manual-test checklist
```

## Perception Pipeline

Runs once per camera frame. All functions live in `perception.py`.

1. **HSV mask.** Convert BGR → HSV. Threshold with defaults `H:[35,85] S:[40,255] V:[40,255]` (all ROS-param tunable). Apply morphological opening (3×3) then closing (5×5) to remove specks and fill small holes.
2. **ROI.** Keep the bottom ~60 % of the frame; the upper portion is sky/horizon and contains no rows.
3. **Stacked-band centerline fit.** Split the ROI into 4 equal-height horizontal bands. Per band:
   - Sum the binary mask column-wise → 1-D histogram.
   - Find the two highest peaks that straddle the image center `x`; these are the two rows the robot is between.
   - Record the midpoint `x` of that peak pair.
4. Fit a straight line through the 4 (band-center-y, midpoint-x) pairs (least-squares / `np.polyfit`). From the fitted line:
   - **Lateral offset** = `line(y_bottom) - (image_width / 2)`, in pixels.
   - **Heading angle** = `atan2(dx, dy)` of the fit, in radians.
5. **End-of-row signal.** Count mask pixels inside a forward sub-ROI (upper half of the kept ROI). Maintain a rolling buffer of the last `end_of_row_consecutive_frames` counts (default 10, ~0.7 s at 15 Hz). If every count in the buffer is below `end_of_row_pixels` (default 500), fire the signal.

**Why no inverse-perspective warp:** adds a calibration step (camera intrinsics + ground-plane extrinsics) that the stacked-band fit does not need to produce usable offset + heading. Noted as a future upgrade if heading accuracy proves insufficient.

## Control

Simple P controller, runs every frame a valid detection is produced:

```
lat_err_norm = offset_px / (image_width / 2)         # ~[-1, 1]
hdg_err      = heading_rad
omega = -k_lat * lat_err_norm - k_hdg * hdg_err
v     = v_nominal * (1 - abs(lat_err_norm) * slowdown)
```

Four tunable parameters in `config/default.yaml`: `v_nominal` (default 0.3 m/s), `k_lat`, `k_hdg`, `slowdown`. No integral or derivative term — unnecessary at low speed on a diff-drive in sim, and keeps tuning to four numbers.

## State Machine

Three states; transitions evaluated once per camera frame.

```
WAITING  ──(first valid detection)─────► FOLLOWING
FOLLOWING ──(end-of-row signal)────────► STOPPED
FOLLOWING ──(no valid detection for
             lost_detection_frames)────► STOPPED    [safety]
STOPPED: terminal; publishes Twist(0) forever, flushes CSV
```

- `WAITING` publishes `Twist(0)` so the robot does not twitch before detection stabilises.
- `STOPPED` is terminal by design — a single-row demo should not restart autonomously.
- `lost_detection_frames` default: 15 (~1 s at 15 Hz).

## Logging

CSV only. One file per run at `~/.ros/row_follower/run_<YYYYMMDD_HHMMSS>.csv`. Directory auto-created. Columns:

```
t_sec, state, odom_x, odom_y, odom_yaw,
offset_px, heading_rad, green_px_forward,
cmd_v, cmd_w
```

- One row per camera frame.
- Header written on first row.
- `csv.writer.writerow` followed by `file.flush()` so a crash does not lose rows.
- Timestamp uses wall clock (`datetime.now().strftime`) for human-scannable filenames.

## Debug Image

Topic `/row_follower/debug_image`, `sensor_msgs/Image`, BGR8, published at camera rate.

Overlay per frame:
- Green mask as a semi-transparent tint.
- The 4 band midpoints as red dots.
- The fitted centerline in yellow.
- Image-center as a white vertical line.
- Top-left text: current state, `offset_px`, `green_px_forward`.

**Optimization:** skip encoding and publishing when `get_subscription_count() == 0`. Costs nothing to leave always-on when no one is looking.

Open with `rqt_image_view /row_follower/debug_image` to watch live.

## Error Handling

Deliberately boring — fail loud, never crash, never stop the robot because logging broke.

| Condition | Behavior |
|-----------|----------|
| `/oak/rgb` not received on startup | Stay in `WAITING`, log warning every 5 s via timer |
| Mask has zero pixels | Treat as lost detection, increment counter |
| `cv_bridge` conversion exception | Log `ERROR`, skip that frame |
| CSV file cannot be opened (permission/disk) | Log `ERROR` once, keep publishing `cmd_vel` |
| `/odom` not yet received | Write empty odom cells in CSV, keep going |

## Testing Strategy

Three layers, each cheap. Each one gates a different class of regression.

1. **Unit tests** — `test/test_perception.py` with pytest. 3–4 PNG fixtures in `test/fixtures/` (a clean row view, an end-of-row view, an empty/sky view). Assert:
   - `find_centerline` returns non-None and the correct offset sign on the clean fixture.
   - `end_of_row_signal` fires on the end-of-row fixture and not on the clean one.
   - Runs in under 1 s, needs no ROS runtime.

2. **Node smoke test** — `test/test_node.py`. Instantiate `RowFollower`, inject a fake `sensor_msgs/Image`, assert a `Twist` is published on `/cmd_vel`. Catches wiring bugs (wrong topic name, wrong QoS, wrong callback signature) without needing Gazebo.

3. **Manual sim integration** — documented in `README.md`. Steps:
   1. `colcon build --packages-select row_follower && source install/setup.bash`.
   2. `bash run_field.sh` in one terminal.
   3. `ros2 launch row_follower follow.launch.py` in another.
   4. `rqt_image_view /row_follower/debug_image` in a third.
   5. Watch the robot drive down a row and stop at the end.
   6. Inspect the CSV at `~/.ros/row_follower/run_*.csv`.

No automated Gazebo integration — Ignition in CI is painful and the feature is sim-only.

## Configuration

`config/default.yaml` with all tunables grouped so they are easy to find:

```yaml
row_follower:
  ros__parameters:
    # Perception
    hsv_h_min: 35
    hsv_h_max: 85
    hsv_s_min: 40
    hsv_s_max: 255
    hsv_v_min: 40
    hsv_v_max: 255
    roi_top_frac: 0.4                # keep bottom 60 % of the frame
    n_bands: 4

    # End-of-row
    end_of_row_pixels: 500
    end_of_row_consecutive_frames: 10
    lost_detection_frames: 15

    # Control
    v_nominal: 0.3
    k_lat: 1.2
    k_hdg: 1.5
    slowdown: 0.5

    # Logging
    csv_dir: ~/.ros/row_follower
```

## Success Criteria

On a default `virtual_maize_field` straight-row config:

- Node transitions `WAITING → FOLLOWING` within 2 s of the first `/oak/rgb` message.
- Robot traverses an entire straight row without its `base_link` crossing either of the two bounding rows in the odom frame.
- `FOLLOWING → STOPPED` transition fires within 1.5 s of the last plants leaving the forward sub-ROI.
- A CSV is produced at `~/.ros/row_follower/run_<ts>.csv` containing one row per received `/oak/rgb` frame over the full run, with the header row present.
- `rqt_image_view /row_follower/debug_image` shows the mask tint, 4 band midpoints, fitted centerline, and a state/offset text overlay at camera rate.

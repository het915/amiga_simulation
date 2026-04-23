#!/bin/bash
# ============================================================================
# Corn Field Simulation Launcher
# ============================================================================
# Generates a world from your config and launches it in Ignition Fortress.
#
# Usage:
#   ./run_field.sh                  # Uses custom_field.yaml (default)
#   ./run_field.sh my_config        # Uses config/my_config.yaml
#   ./run_field.sh --headless       # Run without GUI (server only)
#   ./run_field.sh --map            # Show the 2D ground truth map after generation
#   ./run_field.sh --generate-only  # Generate world file without launching sim
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_NAME="custom_field"
HEADLESS="False"
SHOW_MAP=""
GENERATE_ONLY=false

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --headless)
            HEADLESS="True"
            ;;
        --map)
            SHOW_MAP="--show_map"
            ;;
        --generate-only)
            GENERATE_ONLY=true
            ;;
        --help|-h)
            echo "Usage: $0 [CONFIG_NAME] [--headless] [--map] [--generate-only]"
            echo ""
            echo "  CONFIG_NAME      Name of yaml config in config/ folder (default: custom_field)"
            echo "  --headless       Run simulation without GUI"
            echo "  --map            Show 2D ground truth map after generation"
            echo "  --generate-only  Only generate the world file, don't launch simulation"
            echo ""
            echo "Available configs:"
            ls "$SCRIPT_DIR/src/virtual_maize_field/config/"*.yaml 2>/dev/null | \
                xargs -I{} basename {} .yaml | sed 's/^/  - /'
            exit 0
            ;;
        -*)
            echo "Unknown option: $arg (use --help for usage)"
            exit 1
            ;;
        *)
            CONFIG_NAME="$arg"
            ;;
    esac
done

# Source ROS and workspace
echo "[1/3] Sourcing ROS 2 Humble and workspace..."
source /opt/ros/humble/setup.bash
source "$SCRIPT_DIR/install/setup.bash"

# Kill any existing simulation
if pgrep -f "ign gazebo" > /dev/null 2>&1; then
    echo "      Stopping existing Ignition Gazebo processes..."
    pkill -f "ign gazebo" 2>/dev/null || true
    sleep 2
fi

# Generate world
echo "[2/3] Generating corn field from config: ${CONFIG_NAME}.yaml"
ros2 run virtual_maize_field generate_world "$CONFIG_NAME" $SHOW_MAP
echo "      World saved to: ~/.ros/virtual_maize_field/generated.world"

if [ "$GENERATE_ONLY" = true ]; then
    echo "Done (generate-only mode)."
    exit 0
fi

# Launch simulation
echo "[3/3] Launching Ignition Fortress..."
ros2 launch virtual_maize_field simulation.launch.py headless:="$HEADLESS"

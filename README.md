# vuer-collect-demo

Lightweight VR teleop demo collection using [Vuer](https://vuer.ai) + MuJoCo.
Record manipulation trajectories from a VR headset and save them as Zarr files.

## Quick start

### 1. Install

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/shara-mit-collab/vuer-collect-demo.git
cd vuer-collect-demo
uv sync
```

### 2. Set up ngrok

Create an [ngrok](https://ngrok.com) account, install the CLI, and reserve a static domain (free tier gives one). Then start a tunnel:

```bash
ngrok http 8012 --url YOUR-DOMAIN.ngrok.app
```

### 3. Run

```bash
uv run python collect_demo.py \
    --scene-dir scenes/three_block_dual_sharpa \
    --ngrok-url https://YOUR-DOMAIN.ngrok.app \
    --actuators duo \
    --hands-scale 1.5 \
    --show-lights
```

Open the URL printed in the terminal on your VR headset's browser.

> **Tip:** Set `export NGROK_URL=https://YOUR-DOMAIN.ngrok.app` in your shell profile to avoid passing `--ngrok-url` every time.

### 4. Collect demos

| Action | Trigger |
|---|---|
| **Save trajectory & reset** | Press `a` on keyboard **or** tap the blue reset box in VR |
| **Discard trajectory & reset** | Tap the delete octahedron in VR |
| **Record initial pose** | Tap the red record sphere in VR |
| **Mark timestamp (b / c)** | Press `b` or `c` on keyboard |

Trajectories are saved under `data/<scene>/<timestamp>/frames_zarr/ep_00001.zarr`.

## CLI options

| Flag | Default | Description |
|---|---|---|
| `--scene-dir` | *(required)* | Path to scene folder (must contain `*.mjcf.xml` and `assets/`) |
| `--ngrok-url` | `$NGROK_URL` or `$USER-vuer-port.ngrok.app` | Your ngrok static URL |
| `--entry-file` | auto-detect | MJCF filename inside `--scene-dir` |
| `--assets` | `assets` | Assets sub-folder name |
| `--vuer-port` | `8012` | Local WebSocket port |
| `--asset-prefix` | derived from `--ngrok-url` | Override the full asset URL prefix (advanced) |
| `--localhost` | off | Use `localhost` instead of ngrok (headset must be on same network) |
| `--data-dir` | `data` | Output directory for recordings |
| `--actuators` | `mono` | `mono` / `duo` / `none` — gripper control mode |
| `--hands-scale` | `1.0` | Scale factor for VR hands |
| `--show-lights` | off | Enable richer scene lighting |
| `--clip-head` | `10` | Frames to clip from trajectory start |
| `--reset-time` | `1.0` | Seconds to pause after reset |
| `--frame-file` | none | Path to `.frame.yaml` for initial keyframe |
| `--verbose` | off | Print asset paths |

## Adding your own scene

1. Create a folder (e.g. `scenes/my_scene/`) containing:
   - `my_scene.mjcf.xml` — your MuJoCo scene
   - `assets/` — meshes, textures, etc. referenced by the XML
2. Run with `--scene-dir scenes/my_scene`.

## Data format

Each episode is a Zarr store:

```
ep_00001.zarr/
├── trajectory/
│   ├── mocap_pos    (T, N*3)
│   ├── mocap_quat   (T, N*4)
│   ├── qpos         (T, D)
│   ├── qvel         (T, D)
│   ├── ctrl         (T, A)
│   └── ...
├── b_press          (timestamps)
├── c_press          (timestamps)
└── .zattrs          (metadata: command, trajectory_length)
```

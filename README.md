# vuer-collect-demo

Lightweight VR teleop demo collection using [Vuer](https://vuer.ai) + MuJoCo.
Record manipulation trajectories from a VR headset and save them as Zarr files.

## Prerequisites

- **Python 3.10+**
- **Meta Quest 2 / 3 / Pro** (or any WebXR-capable headset)
- A computer on the same network as the headset (or ngrok for remote access)

## Setup

### 1. Install uv (Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install

```bash
git clone https://github.com/shara-mit-collab/vuer-collect-demo.git
cd vuer-collect-demo
uv sync
```

That's it — `uv sync` creates a virtual environment and installs all dependencies automatically.

### 3. Set up ngrok (for remote access)

ngrok creates a public URL that tunnels to your local machine, so the VR headset can connect even if it's not on the same network.

1. **Create an ngrok account** at https://ngrok.com (free tier works)
2. **Install ngrok:**
   ```bash
   # macOS
   brew install ngrok
   # or download from https://ngrok.com/download
   ```
3. **Authenticate:**
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```
   (Find your auth token at https://dashboard.ngrok.com/get-started/your-authtoken)
4. **Reserve a free static domain** at https://dashboard.ngrok.com/domains — you get one free domain on the free tier. It will look something like `something-random-name.ngrok-free.app`.
5. **Add it to your shell profile** so you don't have to type it every time:
   ```bash
   echo 'export NGROK_URL=https://YOUR-DOMAIN.ngrok-free.app' >> ~/.zshrc
   source ~/.zshrc
   ```

> **Skip ngrok?** If your headset and computer are on the same WiFi network, you can use `--localhost` instead and open `https://vuer.ai/workspace?ws=ws://YOUR_COMPUTER_IP:8012` on the headset.

## Running

### 1. Start the ngrok tunnel (in a separate terminal)

```bash
ngrok http 8012 --url $NGROK_URL
```

Keep this running in the background.

### 2. Start the collection server

```bash
uv run python collect_demo.py \
    --scene-dir scenes/three_block_dual_sharpa \
    --actuators duo \
    --hands-scale 1.5 \
    --show-lights
```

The script will print a URL like:
```
Visit: https://vuer.ai/workspace?ws=wss://your-domain.ngrok-free.app
```

### 3. Connect from the VR headset

1. Open the **Meta Quest Browser** on your headset
2. Navigate to the URL printed in the terminal
3. When prompted, **allow hand tracking** permissions
4. You should see the MuJoCo scene with your hands tracked in it

## Collecting demos

Once connected and you can see the scene in VR:

| Action | How |
|---|---|
| **Save trajectory & reset** | Press `a` on your keyboard, **or** tap the blue **reset** box in VR |
| **Discard trajectory & reset** | Tap the **delete** octahedron in VR |
| **Record initial pose** | Tap the red **record** sphere in VR |
| **Mark timestamp** | Press `b` or `c` on keyboard (saved as event markers) |

Trajectories are saved to:
```
data/<scene-name>/<YYYYMMDD_HHMM>/frames_zarr/
├── ep_00001.zarr
├── ep_00002.zarr
└── ...
```

## Adding your own scene

1. Create a folder under `scenes/`:
   ```
   scenes/my_scene/
   ├── my_scene.mjcf.xml       # Your MuJoCo scene file
   └── assets/                  # Meshes, textures, etc. referenced by the XML
       ├── some_mesh.stl
       └── ...
   ```
2. The `assetdir` and `meshdir` in your XML's `<compiler>` tag should point to `assets`:
   ```xml
   <compiler assetdir="assets" meshdir="assets" />
   ```
3. Run:
   ```bash
   uv run python collect_demo.py --scene-dir scenes/my_scene --actuators duo
   ```

## CLI reference

| Flag | Default | Description |
|---|---|---|
| `--scene-dir` | *(required)* | Path to scene folder (must contain `*.mjcf.xml` and `assets/`) |
| `--ngrok-url` | `$NGROK_URL` env var | Your ngrok static URL (e.g. `https://my-domain.ngrok-free.app`) |
| `--entry-file` | auto-detect | MJCF filename inside `--scene-dir` |
| `--assets` | `assets` | Assets sub-folder name |
| `--vuer-port` | `8012` | Local WebSocket port |
| `--localhost` | off | Use localhost instead of ngrok |
| `--data-dir` | `data` | Output directory for recordings |
| `--actuators` | `mono` | `mono` (one gripper) / `duo` (two grippers) / `none` |
| `--hands-scale` | `1.0` | Scale factor for VR hands |
| `--show-lights` | off | Enable richer scene lighting |
| `--clip-head` | `10` | Frames to clip from start of each trajectory (removes noisy startup) |
| `--reset-time` | `1.0` | Seconds to pause after reset before recording starts |
| `--frame-file` | none | Path to `.frame.yaml` for initial keyframe |
| `--verbose` | off | Print all asset paths on startup |

## Data format

Each episode is a [Zarr](https://zarr.readthedocs.io/) store:

```
ep_00001.zarr/
├── trajectory/
│   ├── mocap_pos      # (T, N*3) — end-effector positions
│   ├── mocap_quat     # (T, N*4) — end-effector quaternions (w,x,y,z)
│   ├── qpos           # (T, D)   — joint positions
│   ├── qvel           # (T, D)   — joint velocities
│   ├── ctrl           # (T, A)   — actuator controls
│   ├── site_xpos      # (T, S*3) — site positions
│   ├── site_xmat      # (T, S*9) — site rotation matrices
│   ├── sensordata     # (T, ...)
│   └── ts             # (T,)     — timestamps
├── b_press            # timestamps of 'b' key presses
├── c_press            # timestamps of 'c' key presses
└── .zattrs            # metadata: command, trajectory_length
```

Reading a trajectory in Python:
```python
import zarr
import numpy as np

ep = zarr.open("data/three_block_dual_sharpa/20260304_1131/frames_zarr/ep_00001.zarr", mode="r")
print(ep.attrs["trajectory_length"])
qpos = ep["trajectory"]["qpos"][:]  # shape (T, D)
```

## Troubleshooting

**"Connection failed" on the headset**
- Make sure ngrok is running (`ngrok http 8012 --url $NGROK_URL`)
- Make sure the collect_demo server is running
- Check that `$NGROK_URL` matches your reserved domain exactly

**Scene loads but hands don't appear**
- Grant hand tracking permission when the browser prompts
- Make sure you're using the Meta Quest Browser (not Firefox Reality)

**Server starts but headset can't load assets (broken meshes)**
- Check that the `assets/` folder is inside your `--scene-dir` and all mesh files referenced in the XML exist there

**`uv sync` fails**
- Make sure you have Python 3.10+: `python --version`
- Try `uv sync --python 3.11` to pin a specific version

# vuer-collect-demo

Lightweight VR teleop demo collection using [Vuer](https://vuer.ai) + MuJoCo.
Record manipulation trajectories from a VR headset and save them as Zarr files.

## Prerequisites

- **Python 3.10+**
- **Meta Quest 2 / 3 / Pro** (or any WebXR-capable headset)

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

### 3. Set up a tunnel

Your VR headset needs a public URL to connect to. Pick **one** of these options:

#### Option A: Cloudflare Tunnel (free, no account needed) — Recommended

Install cloudflared:
```bash
# macOS
brew install cloudflared
# Linux
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/
```

That's all — pass `--cloudflared` when running and the tunnel launches automatically. A temporary public URL is generated each time (no sign-up needed).

#### Option B: ngrok (free tier, stable URL)

If you want a **persistent URL** that doesn't change each run:

1. Create an account at https://ngrok.com (free tier works)
2. Install: `brew install ngrok`
3. Authenticate: `ngrok config add-authtoken YOUR_TOKEN`
   (find your token at https://dashboard.ngrok.com/get-started/your-authtoken)
4. Reserve a free static domain at https://dashboard.ngrok.com/domains
5. Add to your shell profile:
   ```bash
   echo 'export TUNNEL_URL=https://YOUR-DOMAIN.ngrok-free.app' >> ~/.zshrc
   source ~/.zshrc
   ```
6. Start the tunnel in a **separate terminal** before running:
   ```bash
   ngrok http 8012 --url $TUNNEL_URL
   ```

#### Option C: localhost (no tunnel, same network only)

If your headset and computer are on the same WiFi, pass `--localhost` and open `http://YOUR_COMPUTER_IP:8012/editor` on the headset.

## Running

### With cloudflared (recommended — single command)

```bash
uv run python collect_demo.py \
    --scene-dir scenes/three_block_dual_sharpa \
    --cloudflared \
    --actuators duo \
    --hands-scale 1.5 \
    --show-lights
```

### With ngrok

```bash
# Terminal 1: start ngrok
ngrok http 8012 --url $TUNNEL_URL

# Terminal 2: start collection
uv run python collect_demo.py \
    --scene-dir scenes/three_block_dual_sharpa \
    --tunnel-url $TUNNEL_URL \
    --actuators duo \
    --hands-scale 1.5 \
    --show-lights
```

### With localhost

```bash
uv run python collect_demo.py \
    --scene-dir scenes/three_block_dual_sharpa \
    --localhost \
    --actuators duo \
    --hands-scale 1.5 \
    --show-lights
```

The script will print a URL like:
```
Open on headset: https://something-random.trycloudflare.com/editor
```

### Connect from the VR headset

1. Open the **Meta Quest Browser** on your headset
2. Navigate to the `/editor` URL printed in the terminal (e.g. `https://your-domain.ngrok.app/editor`)
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
   uv run python collect_demo.py --scene-dir scenes/my_scene --cloudflared --actuators duo
   ```

## CLI reference

| Flag | Default | Description |
|---|---|---|
| `--scene-dir` | *(required)* | Path to scene folder (must contain `*.mjcf.xml` and `assets/`) |
| `--cloudflared` | off | Auto-launch a free Cloudflare tunnel (no account needed) |
| `--tunnel-url` | `$TUNNEL_URL` env var | Public tunnel URL (for ngrok or manual tunnels) |
| `--localhost` | off | Use localhost instead of a tunnel |
| `--entry-file` | auto-detect | MJCF filename inside `--scene-dir` |
| `--assets` | `assets` | Assets sub-folder name |
| `--vuer-port` | `8012` | Local WebSocket port |
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
- Make sure the tunnel is running (cloudflared or ngrok)
- Make sure the collect_demo server is running
- Check that the URL on the headset matches what was printed in the terminal

**Scene loads but hands don't appear**
- Grant hand tracking permission when the browser prompts
- Make sure you're using the Meta Quest Browser (not Firefox Reality)

**Server starts but headset can't load assets (broken meshes)**
- Check that the `assets/` folder is inside your `--scene-dir` and all mesh files referenced in the XML exist there

**`uv sync` fails**
- Make sure you have Python 3.10+: `python --version`
- Try `uv sync --python 3.11` to pin a specific version

**cloudflared not found**
- Install with `brew install cloudflared` (macOS) or download from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

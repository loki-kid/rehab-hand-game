# Rehab Hand Game (Python + OpenCV + MediaPipe + Pygame)

Rehabilitation mini-games controlled by hand gestures from a webcam. Supports multiple modes (Tap, Grip/Pinch, Hold-in-Zone, Sequential Tap), levels, visual/audio feedback, mirror camera, and high-score persistence.

## Features

- Hand tracking: MediaPipe Hands (21 landmarks)
- Mirror camera view with aligned landmarks
- Modes: Tap, Grip (pinch 4–8), Hold (stay in zone), Sequential Tap (1→K)
- Levels: +1 level every 5 points; items move and bounce when level > 1
- Item lifetime: 5s (Hold uses 10s)
- Visual feedback: hit flash, fail icon, Level Up text; special effect for Grip/Hold
- Audio feedback: correct/fail (toggle ON/OFF in menu)
- Menus: Start, Mode Select, Game Over
- High score saved to JSON
- 30 FPS target

## Requirements

- Python 3.9+
- Webcam

## Setup

1. Create a virtual environment

Windows (PowerShell):

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

macOS/Linux (bash/zsh):

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Place sounds (optional but recommended)

- Put `correct.wav` and `fail.wav` in `assets/sounds/`. If missing, game runs without audio.

4. Run

```bash
python main.py
```

More details: see `docs/SETUP.md` and `PROJECT_OVERVIEW.md`.

## Controls & Flow

- ESC: Quit (in-game) / Back (menus)
- Flow: Start Menu → Mode Select → Game → Game Over (Play Again / Exit)

## Modes

- Tap: touch item with index fingertip
- Grip: pinch (distance between thumb tip 4 and index tip 8 < 40 px) while index is on item
- Hold: keep index inside item; accumulate 3s to score; item timeout 10s
- Sequential Tap: tap numbered targets in order 1→5; no per-item timeout

## Level & Scoring

- +1 point per successful hit
- Level = max(1, (score // 5) + 1)
- When level > 1, items move with speed = level × 0.5 px/frame and bounce on edges
- Timeout (non-Seq): −1 point, respawn item

## Project Structure

```
rehab_hand_game/
├── main.py
├── core/
│   ├── __init__.py
│   ├── camera_handler.py       # Webcam + MediaPipe (mirror + landmark fix)
│   ├── game_logic.py           # Items, collision, movement
│   └── storage.py              # High score JSON
├── ui/
│   ├── __init__.py
│   ├── ui_game.py              # Pygame window, HUD, effects
│   ├── menu.py                 # Start / Game Over menus
│   └── mode_selector.py        # Mode selection screen
├── assets/
│   ├── images/
│   └── sounds/
├── data/
│   └── highscore.json          # Auto-created
├── docs/
│   └── SETUP.md                # Quick setup guide
├── requirements.txt
├── README.md
└── PROJECT_OVERVIEW.md
```

## Configuration Notes

- Mirror camera is enabled via `CameraHandler(..., flip_horizontal=True)` (default). Do not flip in UI.
- Camera/UI resolution: 640×480 for alignment.
- To suppress some MediaPipe/protobuf warnings, environment vars are set at the top of `main.py`.

## Troubleshooting

- Camera not found: check `camera_index` or other apps using the webcam
- Audio errors: mixer may fail without an audio device; game still runs
- Landmarks misaligned: ensure UI does not rotate/flip frames; mirroring happens only in `core/camera_handler.py`

# rehab-hand-game

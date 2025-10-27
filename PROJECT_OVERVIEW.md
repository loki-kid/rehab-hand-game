### Rehab Hand Game – Project Overview

Rehabilitation mini-games using webcam hand tracking. Player interacts with targets using finger gestures. Built with OpenCV, MediaPipe, and Pygame.

### Key Features

- **Webcam + Hand Tracking**: Uses OpenCV for video capture and MediaPipe Hands for 21 landmarks.
- **Mirror Mode**: Frame is mirrored (selfie view) in `camera_handler.py` using `cv2.flip(..., 1)`. Landmark X coordinates are mirrored to match the flipped frame, so dots align with the hand.
- **Pygame UI**: Live camera with landmarks, HUD (score/level/mode/timer), visual effects (hit flash, fail icon, Level Up).
- **Modes**: Tap, Grip (pinch thumb-index), Hold (stay in zone), Sequential Tap (tap 1→K in order).
- **Scoring**: +1 per success; high score persisted to `data/highscore.json`.
- **Levels**: Every 5 points increases level. For level > 1, items move and bounce; speed = `level * 0.5` px/frame.
- **Item Lifetime**: 5s for Tap/Grip; 10s for Hold. On timeout: −1 score and respawn.
- **Sounds**: `assets/sounds/correct.wav` on hit; `assets/sounds/fail.wav` on timeout (via `pygame.mixer`). Toggle ON/OFF in menu.
- **Menus**: Start Menu (Start/Quit/Sound), Mode Selection, Game Over (Play Again/Exit).

### Project Structure

- `main.py`: Entry point; orchestrates menus → mode selection → gameplay → game over.
- `core/camera_handler.py`: Opens camera, runs MediaPipe, mirrors frame, adjusts landmark X for mirror.
- `core/game_logic.py`: Item model; generation, collision, movement with edge bounces.
- `core/storage.py`: High score load/save (JSON).
- `ui/ui_game.py`: Pygame window/rendering; HUD, effects.
- `ui/menu.py`: Start/Game Over menus with sound toggle.
- `ui/mode_selector.py`: Mode selection screen.
- `assets/images/`, `assets/sounds/`: Asset folders.
- `docs/SETUP.md`: Quick setup guide; `README.md` and `PROJECT_OVERVIEW.md` for docs.

### Install & Run

```bash
pip install -r requirements.txt
python main.py
```

### Controls

- **ESC**: Quit the game.

### Configuration Notes

- Mirror mode is enabled via `CameraHandler(..., flip_horizontal=True)`; do not flip in UI.
- Resolution is 640×480 (camera + UI) for alignment.
- Sounds optional; game continues if mixer fails.

### How Levels Work

- Level starts at 1. Formula: `level = max(1, (score // 5) + 1)`.
- When `level > 1`, item speed = `level * 0.5` px/frame; random direction; bounces on edges.

### Timing

- Tap/Grip items: 5s lifetime; Hold items: 10s. Timing via `pygame.time.get_ticks()`.
- On timeout (non-Seq): score −1 (not below 0), fail sound, respawn item.

### Troubleshooting

- If camera fails: check webcam availability/index. App prints a clear error.
- If audio errors: ensure an audio device is available; otherwise ignore—gameplay works without sound.

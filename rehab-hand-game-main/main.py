"""
Entry point for the Rehab Hand Game application.

Responsibilities:
- Initialize subsystems (camera, UI/game loop, game logic)
- Manage high-level application lifecycle
- Provide a simple CLI entry point for development
"""

from __future__ import annotations

import os, warnings
os.environ["GLOG_minloglevel"] = "2"  # 0=INFO,1=WARNING,2=ERROR,3=FATAL
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")


import sys

from core.camera_handler import CameraHandler
from ui.ui_game import GameUI
from core.game_logic import generate_item, check_collision, update_item_position, Item
from ui.menu import Menu
from core.storage import load_high_score, save_high_score
import pygame
from ui.mode_selector import ModeSelector


def main() -> None:
    """Main loop: menu → game → game over with high score and mute option."""
    ui = GameUI(width=640, height=480)
    ui.initialize()

    # Audio init (may fail silently in some environments)
    try:
        pygame.mixer.init()
    except Exception:
        pass

    # Load sounds
    try:
        snd_correct = pygame.mixer.Sound("assets/sounds/correct.wav")
    except Exception:
        snd_correct = None
    try:
        snd_fail = pygame.mixer.Sound("assets/sounds/fail.wav")
    except Exception:
        snd_fail = None

    # Menus and storage
    menu = Menu(width=640, height=480)
    high_score = load_high_score()
    muted = False
    game_mode = "tap"  # or "grip"

    running = True
    while running:
        # Start menu
        start, muted = menu.start_menu(ui._screen, initial_muted=muted)
        if not start:
            break

        # Mode selection
        selector = ModeSelector(width=640, height=480)
        game_mode = selector.select_mode(ui._screen, initial_mode=game_mode)

        # Run a single game round; returns final score
        score = run_game_round(ui, muted, snd_correct, snd_fail, game_mode=game_mode)

        # Update and persist high score
        if score > high_score:
            high_score = score
            save_high_score(high_score)

        # Game Over menu
        play_again, muted = menu.game_over_menu(ui._screen, score=score, high_score=high_score, muted=muted)
        if not play_again:
            running = False

    ui.shutdown()


def run_game_round(ui: GameUI, muted: bool, snd_correct: pygame.mixer.Sound | None, snd_fail: pygame.mixer.Sound | None, game_mode: str = "tap") -> int:
    """Run one gameplay session. Returns the final score."""
    camera = CameraHandler(camera_index=0, width=640, height=480, flip_horizontal=True)
    score: int = 0
    level: int = 1
    current_item: Item | None = None
    # Lifetime per item in milliseconds
    item_lifetime_ms: int = 5000
    item_spawn_time_ms: int = 0
    # Visual effect deadlines (ms)
    effects: dict = {}
    # Hold-in-Zone config/state
    hold_required_s: float = 3.0
    hold_accum_ms: int = 0

    try:
        camera.open()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")
        return 0

    try:
        # Spawn single-item only for non-seq modes
        current_item = None
        item_spawn_time_ms = pygame.time.get_ticks()
        if game_mode != "seq":
            current_item = generate_item(640, 480, radius=20, level=level)
        # Hold mode has longer per-item lifetime (10s)
        if game_mode == "hold":
            item_lifetime_ms = 10000
        # Sequential Tap setup
        seq_targets: list[tuple[int, int, int, int]] = []  # (x,y,r,label)
        seq_current = 1
        seq_total = 5
        if game_mode == "seq":
            seq_targets = []
            for i in range(1, seq_total + 1):
                t = generate_item(640, 480, radius=18, level=1)
                seq_targets.append((int(t.x), int(t.y), t.radius, i))

        while True:
            # ESC or close window ends the round (game over)
            if ui.handle_events():
                break

            data = camera.read_frame()
            if data is None:
                ui.render(None, None, fps_limit=30, item=None, score=score, level=level, time_left_s=0.0, effects=effects)
                continue

            frame_bgr, landmarks_px, index_tip = data

            # Move item based on level (not used in seq mode)
            if game_mode != "seq" and current_item is not None:
                update_item_position(current_item, 640, 480)

            # Input logic depending on mode
            if game_mode != "seq" and current_item is None:
                current_item = generate_item(640, 480, radius=20, level=level)
                item_spawn_time_ms = pygame.time.get_ticks()
            if index_tip is not None and (current_item is not None or game_mode == "seq"):
                hit = False
                if game_mode == "tap":
                    # Tap mode: index fingertip inside the item
                    hit = check_collision(index_tip[0], index_tip[1], current_item)
                elif game_mode == "grip":
                    # Grip mode: pinch detection using distance between thumb tip (4) and index tip (8)
                    # Use raw landmarks if available to get thumb tip position; fall back to tap logic if missing
                    if landmarks_px and len(landmarks_px) >= 9:
                        thumb_tip = landmarks_px[4]
                        idx_tip = landmarks_px[8]
                        # Pinch if distance < threshold (40 px)
                        dx = thumb_tip[0] - idx_tip[0]
                        dy = thumb_tip[1] - idx_tip[1]
                        pinch_dist = (dx * dx + dy * dy) ** 0.5
                        if pinch_dist < 40:
                            hit = check_collision(idx_tip[0], idx_tip[1], current_item)
                elif game_mode == "hold":
                    # Hold mode: accumulate time while index inside the item
                    if check_collision(index_tip[0], index_tip[1], current_item):
                        hold_accum_ms += 33  # approx per-frame at 30 FPS
                    else:
                        hold_accum_ms = max(0, hold_accum_ms - 50)  # decay when outside
                    if hold_accum_ms >= int(hold_required_s * 1000):
                        hit = True
                        hold_accum_ms = 0
                elif game_mode == "seq":
                    # Sequential Tap: must tap targets in order 1..K
                    if seq_targets:
                        tx, ty, tr, label = seq_targets[0]
                        if label == seq_current and check_collision(index_tip[0], index_tip[1], Item(x=tx, y=ty, radius=tr)):
                            seq_targets.pop(0)
                            seq_current += 1
                            hit = True

                if hit:
                    score += 1
                    # Level up each 5 points
                    new_level = max(1, (score // 5) + 1)
                    if new_level > level:
                        # trigger level-up effect for 1s
                        effects["levelup_until_ms"] = pygame.time.get_ticks() + 1000
                    level = new_level
                    if not muted and snd_correct is not None:
                        snd_correct.play()
                    # Hit effect by mode
                    if game_mode == "tap":
                        effects["hit_pos"] = (current_item.x, current_item.y)
                        effects["hit_until_ms"] = pygame.time.get_ticks() + 300
                    elif game_mode == "grip":
                        effects["grip_pos"] = (current_item.x, current_item.y)
                        effects["grip_until_ms"] = pygame.time.get_ticks() + 300
                    elif game_mode == "hold":
                        # Reuse grip visual for hold success
                        effects["grip_pos"] = (current_item.x, current_item.y)
                        effects["grip_until_ms"] = pygame.time.get_ticks() + 300
                    if game_mode == "seq":
                        # Completed a target; if sequence finished, refresh a new sequence
                        if not seq_targets:
                            seq_current = 1
                            for i in range(1, seq_total + 1):
                                t = generate_item(640, 480, radius=18, level=1)
                                seq_targets.append((int(t.x), int(t.y), t.radius, i))
                    else:
                        # Generate a new item with updated level
                        current_item = generate_item(640, 480, radius=20, level=level)
                        item_spawn_time_ms = pygame.time.get_ticks()

            # Lifetime management
            now_ms = pygame.time.get_ticks()
            elapsed_ms = now_ms - item_spawn_time_ms
            time_left_ms = max(0, item_lifetime_ms - elapsed_ms)
            if game_mode != "seq" and elapsed_ms >= item_lifetime_ms:
                score = max(0, score - 1)
                level = max(1, (score // 5) + 1)
                if not muted and snd_fail is not None:
                    snd_fail.play()
                # Fail effect for 0.5s
                effects["fail_until_ms"] = pygame.time.get_ticks() + 500
                current_item = generate_item(640, 480, radius=20, level=level)
                item_spawn_time_ms = now_ms

            # Render frame, landmarks, item, score/level, and effects
            item_tuple = None if game_mode == "seq" else ((int(current_item.x), int(current_item.y), current_item.radius) if current_item else None)
            ui.render(
                frame_bgr,
                landmarks_px,
                fps_limit=30,
                item=item_tuple,
                score=score,
                level=level,
                time_left_s=(time_left_ms / 1000.0 if game_mode != "seq" else None),
                effects=effects,
                mode_name=("Grip" if game_mode == "grip" else ("Hold" if game_mode == "hold" else ("Seq" if game_mode == "seq" else "Tap"))),
                seq_targets=(seq_targets if game_mode == "seq" else None),
                seq_current=seq_current,
            )

        return score
    finally:
        camera.release()


if __name__ == "__main__":
    main()

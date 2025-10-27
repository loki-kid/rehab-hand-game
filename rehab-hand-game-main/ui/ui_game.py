"""
Game UI and rendering layer (Pygame or OpenCV-based).

Responsibilities:
- Initialize window or display surface
- Render video frames and interactive items
- Handle input events and forward interactions to game logic
"""

from __future__ import annotations

from typing import Optional, Any, Tuple, List

import numpy as np
import pygame
import cv2


class GameUI:
    """Pygame-based window for rendering camera frames and simple overlays."""

    def __init__(self, width: int = 640, height: int = 480, font_path: Optional[str] = None) -> None:
        self.width = width
        self.height = height
        self._is_initialized = False
        self._screen: Optional[pygame.Surface] = None
        self._clock: Optional[pygame.time.Clock] = None
        self._should_quit: bool = False
        self._font_path = font_path

    def initialize(self) -> None:
        """Set up rendering context and resources."""
        pygame.init()
        pygame.display.set_caption("Rehab Hand Game")
        self._screen = pygame.display.set_mode((self.width, self.height))
        self._clock = pygame.time.Clock()
        self._is_initialized = True
        # Load custom font if provided
        try:
            self._font = pygame.font.Font(self._font_path, 28) if self._font_path else pygame.font.SysFont(None, 28)
            self._font_large = pygame.font.Font(self._font_path, 48) if self._font_path else pygame.font.SysFont(None, 48)
        except Exception:
            self._font = pygame.font.SysFont(None, 28)
            self._font_large = pygame.font.SysFont(None, 48)

    def convert_cv_to_surface(self, frame_bgr: np.ndarray) -> pygame.Surface:
        """Convert an OpenCV BGR frame to a Pygame Surface.

        - OpenCV uses BGR; convert to RGB
        - Do not rotate/flip here; mirroring is handled in camera_handler
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]
        # Use frombuffer to avoid unintended 90° rotation from surfarray
        return pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")

    def render(self, frame: Optional[Any], landmarks_px: Optional[List[Tuple[int, int]]], fps_limit: int = 30, item: Optional[Tuple[int, int, int]] = None, score: int = 0, level: int = 1, time_left_s: Optional[float] = None, effects: Optional[dict] = None, mode_name: str = "Tap", seq_targets: Optional[List[Tuple[int, int, int, int]]] = None, seq_current: int = 1) -> None:
        """Render current view using provided frame and simple HUD.

        Args:
            frame: OpenCV BGR frame or None
            landmarks_px: list of (x, y) pixel positions for landmarks
            fps_limit: target FPS for the loop timing
            item: optional (x, y, radius) for red circle item
            score: current score to display
            level: current difficulty level to display (top-right)
            time_left_s: countdown timer for current item
        """
        if not self._is_initialized or self._screen is None or self._clock is None:
            return

        if frame is not None:
            # Resize frame to window size before converting for better quality
            frame_resized = cv2.resize(frame, (self.width, self.height))
            surface = self.convert_cv_to_surface(frame_resized)
            self._screen.blit(surface, (0, 0))
        else:
            self._screen.fill((0, 0, 0))

        # Draw landmarks as small circles
        if landmarks_px:
            for (x, y) in landmarks_px:
                # Clamp to window bounds to avoid errors
                x = max(0, min(self.width - 1, x))
                y = max(0, min(self.height - 1, y))
                pygame.draw.circle(self._screen, (0, 255, 0), (x, y), 4)

        # Draw a single item (Tap/Grip/Hold)
        if item is not None:
            item_x, item_y, item_r = item
            pygame.draw.circle(self._screen, (255, 0, 0), (int(item_x), int(item_y)), int(item_r))

        # Draw sequence targets if provided: list of (x, y, r, label)
        if seq_targets:
            for (tx, ty, tr, label) in seq_targets:
                color = (0, 200, 255) if label == seq_current else (100, 120, 160)
                pygame.draw.circle(self._screen, color, (int(tx), int(ty)), int(tr), width=3)
                if hasattr(self, "_font") and self._font is not None:
                    num_surface = self._font.render(str(label), True, (255, 255, 255))
                    self._screen.blit(num_surface, num_surface.get_rect(center=(int(tx), int(ty))))

        # Draw score HUD at top-left
        if hasattr(self, "_font") and self._font is not None:
            # Score (top-left)
            score_surface = self._font.render(f"Score: {score}", True, (255, 255, 255))
            self._screen.blit(score_surface, (10, 10))

            # Level (top-right)
            level_text = f"Level: {level}"
            level_surface = self._font.render(level_text, True, (255, 255, 255))
            level_pos = (self.width - level_surface.get_width() - 10, 10)
            self._screen.blit(level_surface, level_pos)

            # Time left (bottom-center)
            if time_left_s is not None:
                time_text = f"Time: {max(0.0, time_left_s):.1f}s"
                time_surface = self._font.render(time_text, True, (255, 255, 0))
                time_pos = ((self.width - time_surface.get_width()) // 2, self.height - time_surface.get_height() - 10)
                self._screen.blit(time_surface, time_pos)

            # Mode (below level top-right)
            mode_surface = self._font.render(f"Mode: {mode_name}", True, (200, 200, 255))
            mode_pos = (self.width - mode_surface.get_width() - 10, 10 + level_surface.get_height() + 6)
            self._screen.blit(mode_surface, mode_pos)

        # Visual effects (optional):
        # - hit flash: draw a bright ring at item position until deadline
        # - fail icon: draw a red X at top-left until deadline
        # - level up text: flash centered text until deadline
        now_ms = pygame.time.get_ticks()
        if effects:
            # Hit flash (Tap): white/yellow rings
            hit_until = effects.get("hit_until_ms")
            hit_pos = effects.get("hit_pos")  # (x, y)
            if hit_until and hit_pos and now_ms <= hit_until:
                x, y = int(hit_pos[0]), int(hit_pos[1])
                for r in range(8, 28, 4):
                    pygame.draw.circle(self._screen, (255, 255, 200), (x, y), r, width=2)

            # Grip flash: thicker golden ring
            grip_until = effects.get("grip_until_ms")
            grip_pos = effects.get("grip_pos")
            if grip_until and grip_pos and now_ms <= grip_until:
                x, y = int(grip_pos[0]), int(grip_pos[1])
                pygame.draw.circle(self._screen, (255, 215, 0), (x, y), 24, width=5)

            # Fail icon
            fail_until = effects.get("fail_until_ms")
            if fail_until and now_ms <= fail_until:
                # Draw a red X at top-left
                x0, y0, s = 20, 20, 18
                pygame.draw.line(self._screen, (255, 80, 80), (x0, y0), (x0 + s, y0 + s), 3)
                pygame.draw.line(self._screen, (255, 80, 80), (x0 + s, y0), (x0, y0 + s), 3)

            # Level Up text
            lvl_until = effects.get("levelup_until_ms")
            if lvl_until and now_ms <= lvl_until and hasattr(self, "_font_large") and self._font_large is not None:
                text = self._font_large.render("Level Up!", True, (255, 255, 0))
                rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self._screen.blit(text, rect)

        pygame.display.flip()
        self._clock.tick(fps_limit)

    def handle_events(self) -> bool:
        """Poll and process user input events.

        Returns True if user requested to quit (ESC or window close).
        """
        if not self._is_initialized:
            return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        return False

    def shutdown(self) -> None:
        """Tear down UI resources and close window."""
        self._is_initialized = False
        pygame.quit()

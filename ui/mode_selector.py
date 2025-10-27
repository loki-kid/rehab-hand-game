from __future__ import annotations

from typing import Tuple
import pygame


class ModeSelector:
    """Screen to choose game mode: Tap vs Grip."""

    def __init__(self, width: int = 640, height: int = 480, font_path: str | None = None) -> None:
        self.width = width
        self.height = height
        self._font = pygame.font.Font(font_path, 36) if font_path else pygame.font.SysFont(None, 36)
        self._small = pygame.font.Font(font_path, 24) if font_path else pygame.font.SysFont(None, 24)

    def _draw_centered_text(self, surface: pygame.Surface, text: str, y: int, color=(255, 255, 255)) -> None:
        s = self._font.render(text, True, color)
        rect = s.get_rect(center=(self.width // 2, y))
        surface.blit(s, rect)

    def _button(self, surface: pygame.Surface, title: str, desc: str, center: Tuple[int, int]) -> pygame.Rect:
        title_s = self._small.render(title, True, (0, 0, 0))
        desc_s = self._small.render(desc, True, (40, 40, 40))
        padding_x, padding_y = 24, 14
        w = max(title_s.get_width(), desc_s.get_width()) + 2 * padding_x
        h = title_s.get_height() + desc_s.get_height() + 3 * padding_y // 2
        rect = pygame.Rect(0, 0, w, h)
        rect.center = center
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), rect, width=2, border_radius=10)
        surface.blit(title_s, title_s.get_rect(center=(center[0], center[1] - 10)))
        surface.blit(desc_s, desc_s.get_rect(center=(center[0], center[1] + 18)))
        return rect

    def select_mode(self, screen: pygame.Surface, initial_mode: str = "tap") -> str:
        """Render selection and return 'tap', 'grip', 'hold', or 'seq'. ESC/close keeps initial_mode."""
        selected = initial_mode
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return selected
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return selected
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if tap_btn.collidepoint(mx, my):
                        return "tap"
                    if grip_btn.collidepoint(mx, my):
                        return "grip"
                    if hold_btn.collidepoint(mx, my):
                        return "hold"
                    if seq_btn.collidepoint(mx, my):
                        return "seq"

            screen.fill((22, 24, 34))
            self._draw_centered_text(screen, "Select Mode", self.height // 4, (255, 255, 0))
            tap_btn = self._button(screen, "Tap Mode", "Touch item with index finger", (self.width // 2, self.height // 2 - 60))
            grip_btn = self._button(screen, "Grip Mode", "Pinch thumb + index on item", (self.width // 2, self.height // 2 + 20))
            hold_btn = self._button(screen, "Hold Mode", "Hold index inside zone N seconds", (self.width // 2, self.height // 2 + 100))
            seq_btn = self._button(screen, "Sequential Tap", "Tap targets in order 1→K", (self.width // 2, self.height // 2 + 180))
            pygame.display.flip()
            clock.tick(30)

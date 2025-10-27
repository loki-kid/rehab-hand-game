from __future__ import annotations

from typing import Optional, Tuple
import pygame


class Menu:
    """Simple Start and Game Over menus with a mute toggle."""

    def __init__(self, width: int = 640, height: int = 480, font_path: Optional[str] = None) -> None:
        self.width = width
        self.height = height
        self._font = pygame.font.Font(font_path, 36) if font_path else pygame.font.SysFont(None, 36)
        self._small = pygame.font.Font(font_path, 24) if font_path else pygame.font.SysFont(None, 24)

    def _draw_centered_text(self, surface: pygame.Surface, text: str, y: int, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        s = self._font.render(text, True, color)
        rect = s.get_rect(center=(self.width // 2, y))
        surface.blit(s, rect)

    def _button(self, surface: pygame.Surface, text: str, center: Tuple[int, int]) -> pygame.Rect:
        label = self._small.render(text, True, (0, 0, 0))
        padding_x, padding_y = 20, 10
        rect = label.get_rect()
        btn_rect = pygame.Rect(0, 0, rect.width + 2 * padding_x, rect.height + 2 * padding_y)
        btn_rect.center = center
        pygame.draw.rect(surface, (255, 255, 255), btn_rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), btn_rect, width=2, border_radius=8)
        surface.blit(label, label.get_rect(center=center))
        return btn_rect

    def start_menu(self, screen: pygame.Surface, initial_muted: bool = False) -> Tuple[bool, bool]:
        """Render Start Menu and wait for user: returns (start_game, muted)."""
        muted = initial_muted
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (False, muted)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return (False, muted)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if start_btn.collidepoint(mx, my):
                        return (True, muted)
                    if quit_btn.collidepoint(mx, my):
                        return (False, muted)
                    if mute_btn.collidepoint(mx, my):
                        muted = not muted

            screen.fill((20, 20, 30))
            self._draw_centered_text(screen, "Rehab Hand Game", self.height // 3, (255, 255, 0))
            start_btn = self._button(screen, "Start Game", (self.width // 2, self.height // 2))
            quit_btn = self._button(screen, "Quit", (self.width // 2, self.height // 2 + 60))
            mute_text = "Sound: OFF" if muted else "Sound: ON"
            mute_btn = self._button(screen, mute_text, (self.width // 2, self.height // 2 + 120))
            pygame.display.flip()
            clock.tick(30)

    def game_over_menu(self, screen: pygame.Surface, score: int, high_score: int, muted: bool) -> Tuple[bool, bool]:
        """Render Game Over menu; returns (play_again, muted)."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (False, muted)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return (False, muted)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if again_btn.collidepoint(mx, my):
                        return (True, muted)
                    if exit_btn.collidepoint(mx, my):
                        return (False, muted)
                    if mute_btn.collidepoint(mx, my):
                        muted = not muted

            screen.fill((30, 20, 20))
            self._draw_centered_text(screen, "Game Over", self.height // 3, (255, 80, 80))
            score_text = f"Score: {score}  |  High Score: {high_score}"
            info = self._small.render(score_text, True, (255, 255, 255))
            screen.blit(info, info.get_rect(center=(self.width // 2, self.height // 2 - 40)))

            again_btn = self._button(screen, "Play Again", (self.width // 2, self.height // 2 + 10))
            exit_btn = self._button(screen, "Exit", (self.width // 2, self.height // 2 + 70))
            mute_text = "Sound: OFF" if muted else "Sound: ON"
            mute_btn = self._button(screen, mute_text, (self.width // 2, self.height // 2 + 130))
            pygame.display.flip()
            clock.tick(30)

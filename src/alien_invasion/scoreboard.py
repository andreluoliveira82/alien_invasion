from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .alien_invasion import AlienInvasion


PRIMARY = (143, 255, 225)
ACCENT = (255, 207, 102)
MUTED = (121, 150, 165)
ERROR = (255, 102, 125)


class Scoreboard:
    """Render the terminal HUD, storage messages, and session results."""

    def __init__(self, ai_game: AlienInvasion) -> None:
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        self.profile = ai_game.profile
        self.font = pygame.font.SysFont("Consolas", 20)
        self.label_font = pygame.font.SysFont("Consolas", 16)
        self.score_font = pygame.font.SysFont("Consolas", 28, bold=True)
        self.summary_font = pygame.font.SysFont("Consolas", 30)
        self.title_font = pygame.font.SysFont("Consolas", 46, bold=True)
        self.message: str | None = None
        self.message_images: list[tuple[pygame.Surface, pygame.Rect]] = []
        self.summary_images: list[tuple[pygame.Surface, pygame.Rect]] = []
        self.new_high_score = False
        self.new_highest_level = False
        self.reset()

    def reset(self) -> None:
        """Clear the previous session's messages and results, then refresh HUD."""
        self.set_message(None)
        self.summary_images.clear()
        self.new_high_score = False
        self.new_highest_level = False
        self.refresh()

    def refresh(self) -> None:
        """Prepare all HUD surfaces from current profile and session values."""
        self.pilot_image = self.font.render(f"PILOTO {self.profile.name}", True, PRIMARY)
        self.pilot_rect = self.pilot_image.get_rect(topleft=(24, 5))
        self.points_image = self.label_font.render("PONTOS", True, MUTED)
        self.points_rect = self.points_image.get_rect(
            midtop=(self.screen_rect.centerx, 3)
        )
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self) -> None:
        """Center the current score beneath its label."""
        score = f"{self.stats.score:,}".replace(",", ".")
        self.score_image = self.score_font.render(score, True, PRIMARY)
        self.score_rect = self.score_image.get_rect(
            midtop=(self.screen_rect.centerx, 23)
        )

    def prep_high_score(self) -> None:
        """Show this pilot's saved record using Portuguese thousands separators."""
        score = f"{self.stats.high_score:,}".replace(",", ".")
        self.high_score_image = self.font.render(f"RECORDE {score}", True, ACCENT)
        self.high_score_rect = self.high_score_image.get_rect(topleft=(24, 30))

    def prep_level(self) -> None:
        """Prepare the current level at the right edge."""
        self.level_image = self.font.render(f"NÍVEL {self.stats.level}", True, PRIMARY)
        self.level_rect = self.level_image.get_rect(
            topright=(self.screen_rect.right - 24, 5)
        )

    def prep_ships(self) -> None:
        """Display the number of remaining lives."""
        self.ships_image = self.font.render(
            f"VIDAS {self.stats.ships_left}", True, PRIMARY
        )
        self.ships_rect = self.ships_image.get_rect(
            topright=(self.screen_rect.right - 24, 30)
        )

    def show_score(self) -> None:
        """Draw HUD and any storage error on the current gameplay frame."""
        for image, rect in (
            (self.pilot_image, self.pilot_rect),
            (self.points_image, self.points_rect),
            (self.score_image, self.score_rect),
            (self.high_score_image, self.high_score_rect),
            (self.level_image, self.level_rect),
            (self.ships_image, self.ships_rect),
            *self.message_images,
        ):
            self.screen.blit(image, rect)

    def set_message(self, message: str | None) -> None:
        """Cache a wrapped storage message at the bottom of the screen."""
        self.message = message
        self.message_images.clear()
        if not message:
            return
        lines = [""]
        for word in message.split():
            candidate = f"{lines[-1]} {word}".strip()
            if lines[-1] and self.font.size(candidate)[0] > self.screen_rect.width - 48:
                lines.append(word)
            else:
                lines[-1] = candidate
        for index, line in enumerate(lines):
            image = self.font.render(line, True, ERROR)
            rect = image.get_rect(
                midbottom=(
                    self.screen_rect.centerx,
                    self.screen_rect.bottom - 16
                    - (len(lines) - index - 1) * self.font.get_linesize(),
                )
            )
            self.message_images.append((image, rect))

    def prep_game_over(self) -> None:
        """Cache results and mark score and level records independently."""
        self.summary_images.clear()
        self.new_high_score = self.stats.score > self.stats.starting_high_score
        self.new_highest_level = self.stats.level > self.stats.starting_highest_level
        self.summary_rect = pygame.Rect(
            0, 0, min(760, self.screen_rect.width - 80), 410
        )
        self.summary_rect.center = self.screen_rect.center
        title = self.title_font.render("MISSÃO ENCERRADA", True, PRIMARY)
        self.summary_images.append(
            (title, title.get_rect(midtop=(self.summary_rect.centerx, self.summary_rect.top + 32)))
        )
        score = f"{self.stats.score:,}".replace(",", ".")
        for offset, text, is_new in (
            (126, f"PONTOS {score}", self.new_high_score),
            (182, f"NÍVEL {self.stats.level}", self.new_highest_level),
        ):
            image = self.summary_font.render(text, True, PRIMARY)
            badge = self.font.render("NOVO!", True, ACCENT) if is_new else None
            width = image.get_width() + (badge.get_width() + 20 if badge else 0)
            rect = image.get_rect(
                midleft=(self.summary_rect.centerx - width // 2, self.summary_rect.top + offset)
            )
            self.summary_images.append((image, rect))
            if badge is not None:
                self.summary_images.append(
                    (badge, badge.get_rect(midleft=(rect.right + 20, rect.centery)))
                )
        for offset, text, color in (
            (282, "[ ENTER ] JOGAR NOVAMENTE", PRIMARY),
            (330, "[ ESC ] TROCAR PILOTO", MUTED),
        ):
            image = self.font.render(text, True, color)
            self.summary_images.append(
                (image, image.get_rect(midtop=(self.summary_rect.centerx, self.summary_rect.top + offset)))
            )

    def show_game_over(self) -> None:
        """Draw the session summary over the frozen game."""
        pygame.draw.rect(self.screen, self.settings.bg_color, self.summary_rect)
        pygame.draw.rect(self.screen, MUTED, self.summary_rect, width=1)
        for image, rect in self.summary_images:
            self.screen.blit(image, rect)

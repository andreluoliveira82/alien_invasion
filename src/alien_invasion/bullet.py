from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame.sprite import Sprite

if TYPE_CHECKING:
    from .alien_invasion import AlienInvasion


class Bullet(Sprite):
    """Classe para gerenciar os projeteis disparados pela espaçonave"""

    def __init__(self, ai_game: AlienInvasion) -> None:
        """Create a projectile at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Cria um bullet rect em (0, 0) e, em seguida, define a posição correta
        self.rect = pygame.Rect(
            0, 0, self.settings.bullet_width, self.settings.bullet_height
        )
        self.rect.midtop = ai_game.ship.rect.midtop

        # Armazena a posição do projetil como um float
        self.y = float(self.rect.y)

    def update(self) -> None:
        """Desloca o projetil verticalmente pela tela"""
        self.y -= self.settings.bullet_speed_factor
        self.rect.y = self.y

    def draw_bullet(self) -> None:
        """Draw the projectile rectangle using its configured color."""
        pygame.draw.rect(self.screen, self.color, self.rect)

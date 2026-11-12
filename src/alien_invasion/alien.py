from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from .assets import IMAGE_DIR
from pygame.sprite import Sprite

if TYPE_CHECKING:
    from .alien_invasion import AlienInvasion


class Alien(Sprite):
    """Classe que representa um alien"""

    def __init__(self, ai_game: AlienInvasion) -> None:
        """Inicializa e define a posicao do alienígena"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load(IMAGE_DIR / "alien.bmp")
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.x = float(self.rect.x)

    def update(self) -> None:
        """Advance horizontally using the fleet speed and direction."""
        self.x += self.settings.alien_speed_factor * self.settings.fleet_direction
        self.rect.x = self.x

    def check_edges(self) -> bool:
        """Retorna True se o alienígena estiver na borda da tela"""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

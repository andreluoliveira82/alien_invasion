import pygame
from pygame import Rect
from pygame.sprite import Group
from .ship import Ship


class Scoreboard:
    """Classe para exibir informações de pontuação"""

    high_score_rect: Rect

    def __init__(self, ai_game):
        """Inicializa os atributos de pontuação"""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Configurações de fonte para informações de pontuação
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 24)

        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_level(self):
        """Transforma o nivel em uma imagem renderizada"""
        level_str = f"Level: {self.stats.level!s}"
        self.level_image = self.font.render(
            level_str, True, self.text_color, self.settings.bg_color
        )
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        """Mostra as espaçonaves restantes"""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)

    def prep_high_score(self):
        """Transforma a pontuação em uma imagen renderizada"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = f"High Sore: {high_score:,}"
        self.high_score_image = self.font.render(
            high_score_str.replace(",", "."),
            True,
            self.text_color,
            self.settings.bg_color,
        )
        self.high_score_rect = self.score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_score(self):
        """transforma a pontuação em uma imagem renderizada"""
        rounded_score = round(self.stats.score, -1)
        score_str = f"score: {rounded_score:,}"
        self.score_image = self.font.render(
            score_str.replace(",", "."), True, self.text_color, self.settings.bg_color
        )
        # Exibe a pontuação no canto superior direiro da tela
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def show_score(self):
        """Desenha a pontuação na tela e o nivel na tela"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

    def check_high_score(self):
        """Verifica se há uma nova pontuação máxima"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

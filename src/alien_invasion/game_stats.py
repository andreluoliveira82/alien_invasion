
class GameStats:
    """Rastreia as estatísticas de Invasão Alienígena"""

    def __init__(self, ai_game):
        """Inicializa as estatísticas"""
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.ships_left = None
        self.settings = ai_game.settings
        self.reset_stats()

    def reset_stats(self):
        """Inicializa as estatísticas que podem mudar durante um jogo"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
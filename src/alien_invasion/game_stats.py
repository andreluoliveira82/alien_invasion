
from .profiles import Profile
from .settings import Settings


class GameStats:
    """Rastreia as estatísticas de Invasão Alienígena"""

    def __init__(self, settings: Settings, profile: Profile) -> None:
        """Inicializa as estatísticas"""
        self.settings = settings
        self.profile = profile
        self.reset_stats()

    def reset_stats(self) -> None:
        """Inicializa as estatísticas que podem mudar durante um jogo"""
        self.ships_left: int = self.settings.ship_limit
        self.score: int = 0
        self.level: int = 1
        self.high_score: int = self.profile.high_score
        self.highest_level: int = self.profile.highest_level
        self.starting_high_score: int = self.high_score
        self.starting_highest_level: int = self.highest_level

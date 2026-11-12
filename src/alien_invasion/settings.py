class Settings:
    """Classe para armazenar as configurações do jogo Invasão Alienigena"""

    def __init__(self) -> None:
        """Inicializa as configurações do jogo"""

        # configurações da tela
        self.screen_width: int = 1200
        self.screen_height: int = 800
        self.fullscreen: bool = True
        self.bg_color: tuple[int, int, int] = (5, 11, 20)

        # configurações da espaçonave
        self.ship_limit: int = 3

        # configurações do projetil
        self.bullet_width: int = 30
        self.bullet_height: int = 15
        self.bullet_color: tuple[int, int, int] = (143, 255, 225)
        self.bullets_allowed: int = 5

        # configurações do alienígena
        self.fleet_drop_speed: int = 10

        # A rapidez com que o jogo acelera
        self.speedup_scale: float = 1.1
        self.score_scale: float = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self) -> None:
        """Inicializa as configurações que mudam ao longo do jogo"""
        self.ship_speed_factor: float = 3.0
        self.bullet_speed_factor: float = 2.5
        self.alien_speed_factor: float = 1.0
        self.fleet_direction: int = 1  # 1 representa a direita, -1 representa a esquerda
        self.alien_points: int = 50

    def increase_speed(self) -> None:
        """Incrementa o speed do jogo"""
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)

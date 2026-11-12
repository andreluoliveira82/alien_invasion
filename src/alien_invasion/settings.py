class Settings:
    """Classe para armazenar as configurações do jogo Invasão Alienigena"""

    def __init__(self):
        """Inicializa as configurações do jogo"""

        # configurações da tela
        self.fleet_direction = None
        self.alien_speed_factor = None
        self.bullet_speed_factor = None
        self.ship_speed_factor = None
        self.alien_points = None
        self.screen_width = 1200
        self.screen_height = 800
        self.fullscreen = True
        self.bg_color = (230, 230, 230)

        # configurações da espaçonave
        self.ship_limit = 3

        # configurações do projetil
        self.bullet_width = 30
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5

        # configurações do alienígena
        self.fleet_drop_speed = 10

        # A rapidez com que o jogo acelera
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Inicializa as configurações que mudam ao longo do jogo"""
        self.ship_speed_factor = 3
        self.bullet_speed_factor = 2.5
        self.alien_speed_factor = 1.0
        self.fleet_direction = 1  # 1 representa a direita, -1 representa a esquerda
        self.alien_points = 50

    def increase_speed(self):
        """Incrementa o speed do jogo"""
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
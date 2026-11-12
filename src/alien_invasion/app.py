import pygame

from .alien_invasion import AlienInvasion
from .profile_menu import ProfileMenu
from .profiles import ProfileStore
from .settings import Settings
from .sound_manager import SoundManager


def run() -> None:
    """Start one Alien Invasion process."""
    try:
        pygame.init()
        pygame.display.set_caption("Alien Invasion")
        settings = Settings()
        if settings.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(
                (settings.screen_width, settings.screen_height)
            )
        settings.screen_width, settings.screen_height = screen.get_size()
        clock = pygame.time.Clock()
        sound_manager = SoundManager()
        store = ProfileStore()
        while True:
            profile = ProfileMenu(screen, clock, store).run()
            if profile is None:
                break
            AlienInvasion(screen, clock, settings, store, profile, sound_manager).run_game()
    finally:
        pygame.quit()

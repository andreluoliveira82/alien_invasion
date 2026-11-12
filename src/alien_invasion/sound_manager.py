"""Optional arcade audio that never interrupts a game session."""

from pathlib import Path

import pygame

from .assets import SOUND_DIR


class SoundManager:
    """Load available effects once and tolerate missing audio devices or files."""

    FILENAMES = {
        "fire": "fire.wav",
        "hit": "hit.wav",
        "damage": "damage.wav",
        "level_up": "level_up.wav",
        "game_over": "game_over.wav",
    }

    def __init__(self, sound_dir: Path = SOUND_DIR) -> None:
        self.warning: str | None = None
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            self.warning = "Áudio indisponível. O jogo continua sem som."
            return

        unavailable = []
        for name, filename in self.FILENAMES.items():
            try:
                self._sounds[name] = pygame.mixer.Sound(str(sound_dir / filename))
            except (pygame.error, OSError):
                unavailable.append(filename)
        if unavailable:
            self.warning = f"Sons indisponíveis: {', '.join(unavailable)}."

    def play(self, name: str) -> None:
        """Play a known effect, disabling it if the audio device fails."""
        sound = self._sounds.get(name)
        if sound is None:
            return
        try:
            if not pygame.mixer.get_init():
                raise pygame.error("mixer not initialized")
            sound.play()
        except pygame.error:
            del self._sounds[name]
            warning = f"Falha ao reproduzir {self.FILENAMES[name]}."
            self.warning = f"{self.warning} {warning}" if self.warning else warning

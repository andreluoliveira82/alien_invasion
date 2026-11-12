"""Generate the game's original arcade effects using reset-phase sine tones."""

from math import sin, tau
from pathlib import Path
from struct import pack
import wave


SAMPLE_RATE = 44_100
EFFECTS = {
    "fire": ((880, .05), (440, .04)),
    "hit": ((660, .04), (990, .06)),
    "damage": ((180, .12), (110, .18)),
    "level_up": ((440, .08), (660, .08), (880, .14)),
    "game_over": ((392, .12), (294, .14), (196, .24)),
}


def write_tone(
    path: Path, notes: tuple[tuple[float, float], ...], volume: float = 0.35
) -> None:
    """Write mono PCM with a 10 ms attack and 20 ms release on each note."""
    samples = bytearray()
    for frequency, duration in notes:
        count = int(duration * SAMPLE_RATE)
        for index in range(count):
            envelope = min(
                1.0,
                index / (0.01 * SAMPLE_RATE),
                (count - 1 - index) / (0.02 * SAMPLE_RATE),
            )
            value = int(32767 * volume * envelope * sin(tau * frequency * index / SAMPLE_RATE))
            samples.extend(pack("<h", max(-32767, min(32767, value))))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(samples)


if __name__ == "__main__":
    sound_dir = Path(__file__).resolve().parents[1] / "src" / "alien_invasion" / "sounds"
    for name, notes in EFFECTS.items():
        write_tone(sound_dir / f"{name}.wav", notes)

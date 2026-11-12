# Milestone A Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver local player profiles, persistent progress, a terminal-arcade flow, original sound effects, and a portable Windows build without changing the core game rules.

**Architecture:** A small application runner owns Pygame startup and switches between `ProfileMenu` and `AlienInvasion`. `ProfileStore` alone owns JSON persistence, while `SoundManager` alone owns mixer failures and sound playback. Existing gameplay classes keep their current responsibilities and receive only the active profile dependencies they need.

**Tech Stack:** Python 3.13, Pygame 2.6, standard-library JSON/WAV support, uv, PyInstaller `onedir`, PowerShell.

**Execution context:** Create a dedicated Git worktree and branch from commit `828b73e`. Do not implement directly on `main`. Automated tests are deliberately deferred by the approved specification; every task therefore contains bounded import, persistence, or manual smoke checks.

---

## File map

**Create:**

- `src/alien_invasion/app.py`: initialize Pygame and switch between profile selection and a game session.
- `src/alien_invasion/__main__.py`: support `python -m alien_invasion`.
- `src/alien_invasion/profiles.py`: profile model, validation, JSON loading, atomic saving, and corrupt-file recovery.
- `src/alien_invasion/profile_menu.py`: keyboard-first terminal profile picker and profile-name input.
- `src/alien_invasion/sound_manager.py`: optional mixer initialization and named sound playback.
- `src/alien_invasion/sounds/*.wav`: five generated, original effects.
- `scripts/generate_sounds.py`: deterministic standard-library WAV generator.
- `scripts/build.ps1`: build and zip the portable Windows bundle.
- `run_game.py`: PyInstaller entry adapter.
- `alien-invasion.spec`: reproducible `onedir` configuration.

**Rename:**

- `src/alien_invasion/alien_invaion.py` to `src/alien_invasion/alien_invasion.py`.

**Modify:**

- `src/alien_invasion/__init__.py`: expose the real `main()` entry point.
- `src/alien_invasion/assets.py`: expose image and sound directories.
- `src/alien_invasion/alien.py`: package import and useful type hints.
- `src/alien_invasion/ship.py`: package import and useful type hints.
- `src/alien_invasion/bullet.py`: useful type hints.
- `src/alien_invasion/game_stats.py`: initialize a session from the active profile.
- `src/alien_invasion/scoreboard.py`: terminal HUD and game-over summary.
- `src/alien_invasion/settings.py`: terminal palette and typed dynamic values.
- `pyproject.toml`: project metadata, version `0.2.0`, and PyInstaller development dependency.
- `README.md`: development, controls, profiles, build, and portable distribution.
- `.gitignore`: ignore generated PyInstaller spec caches and portable archives, not the checked-in spec.

**Remove:**

- `src/alien_invasion/button.py`: the terminal flow replaces the old centered Play button.

---

### Task 1: Make the game an executable Python package

**Files:**

- Rename: `src/alien_invasion/alien_invaion.py` → `src/alien_invasion/alien_invasion.py`
- Create: `src/alien_invasion/app.py`
- Create: `src/alien_invasion/__main__.py`
- Create: `run_game.py`
- Modify: `src/alien_invasion/__init__.py`
- Modify: `src/alien_invasion/alien_invasion.py`
- Modify: `src/alien_invasion/alien.py`
- Modify: `src/alien_invasion/ship.py`
- Modify: `src/alien_invasion/scoreboard.py`

- [ ] **Step 1: Rename the misspelled game module**

Run:

```powershell
git mv src/alien_invasion/alien_invaion.py src/alien_invasion/alien_invasion.py
```

Expected: `git status --short` reports one rename after the import edits are staged.

- [ ] **Step 2: Convert all internal imports to package-relative imports**

Use this import block in `alien_invasion.py`:

```python
from .alien import Alien
from .bullet import Bullet
from .game_stats import GameStats
from .scoreboard import Scoreboard
from .settings import Settings
from .ship import Ship
```

Remove the `Buttom` import and Play-button construction. Change `alien.py` and
`ship.py` to `from .assets import IMAGE_DIR`, and change `scoreboard.py` to
`from .ship import Ship`.

- [ ] **Step 3: Add entry adapters**

Create `app.py` with the temporary runner below. Task 4 will replace its body
after the profile menu exists.

```python
from .alien_invasion import AlienInvasion


def run() -> None:
    """Start one Alien Invasion process."""
    AlienInvasion().run_game()
```

Replace `__init__.py` with:

```python
def main() -> None:
    """Run Alien Invasion from an installed command."""
    from .app import run

    run()


__all__ = ["main"]
```

Create identical thin adapters for module and PyInstaller execution:

```python
# src/alien_invasion/__main__.py
from . import main

main()
```

```python
# run_game.py
from alien_invasion import main

main()
```

- [ ] **Step 4: Remove direct-script startup from the game module**

Delete the `if __name__ == "__main__"` block from `alien_invasion.py`. The
supported entries become `python -m alien_invasion`, `alien-invasion`, and
`run_game.py` for PyInstaller.

- [ ] **Step 5: Verify package imports and compilation**

Run:

```powershell
uv run python -c "from alien_invasion import main; from alien_invasion.alien_invasion import AlienInvasion; print(main.__name__, AlienInvasion.__name__)"
uv run python -m compileall -q src run_game.py
```

Expected first output: `main AlienInvasion`. Expected second output: none and
exit code `0`.

- [ ] **Step 6: Commit the package structure**

```powershell
git add run_game.py src/alien_invasion
git commit -m "refactor: make game package executable"
```

---

### Task 2: Add durable local profiles

**Files:**

- Create: `src/alien_invasion/profiles.py`

- [ ] **Step 1: Define the profile interface**

Create these public types and signatures:

```python
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Profile:
    name: str
    high_score: int = 0
    highest_level: int = 1


class ProfileStoreError(RuntimeError):
    """Report a profile write that the UI can present without crashing."""
```

`ProfileStore` exposes `__init__(data_dir: Path | None = None)`,
`list_profiles() -> tuple[Profile, ...]`, `active_profile() -> Profile | None`,
`create(name: str) -> Profile`, `select(name: str) -> Profile`, and
`update_progress(profile: Profile, score: int, level: int) -> bool`.

The constructor resolves its default directory with:

```python
base_dir = Path(os.environ.get("LOCALAPPDATA", Path.home()))
self.data_dir = data_dir or base_dir / "AlienInvasion"
self.path = self.data_dir / "profiles.json"
self.warning: str | None = None
```

- [ ] **Step 2: Implement validation and case-insensitive identity**

Normalize only for lookup:

```python
def _profile_key(name: str) -> str:
    return name.casefold()


def _validated_name(name: str) -> str:
    cleaned = name.strip()
    if not 1 <= len(cleaned) <= 16:
        raise ValueError("O nome deve ter entre 1 e 16 caracteres.")
    if any(character.iscontrol() for character in cleaned):
        raise ValueError("O nome contém um caractere de controle.")
    return cleaned
```

Python strings do not provide `iscontrol()`. Implement the last condition with
`unicodedata.category(character).startswith("C")` and import `unicodedata`.
Store profiles internally as `dict[str, Profile]` keyed by `casefold()`, while
preserving `Profile.name` for display and JSON output. Duplicate creation raises
`ValueError("Já existe um piloto com esse nome.")`.

- [ ] **Step 3: Implement JSON loading and corrupt-file preservation**

Load only schema version `1`. Parse `active_profile` as a display name and each
profile as `Profile(name, int(high_score), max(1, int(highest_level)))`.
Reject negative scores, non-dictionaries, unknown versions, and missing names
through the same recovery branch.

The recovery branch must not overwrite the source file:

```python
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
corrupt_path = self.path.with_name(f"profiles-{timestamp}.corrupt.json")
self.path.replace(corrupt_path)
self.warning = f"Perfis inválidos preservados em {corrupt_path.name}."
self._profiles = {}
self._active_key = None
```

- [ ] **Step 4: Implement atomic writes and progress updates**

Serialize display names as JSON keys and write UTF-8 with readable indentation:

```python
payload: dict[str, Any] = {
    "version": 1,
    "active_profile": active.name if active else None,
    "profiles": {
        profile.name: {
            "high_score": profile.high_score,
            "highest_level": profile.highest_level,
        }
        for profile in self._profiles.values()
    },
}
```

Create the directory, open `profiles.tmp` as `temp_file`, call
`json.dump(payload, temp_file, ensure_ascii=False, indent=2)`, flush and
`os.fsync()`, then call `temp_path.replace(self.path)`.
Delete the temp file after a failed write and raise `ProfileStoreError` with a
Portuguese message. `update_progress()` saves and returns `True` only when
`high_score` or `highest_level` increases.

- [ ] **Step 5: Run an isolated persistence smoke check**

Run:

```powershell
uv run python -c "from pathlib import Path; from tempfile import TemporaryDirectory; from alien_invasion.profiles import ProfileStore; d=TemporaryDirectory(); s=ProfileStore(Path(d.name)); p=s.create('André'); assert s.update_progress(p, 1250, 4); r=ProfileStore(Path(d.name)); assert r.active_profile().name == 'André'; assert r.active_profile().high_score == 1250; assert r.active_profile().highest_level == 4; print('profiles ok')"
```

Expected output: `profiles ok`.

- [ ] **Step 6: Commit persistence**

```powershell
git add src/alien_invasion/profiles.py
git commit -m "feat(profiles): persist local progress"
```

---

### Task 3: Build the terminal profile menu

**Files:**

- Create: `src/alien_invasion/profile_menu.py`

- [ ] **Step 1: Define menu state and interface**

Create `ProfileMenu` with this external interface:

```python
class ProfileMenu:
    def __init__(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        store: ProfileStore,
    ) -> None:
        self.screen = screen
        self.clock = clock
        self.store = store
        self.font = pygame.font.SysFont("consolas", 28)
        self.title_font = pygame.font.SysFont("consolas", 52, bold=True)
        self.selected_index = 0
        self.typing_name = False
        self.name_buffer = ""
        self.message = store.warning

    def run(self) -> Profile | None:
        """Return the selected profile, or None when the application closes."""
```

Build display rows from `[*store.list_profiles(), None]`; `None` represents
`[ NOVO PILOTO ]`. Start the selection on the active profile when it exists.

- [ ] **Step 2: Implement keyboard and mouse behavior**

Handle these exact actions:

- `Up` and `Down`: wrap the selected row.
- `Enter` on a profile: call `store.select()` and return it.
- `Enter` on `[ NOVO PILOTO ]`: enter name-input mode.
- Text input: append `event.unicode` until 16 characters.
- `Backspace`: remove the last character.
- `Enter` while typing: call `store.create()` and return the new profile.
- `Esc` while typing: cancel input; otherwise return `None`.
- `Q` outside name input and window close: return `None`.
- Left-click a row: select it; a second click or click on the selected row
  activates the same action as `Enter`.

Catch `ValueError` and `ProfileStoreError`, keep the menu open, and place the
exception message in `self.message`.

- [ ] **Step 3: Draw the approved terminal layout**

Use the approved palette directly in this module:

```python
BACKGROUND = (5, 11, 20)
PRIMARY = (143, 255, 225)
ACCENT = (255, 207, 102)
MUTED = (121, 150, 165)
ERROR = (255, 102, 125)
```

Draw `ALIEN INVASION`, one bordered row per profile, right-aligned
`RECORDE {score} · NÍVEL {level}`, and the new-pilot row. In input mode draw
`NOME DO PILOTO: {name_buffer}_`. Draw `self.message` in `ERROR` at the bottom.
Store each row's `pygame.Rect` for mouse handling.

- [ ] **Step 4: Run the menu manually without touching real profiles**

Run this PowerShell command from the implementation worktree:

```powershell
$env:LOCALAPPDATA = Join-Path $env:TEMP 'alien-invasion-menu-smoke'; uv run python -c "import pygame; from alien_invasion.profile_menu import ProfileMenu; from alien_invasion.profiles import ProfileStore; pygame.init(); screen=pygame.display.set_mode((1000,700)); ProfileMenu(screen, pygame.time.Clock(), ProfileStore()).run(); pygame.quit()"
```

Expected: terminal menu opens; keyboard entry and selection work; closing the
window exits with code `0`. Remove only the verified smoke directory afterward:

```powershell
Remove-Item -Recurse -Force -LiteralPath (Join-Path $env:TEMP 'alien-invasion-menu-smoke')
```

- [ ] **Step 5: Commit the menu**

```powershell
git add src/alien_invasion/profile_menu.py
git commit -m "feat(ui): add terminal profile menu"
```

---

### Task 4: Connect profiles, HUD, and game-over flow

**Files:**

- Modify: `src/alien_invasion/app.py`
- Modify: `src/alien_invasion/alien_invasion.py`
- Modify: `src/alien_invasion/game_stats.py`
- Modify: `src/alien_invasion/scoreboard.py`
- Modify: `src/alien_invasion/settings.py`
- Modify: `src/alien_invasion/alien.py`
- Modify: `src/alien_invasion/ship.py`
- Modify: `src/alien_invasion/bullet.py`
- Remove: `src/alien_invasion/button.py`

- [ ] **Step 1: Move process startup into `app.run()`**

Replace the temporary runner with this flow:

```python
def run() -> None:
    """Run profile selection and game sessions until the player exits."""
    pygame.init()
    pygame.display.set_caption("Alien Invasion")
    settings = Settings()
    flags = pygame.FULLSCREEN if settings.fullscreen else 0
    size = (0, 0) if settings.fullscreen else (
        settings.screen_width,
        settings.screen_height,
    )
    screen = pygame.display.set_mode(size, flags)
    settings.screen_width, settings.screen_height = screen.get_size()
    clock = pygame.time.Clock()
    store = ProfileStore()

    while profile := ProfileMenu(screen, clock, store).run():
        AlienInvasion(screen, clock, settings, store, profile).run_game()

    pygame.quit()
```

- [ ] **Step 2: Inject process resources and active profile**

Change `AlienInvasion.__init__` to:

```python
def __init__(
    self,
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    settings: Settings,
    profile_store: ProfileStore,
    profile: Profile,
) -> None:
```

Remove Pygame/display initialization from this constructor. Store all five
dependencies. Initialize `game_active = True` and `game_over = False`, then
create the first fleet. Window close and `Q` call `pygame.quit()` and raise
`SystemExit(0)`. `Esc` returns from `run_game()` only when `game_over` is true.

- [ ] **Step 3: Initialize session stats from the profile**

Change `GameStats` to accept `Settings` and `Profile` directly:

```python
class GameStats:
    def __init__(self, settings: Settings, profile: Profile) -> None:
        self.settings = settings
        self.profile = profile
        self.high_score = profile.high_score
        self.highest_level = profile.highest_level
        self.reset_stats()

    def reset_stats(self) -> None:
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
```

Use `GameStats(settings, profile)` in `AlienInvasion`.

- [ ] **Step 4: Persist only new progress**

After scoring, call `profile_store.update_progress(profile, score, level)`. If
it returns `True`, copy `profile.high_score` and `profile.highest_level` into
`GameStats` and refresh the corresponding scoreboard surfaces. Repeat after
incrementing the level. Catch `ProfileStoreError`, keep the session running,
and expose its message through `Scoreboard.set_message()`.

- [ ] **Step 5: Implement retry and return-to-profile controls**

Create `_start_new_game()` to reset dynamic settings, stats, sprites, fleet,
ship position, scoreboard, `game_active`, and `game_over`. On the final ship
loss, set `game_active = False`, `game_over = True`, and prepare the summary.
When game over, `Enter` calls `_start_new_game()` and `Esc` makes `run_game()`
return to `app.run()`.

- [ ] **Step 6: Render the approved HUD and summary**

Set `Settings.bg_color = (5, 11, 20)` and `bullet_color = (143, 255, 225)`.
Update `Scoreboard` to render Portuguese labels and the active profile:

```text
PILOTO ANDRÉ    RECORDE 12.450    NÍVEL 3    VIDAS ◆◆◆
                         PONTOS 4.280
```

Fix `High Sore` and use the high-score surface's own rectangle. Add
`prep_game_over()` and `show_game_over()` for score, level, `NOVO!` indicators,
`[ ENTER ] JOGAR NOVAMENTE`, and `[ ESC ] TROCAR PILOTO`. Use the same terminal
palette as `ProfileMenu`.

- [ ] **Step 7: Add useful types and docstrings only where touched**

Use postponed annotations to avoid import cycles:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .alien_invasion import AlienInvasion
```

Apply this pattern to `Alien`, `Ship`, `Bullet`, and `Scoreboard`. Type event
parameters as `pygame.event.Event`, positions as `tuple[int, int]`, and methods
without results as `-> None`. Replace docstrings that merely repeat method names
with one-line behavior descriptions.

- [ ] **Step 8: Remove the obsolete button and verify both flows**

Run:

```powershell
git rm src/alien_invasion/button.py
uv run python -m compileall -q src run_game.py
$env:LOCALAPPDATA = Join-Path $env:TEMP 'alien-invasion-game-smoke'; uv run python -m alien_invasion
```

Expected: create/select profile, play, lose, retry with `Enter`, return with
`Esc`, and close without a traceback. Verify `profiles.json`, then remove only
the smoke directory with `Remove-Item -Recurse -Force -LiteralPath`.

- [ ] **Step 9: Commit integrated progression**

```powershell
git add src/alien_invasion
git commit -m "feat(game): connect profiles and session flow"
```

---

### Task 5: Add original optional sound effects

**Files:**

- Create: `scripts/generate_sounds.py`
- Create: `src/alien_invasion/sounds/fire.wav`
- Create: `src/alien_invasion/sounds/hit.wav`
- Create: `src/alien_invasion/sounds/damage.wav`
- Create: `src/alien_invasion/sounds/level_up.wav`
- Create: `src/alien_invasion/sounds/game_over.wav`
- Create: `src/alien_invasion/sound_manager.py`
- Modify: `src/alien_invasion/assets.py`
- Modify: `src/alien_invasion/alien_invasion.py`

- [ ] **Step 1: Write a deterministic WAV generator**

Use `wave`, `math.sin`, `struct.pack`, and a fixed 44,100 Hz mono 16-bit format.
Define:

```python
def write_tone(
    path: Path,
    notes: tuple[tuple[float, float], ...],
    volume: float = 0.35,
) -> None:
    """Write frequency/duration pairs as a mono PCM WAV file."""
```

For each note, generate `int(duration * 44_100)` samples. Apply a 10 ms linear
attack and 20 ms linear release to eliminate clicks. Clamp each sample to
`[-32767, 32767]` and pack it as little-endian signed 16-bit PCM.

Generate these exact sequences:

```python
SOUNDS = {
    "fire.wav": ((880.0, 0.05), (440.0, 0.04)),
    "hit.wav": ((660.0, 0.04), (990.0, 0.06)),
    "damage.wav": ((180.0, 0.12), (110.0, 0.18)),
    "level_up.wav": ((440.0, 0.08), (660.0, 0.08), (880.0, 0.14)),
    "game_over.wav": ((392.0, 0.12), (294.0, 0.14), (196.0, 0.24)),
}
```

- [ ] **Step 2: Generate and inspect the assets**

Run:

```powershell
uv run python scripts/generate_sounds.py
Get-ChildItem src/alien_invasion/sounds/*.wav | Select-Object Name,Length
```

Expected: five non-empty WAV files. Play each file locally and confirm no
clipping, long silence, or abrupt click.

- [ ] **Step 3: Centralize the sound directory**

Extend `assets.py`:

```python
PACKAGE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = PACKAGE_DIR / "images"
SOUND_DIR = PACKAGE_DIR / "sounds"
```

- [ ] **Step 4: Implement optional audio**

Create this interface:

```python
class SoundManager:
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

    def play(self, name: str) -> None:
        if sound := self._sounds.get(name):
            sound.play()
```

If `pygame.mixer.get_init()` is false, call `pygame.mixer.init()`. Catch
`pygame.error` for mixer startup and individual files. Keep successfully loaded
files, record one concise warning, and never raise from `play()`.

- [ ] **Step 5: Connect one sound to each approved event**

Construct `SoundManager` once in `app.run()` and inject it into
`AlienInvasion`. Play `fire` only after adding a bullet, `hit` once per collision
frame, `damage` at the start of `_ship_hit()`, `level_up` after incrementing the
level, and `game_over` only on the final loss. Send `SoundManager.warning` to
the scoreboard message area.

- [ ] **Step 6: Verify audio and silent fallback**

Run the game normally and trigger all five events. Then run:

```powershell
$env:SDL_AUDIODRIVER = 'dummy'; uv run python -m alien_invasion
```

Expected: normal run plays each effect; dummy-audio run remains playable and
does not raise a traceback.

- [ ] **Step 7: Commit audio**

```powershell
git add scripts/generate_sounds.py src/alien_invasion/assets.py src/alien_invasion/sound_manager.py src/alien_invasion/sounds src/alien_invasion/alien_invasion.py src/alien_invasion/app.py
git commit -m "feat(audio): add original arcade effects"
```

---

### Task 6: Build and document the portable Windows release

**Files:**

- Create: `alien-invasion.spec`
- Create: `scripts/build.ps1`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `.gitignore`
- Modify: `uv.lock`

- [ ] **Step 1: Update project metadata and build dependency**

Set `version = "0.2.0"` and replace the placeholder description with
`"Jogo arcade de defesa espacial feito com Pygame"`. Add PyInstaller through
uv so the lockfile remains authoritative:

```powershell
uv add --dev pyinstaller
```

Expected: `pyproject.toml` gains a development dependency group and `uv.lock`
records PyInstaller.

- [ ] **Step 2: Define the reproducible `onedir` bundle**

Create `alien-invasion.spec` with `run_game.py` as the script, `src` in
`pathex`, and these data mappings:

```python
datas = [
    ("src/alien_invasion/images", "alien_invasion/images"),
    ("src/alien_invasion/sounds", "alien_invasion/sounds"),
]
```

Use `console=False`, executable name `AlienInvasion`, and a `COLLECT` target
named `AlienInvasion`. Do not enable `onefile` or UPX.

- [ ] **Step 3: Add a bounded PowerShell build script**

`scripts/build.ps1` must stop on errors, build the checked-in spec, and replace
only the known archive path:

```powershell
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$archive = Join-Path $projectRoot "dist\AlienInvasion-win64.zip"

Push-Location $projectRoot
try {
    uv run pyinstaller --clean --noconfirm alien-invasion.spec
    if (Test-Path -LiteralPath $archive) {
        Remove-Item -LiteralPath $archive
    }
    Compress-Archive -Path "dist\AlienInvasion\*" -DestinationPath $archive
} finally {
    Pop-Location
}
```

- [ ] **Step 4: Keep generated outputs out of Git**

Ensure `.gitignore` contains:

```gitignore
build/
dist/
*.zip
```

Keep `alien-invasion.spec` tracked.

- [ ] **Step 5: Rewrite README as the user guide**

Document these exact sections: description, controls, profile behavior,
development requirements, `uv run python -m alien_invasion`, data location,
`powershell -ExecutionPolicy Bypass -File scripts/build.ps1`, portable archive
contents, and the deferred Inno Setup installer. State that uninstalling the
portable folder does not remove `%LOCALAPPDATA%\AlienInvasion\profiles.json`.

- [ ] **Step 6: Build and smoke-test outside the repository**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
Get-Item dist/AlienInvasion/AlienInvasion.exe, dist/AlienInvasion-win64.zip
```

Copy `dist/AlienInvasion` to a temporary directory outside the repository and
run `AlienInvasion.exe`. Verify profile creation, restart persistence, images,
all sounds, retry, and return to profile selection. Confirm the profile file is
under `%LOCALAPPDATA%`, not beside the executable.

- [ ] **Step 7: Commit release tooling and documentation**

```powershell
git add .gitignore README.md pyproject.toml uv.lock alien-invasion.spec scripts/build.ps1
git commit -m "build: add portable Windows release"
```

---

### Task 7: Run the release gate and tag `v0.2.0`

**Files:**

- Verify all tracked files; modify only defects found by this gate.

- [ ] **Step 1: Run static and packaging checks**

```powershell
uv sync
uv run python -m compileall -q src scripts run_game.py
uv run python -c "from alien_invasion import main; from alien_invasion.profiles import ProfileStore; from alien_invasion.sound_manager import SoundManager; print('imports ok')"
git diff --check
```

Expected: `imports ok`; all commands exit `0`.

- [ ] **Step 2: Run the approved manual acceptance checklist**

Use a new temporary `LOCALAPPDATA` directory. Create two profiles with names
that differ from each other. For each profile, verify isolated record and level.
Restart and verify the active profile. Corrupt `profiles.json`, restart, and
verify a timestamped `.corrupt.json` file plus a recoverable warning. Run once
with normal audio and once with `SDL_AUDIODRIVER=dummy`.

- [ ] **Step 3: Verify the portable artifact**

Rebuild from a clean generated-output state through `scripts/build.ps1`. Run
the copied bundle outside the repository. Verify no Python installation is
needed and confirm images, sounds, profiles, retry, and profile switching.

- [ ] **Step 4: Record any gate-only fixes separately**

If the gate required a source fix, rerun Steps 1–3 and commit only the affected
files:

```powershell
git add -u
git commit -m "fix: pass milestone A release gate"
```

Skip this commit when no source file changed.

- [ ] **Step 5: Confirm clean history and create the release tag**

```powershell
git status --short
git log --oneline --decorate v0.1.0..HEAD
git tag -a v0.2.0 -m "Alien Invasion v0.2.0"
git status --short
```

Expected: both status commands produce no output, the log contains the planned
feature/build commits, and `git tag --list v0.2.0` prints `v0.2.0`.

Do not push the branch or tags without separate user authorization.

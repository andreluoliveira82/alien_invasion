from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import unicodedata
from typing import Any


@dataclass(slots=True)
class Profile:
    name: str
    high_score: int = 0
    highest_level: int = 1


class ProfileStoreError(RuntimeError):
    """Report a profile write that the UI can present without crashing."""


class ProfileStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = (
            data_dir
            if data_dir is not None
            else Path(os.environ.get("LOCALAPPDATA", Path.home())) / "AlienInvasion"
        )
        self.path = self.data_dir / "profiles.json"
        self.warning: str | None = None
        self._profiles: dict[str, Profile] = {}
        self._active_key: str | None = None
        self._write_blocked = False
        self._load()

    def list_profiles(self) -> tuple[Profile, ...]:
        return tuple(self._profiles.values())

    def active_profile(self) -> Profile | None:
        return self._profiles.get(self._active_key)

    def create(self, name: str) -> Profile:
        name = self._validate_name(name)
        key = name.casefold()
        if key in self._profiles:
            raise ValueError("Já existe um piloto com esse nome.")
        profile = Profile(name)
        previous_active = self._active_key
        self._profiles[key] = profile
        self._active_key = key
        try:
            self._save()
        except ProfileStoreError:
            del self._profiles[key]
            self._active_key = previous_active
            raise
        return profile

    def select(self, name: str) -> Profile:
        key = name.casefold()
        if key not in self._profiles:
            raise ValueError("Piloto não encontrado.")
        previous_active = self._active_key
        self._active_key = key
        try:
            self._save()
        except ProfileStoreError:
            self._active_key = previous_active
            raise
        return self._profiles[key]

    def update_progress(self, profile: Profile, score: int, level: int) -> bool:
        if self._profiles.get(profile.name.casefold()) is not profile:
            raise ValueError("Piloto não pertence a este armazenamento.")
        if type(score) is not int or score < 0:
            raise ValueError("A pontuação deve ser um inteiro não negativo.")
        if type(level) is not int or level < 1:
            raise ValueError("O nível deve ser um inteiro maior ou igual a 1.")
        previous = profile.high_score, profile.highest_level
        progress = max(profile.high_score, score), max(profile.highest_level, level)
        if progress == previous:
            return False
        profile.high_score, profile.highest_level = progress
        try:
            self._save()
        except ProfileStoreError:
            profile.high_score, profile.highest_level = previous
            raise
        return True

    @staticmethod
    def _validate_name(name: str) -> str:
        name = name.strip()
        if not 1 <= len(name) <= 16:
            raise ValueError("O nome deve ter entre 1 e 16 caracteres.")
        if any(unicodedata.category(character).startswith("C") for character in name):
            raise ValueError("O nome contém um caractere de controle.")
        return name

    @staticmethod
    def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Chave JSON duplicada.")
            result[key] = value
        return result

    def _load(self) -> None:
        try:
            with self.path.open(encoding="utf-8") as source:
                data = json.load(source, object_pairs_hook=self._json_object)
        except FileNotFoundError:
            return
        except OSError:
            self._write_blocked = True
            self.warning = "Não foi possível ler os perfis. O arquivo original foi preservado."
            return
        except (ValueError, RecursionError):
            self._recover_corrupt()
            return
        try:
            self._load_data(data)
        except (KeyError, TypeError, ValueError):
            self._recover_corrupt()

    def _load_data(self, data: Any) -> None:
        if (
            not isinstance(data, dict)
            or type(data["version"]) is not int
            or data["version"] != 1
            or not isinstance(data["profiles"], dict)
        ):
            raise ValueError("Formato de perfis inválido.")
        profiles: dict[str, Profile] = {}
        for display_name, progress in data["profiles"].items():
            name = self._validate_name(display_name)
            key = name.casefold()
            if key in profiles or not isinstance(progress, dict):
                raise ValueError("Perfil inválido.")
            score = progress["high_score"]
            level = progress["highest_level"]
            if type(score) is not int or score < 0 or type(level) is not int or level < 1:
                raise ValueError("Progresso inválido.")
            profiles[key] = Profile(name, score, level)
        active = data["active_profile"]
        if active is not None and (
            not isinstance(active, str) or active.casefold() not in profiles
        ):
            raise ValueError("Piloto ativo inválido.")
        self._profiles = profiles
        self._active_key = active.casefold() if active is not None else None

    def _recover_corrupt(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = self.data_dir / f"profiles-{timestamp}.corrupt.json"
        suffix = 1
        try:
            while backup.exists():
                backup = self.data_dir / f"profiles-{timestamp}-{suffix}.corrupt.json"
                suffix += 1
            self.path.rename(backup)
        except OSError:
            self._write_blocked = True
            self.warning = "Não foi possível preservar os perfis inválidos. O arquivo original foi mantido."
        else:
            self.warning = f"Perfis inválidos preservados em {backup.name}."
        self._profiles = {}
        self._active_key = None

    def _save(self) -> None:
        if self._write_blocked:
            raise ProfileStoreError("Não foi possível salvar sem sobrescrever os perfis originais.")
        active = self.active_profile()
        data = {
            "version": 1,
            "active_profile": active.name if active is not None else None,
            "profiles": {
                profile.name: {
                    "high_score": profile.high_score,
                    "highest_level": profile.highest_level,
                }
                for profile in self._profiles.values()
            },
        }
        temp_path = self.data_dir / "profiles.tmp"
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with temp_path.open("w", encoding="utf-8") as target:
                json.dump(data, target, ensure_ascii=False, indent=2)
                target.flush()
                os.fsync(target.fileno())
            temp_path.replace(self.path)
        except (OSError, TypeError, ValueError) as error:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise ProfileStoreError("Não foi possível salvar os perfis.") from error

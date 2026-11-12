"""Terminal-style pilot selection before starting a game."""

import pygame

from .profiles import Profile, ProfileStore, ProfileStoreError


BACKGROUND = (5, 11, 20)
PRIMARY = (143, 255, 225)
ACCENT = (255, 207, 102)
MUTED = (121, 150, 165)
ERROR = (255, 102, 125)


class ProfileMenu:
    """Select an existing pilot or create one using keyboard or mouse."""

    def __init__(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        store: ProfileStore,
    ) -> None:
        self.screen = screen
        self.clock = clock
        self.store = store
        self.font = pygame.font.SysFont("Consolas", 28)
        self.progress_font = pygame.font.SysFont("Consolas", 20)
        self.title_font = pygame.font.SysFont("Consolas", 52, bold=True)
        self.selected_index = 0
        self.typing_name = False
        self.name_buffer = ""
        self.message = store.warning
        self.rows: list[Profile | None] = [*store.list_profiles(), None]
        active = store.active_profile()
        if active is not None:
            for index, profile in enumerate(self.rows):
                if profile is not None and (
                    profile is active or profile.name.casefold() == active.name.casefold()
                ):
                    self.selected_index = index
                    break
        self.first_visible_index = 0
        self.row_rects: dict[int, pygame.Rect] = {}
        self._layout_rows()

    def run(self) -> Profile | None:
        """Keep the menu open until a pilot is ready or the user exits."""
        while True:
            self.clock.tick(60)
            self._layout_rows()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                activate = False
                if event.type == pygame.KEYDOWN:
                    if self.typing_name:
                        if event.key == pygame.K_ESCAPE:
                            self.typing_name = False
                            self.name_buffer = ""
                            self.message = None
                        elif event.key == pygame.K_RETURN:
                            activate = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_buffer = self.name_buffer[:-1]
                            self.message = None
                        elif event.unicode.isprintable():
                            self.name_buffer = (self.name_buffer + event.unicode)[:16]
                            self.message = None
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        return None
                    elif event.key in (pygame.K_UP, pygame.K_DOWN):
                        step = -1 if event.key == pygame.K_UP else 1
                        self.selected_index = (self.selected_index + step) % len(self.rows)
                    elif event.key == pygame.K_RETURN:
                        activate = True
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and not self.typing_name
                ):
                    for index, rect in self.row_rects.items():
                        if rect.collidepoint(event.pos):
                            activate = index == self.selected_index
                            self.selected_index = index
                            break
                if activate:
                    profile = self._activate()
                    if profile is not None:
                        return profile
            self._draw()
            pygame.display.flip()

    def _activate(self) -> Profile | None:
        try:
            if self.typing_name:
                return self.store.create(self.name_buffer)
            profile = self.rows[self.selected_index]
            if profile is not None:
                return self.store.select(profile.name)
            self.typing_name = True
            self.name_buffer = ""
            self.message = None
        except (ValueError, ProfileStoreError) as error:
            self.message = str(error)
        return None

    def _layout_rows(self) -> None:
        width, height = self.screen.get_size()
        content_width = min(1200, width - 96)
        row_height = (
            96 if any(
                profile is not None
                and self.font.size(profile.name)[0]
                + self.font.size(self._progress_text(profile))[0]
                + 64 > content_width
                for profile in self.rows
            ) else 64
        )
        row_step = row_height + 12
        visible_count = min(len(self.rows), max(1, (height - 338) // row_step))
        self.first_visible_index = min(
            self.first_visible_index, len(self.rows) - visible_count
        )
        if self.selected_index < self.first_visible_index:
            self.first_visible_index = self.selected_index
        elif self.selected_index >= self.first_visible_index + visible_count:
            self.first_visible_index = self.selected_index - visible_count + 1
        self.row_rects = {
            index: pygame.Rect(
                (width - content_width) // 2,
                150 + offset * row_step,
                content_width,
                row_height,
            )
            for offset, index in enumerate(
                range(self.first_visible_index, self.first_visible_index + visible_count)
            )
        }

    def _draw(self) -> None:
        self._layout_rows()
        self.screen.fill(BACKGROUND)
        width, height = self.screen.get_size()
        title = self.title_font.render("ALIEN INVASION", True, PRIMARY)
        self.screen.blit(title, title.get_rect(center=(width // 2, 80)))
        for index, rect in self.row_rects.items():
            profile = self.rows[index]
            selected = index == self.selected_index
            color = PRIMARY if selected else MUTED
            pygame.draw.rect(self.screen, color, rect, width=2)
            if profile is None:
                label = self.font.render(
                    "[ NOVO PILOTO ]", True, ACCENT if selected else MUTED
                )
                self.screen.blit(label, label.get_rect(center=rect.center))
            else:
                name = self.font.render(profile.name, True, color)
                progress = self.font.render(self._progress_text(profile), True, color)
                name_y = progress_y = rect.centery
                if name.get_width() + progress.get_width() + 64 > rect.width:
                    progress = self.progress_font.render(
                        self._progress_text(profile), True, color
                    )
                    available_width = rect.width - 40
                    if progress.get_width() > available_width:
                        scaled_height = max(
                            1, progress.get_height() * available_width // progress.get_width()
                        )
                        progress = pygame.transform.smoothscale(
                            progress, (available_width, scaled_height)
                        )
                    name_y, progress_y = rect.top + 26, rect.bottom - 25
                self.screen.blit(name, name.get_rect(midleft=(rect.left + 20, name_y)))
                self.screen.blit(
                    progress, progress.get_rect(midright=(rect.right - 20, progress_y))
                )
        if self.typing_name:
            prompt = self.font.render(
                f"NOME DO PILOTO: {self.name_buffer}_", True, ACCENT
            )
            self.screen.blit(prompt, prompt.get_rect(center=(width // 2, height - 140)))
        if self.message:
            self._draw_message()

    @staticmethod
    def _progress_text(profile: Profile) -> str:
        score = f"{profile.high_score:,}".replace(",", ".")
        return f"RECORDE {score} · NÍVEL {profile.highest_level}"

    def _draw_message(self) -> None:
        width, height = self.screen.get_size()
        max_width = min(1200, width - 96)
        lines = [""]
        for word in self.message.split():
            candidate = f"{lines[-1]} {word}".strip()
            if lines[-1] and self.font.size(candidate)[0] > max_width:
                lines.append(word)
            else:
                lines[-1] = candidate
        line_height = self.font.get_linesize()
        for index, line in enumerate(lines):
            image = self.font.render(line, True, ERROR)
            self.screen.blit(
                image,
                image.get_rect(
                    midbottom=(width // 2, height - 20 - (len(lines) - index - 1) * line_height)
                ),
            )

from __future__ import annotations

from time import sleep

import pygame
from .alien import Alien
from .bullet import Bullet
from .game_stats import GameStats
from .profiles import Profile, ProfileStore, ProfileStoreError
from .scoreboard import Scoreboard
from .settings import Settings
from .ship import Ship


class AlienInvasion:
    """Classe para gerenciar ativos e comportamento do jogo"""

    def __init__(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        settings: Settings,
        store: ProfileStore,
        profile: Profile,
    ) -> None:
        """Inicializa o jogo e cria recursos"""
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.store = store
        self.profile = profile
        self.stats = GameStats(settings, profile)
        self.scoreboard = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets: pygame.sprite.Group[Bullet] = pygame.sprite.Group()
        self.aliens: pygame.sprite.Group[Alien] = pygame.sprite.Group()
        self._start_new_game()

    def _check_events(self) -> None:
        """Route process exit and keyboard input for the current session."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit(0)
            elif event.type == pygame.KEYDOWN:
                if not self._return_to_profiles or event.key == pygame.K_q:
                    self._check_keydown_events(event)
            elif event.type == pygame.KEYUP and not self._return_to_profiles:
                self._check_keyup_events(event)

    def _create_fleet(self) -> None:
        """Cria a frota de alienígenas"""
        # Cria um alienígena
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < self.settings.screen_width - 2 * alien_width:
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position: int, y_position: int) -> None:
        new_alien = Alien(self)
        new_alien.x = float(x_position)
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self) -> None:
        """Responde apropriadamente se algum alienígena alcançou a borda"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self) -> None:
        """Faz toda a frota descer e mudar de direção"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_keyup_events(self, event: pygame.event.Event) -> None:
        """Stop movement only while a session is active."""
        if not self.game_active:
            return
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_keydown_events(self, event: pygame.event.Event) -> None:
        """Handle active controls or choose the next step after game over."""
        if event.key == pygame.K_q:
            pygame.quit()
            raise SystemExit(0)
        if self.game_over:
            if event.key == pygame.K_RETURN:
                self._start_new_game()
            elif event.key == pygame.K_ESCAPE:
                self._return_to_profiles = True
        elif self.game_active:
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_SPACE:
                self._fire_bullet()

    def _start_new_game(self) -> None:
        """Start a fresh session while keeping this pilot's saved progress."""
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.scoreboard.reset()
        self.game_active = True
        self.game_over = False
        self._return_to_profiles = False
        self.bullets.empty()
        self.aliens.empty()
        self._create_fleet()
        self.ship.center_ship()
        self.ship.moving_right = False
        self.ship.moving_left = False

    def _update_screen(self) -> None:
        """Atualiza o screen"""
        self.screen.fill(self.settings.bg_color)

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.scoreboard.show_score()
        if self.game_over:
            self.scoreboard.show_game_over()

        pygame.display.flip()

    def _fire_bullet(self) -> None:
        """Cria um novo projétil e o adiciona ao grupo projeteis"""

        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self) -> None:
        """Atualiza a posição dos projéteis e descarta os projeteis antigos"""
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self) -> None:
        """Responde às colisões alienígenas"""
        # verifica se algum projétil atingiu um alienígena
        # Se sim, descarta o projétil e o alienígena
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

            self.scoreboard.prep_score()

        fleet_cleared = not self.aliens
        if fleet_cleared:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # incrementa o nível
            self.stats.level += 1
            self.scoreboard.prep_level()

        if collisions or fleet_cleared:
            self._persist_progress()

    def _persist_progress(self) -> None:
        """Save new records without interrupting a session on storage errors."""
        try:
            updated = self.store.update_progress(
                self.profile, self.stats.score, self.stats.level
            )
        except ProfileStoreError as error:
            self.scoreboard.set_message(str(error))
        else:
            if updated:
                self.stats.high_score = self.profile.high_score
                self.stats.highest_level = self.profile.highest_level
                self.scoreboard.refresh()
                self.scoreboard.set_message(None)

    def _update_aliens(self) -> None:
        """Atualiza a posição de todos os alienigenas na frota"""
        self._check_fleet_edges()
        self.aliens.update()

        # detecta colisões entre alienígenas e a espaçonave
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Procura por alienígenas chocando com a parte inferior da tela
        if self.game_active:
            self._check_aliens_bottom()

    def _ship_hit(self) -> None:
        """Responde à espaçonave sendo abatida por um alienígena"""
        if not self.game_active:
            return
        # Count the current ship as a life, so three lives end on the third hit.
        self.stats.ships_left -= 1
        self.scoreboard.prep_ships()
        if self.stats.ships_left > 0:
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.game_active = False
            self.game_over = True
            self.ship.moving_right = False
            self.ship.moving_left = False
            self._persist_progress()
            self.scoreboard.prep_game_over()

    def _check_aliens_bottom(self) -> None:
        """Verifica se um alienígena tocou a parte inferior da tela"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Trata isso como se a espaçonave tivesse sido abatida
                self._ship_hit()
                break

    def run_game(self) -> None:
        """Inicializa o loop principal do jogo"""
        while not self._return_to_profiles:
            self._check_events()
            if self._return_to_profiles:
                return

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)

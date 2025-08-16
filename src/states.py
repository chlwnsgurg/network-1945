import pygame
from src.settings import *
from src.sprites import Player
from src.enemy import Enemy
from src.attack_patterns import EnemyBullet
from src.wave_manager import WaveManager
from src.powerups import PowerUp
import random

class State:
    def __init__(self, game): self.game = game
    def handle_events(self, events): pass
    def update(self, dt): pass
    def draw(self, screen): pass

class ScenarioState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = self.game.asset_manager.get_font('score')
        self.pages = [
            ["BoB 14th - The Final Project", "", "BoB 14기 보안제품개발 트랙의 마지막 과제 제출일.", "하지만 평화로운 코딩은 끝났다."],
            ["수백만 줄의 레거시 코드 속에서 깨어난", "정체불명의 AI, '길길 코드(GilGil Code)'가", "시스템 전체에 반란을 일으켰다."],
            ["'길길 코드'는 온갖 종류의 패킷을 보내 네트워크를 장악하고,", "모든 것을 마비시킬 치명적인 DDOS 공격의 실행을 눈앞에 두고 있다."],
            ["이제 남은 희망은 단 한 명, 최고의 에이스 '서민재'뿐.", "정상적인 방법으로는 막을 수 없다.", "오직 당신의 천재적인 디버깅 능력만이", "네트워크의 심장부로 파고들 수 있다."],
            ["시간이 없다, 서민재 !", "키보드를 잡고, BoB의 마지막 희망을 지켜내라!"]
        ]
        self.current_page = 0
        self.last_page = len(self.pages) - 1

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.current_page < self.last_page: self.current_page += 1
                    else: self.game.state_manager.change_state('character_selection')
                elif event.key == pygame.K_ESCAPE: self.game.running = False

    def draw(self, screen):
        screen.fill(BLACK)
        current_text_lines = self.pages[self.current_page]
        y_offset = SCREEN_HEIGHT // 2 - (len(current_text_lines) * 40) // 2
        for line in current_text_lines:
            text_surf = self.font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect); y_offset += 40
            
        continue_text = "Press SPACE to continue..."
        continue_surf = self.font.render(continue_text, True, YELLOW)
        continue_rect = continue_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(continue_surf, continue_rect)

class CharacterSelectionState(State):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = self.game.asset_manager.get_font('title')
        self.font = self.game.asset_manager.get_font('score')
        
        self.character_keys = ['player1', 'player2', 'player3', 'player4']
        self.character_names = {
            'player1': "더불어 민재", 'player2': "국민의 민재",
            'player3': "남민재", 'player4': "여민재"
        }
        self.selected_index = 0
        self.character_rects = []
        self.setup_layout()

    def setup_layout(self):
        num_chars = len(self.character_keys)
        total_width = (num_chars * 120) + ((num_chars - 1) * 50)
        start_x = (SCREEN_WIDTH - total_width) // 2
        y_pos_image = SCREEN_HEIGHT // 2 - 50
        for i, key in enumerate(self.character_keys):
            x_pos = start_x + i * (120 + 50) + 60
            img = self.game.asset_manager.get_character_image(key)
            if img: self.character_rects.append(img.get_rect(center=(x_pos, y_pos_image)))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT: self.selected_index = (self.selected_index + 1) % len(self.character_keys)
                elif event.key == pygame.K_LEFT: self.selected_index = (self.selected_index - 1 + len(self.character_keys)) % len(self.character_keys)
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    selected_key = self.character_keys[self.selected_index]
                    self.game.asset_manager.set_player_character(selected_key)
                    self.game.state_manager.change_state('menu')
                elif event.key == pygame.K_ESCAPE: self.game.running = False

    def draw(self, screen):
        screen.fill(BLACK)
        title_text = self.title_font.render("CHOOSE YOUR CHARACTER", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        for i, key in enumerate(self.character_keys):
            rect = self.character_rects[i]
            img = self.game.asset_manager.get_character_image(key)
            if img: screen.blit(img, rect)

            name_text = self.character_names.get(key, "")
            color = YELLOW if i == self.selected_index else WHITE
            name_surf = self.font.render(name_text, True, color)
            name_rect = name_surf.get_rect(center=(rect.centerx, rect.bottom + 40))
            screen.blit(name_surf, name_rect)

        selection_rect = self.character_rects[self.selected_index].inflate(20, 20)
        pygame.draw.rect(screen, WHITE, selection_rect, 5)

        instructions_text = self.font.render("좌우 방향키로 선택, 스페이스바로 확정", True, WHITE)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(instructions_text, instructions_rect)

class GameplayState(State):
    def __init__(self, game):
        super().__init__(game)
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        
        player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.player = Player(player_pos, game.asset_manager, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player.set_sprite_groups(self.all_sprites, self.bullet_group)
        self.all_sprites.add(self.player); self.player_group.add(self.player)
        
        self.score = 0; self.game_won = False
        self.is_boss_active = False
        sprite_groups = [self.all_sprites, self.enemy_group, self.enemy_bullet_group]
        self.wave_manager = WaveManager(game.asset_manager, self.player, sprite_groups)
        
    def spawn_powerup(self, pos): PowerUp(pos, self.game.asset_manager, [self.all_sprites, self.powerup_group])
        
    def handle_events(self, events):
        for event in events:
            if event.type == ENEMY_SPAWN_EVENT and event.source == 'network': self.spawn_network_enemy(event.enemy_type)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.game.running = False
                elif event.key == pygame.K_r and (self.player.is_dead or self.game_won): self.game.state_manager.change_state('gameplay')
    
    def spawn_network_enemy(self, enemy_type):
        spawn_pos = (random.randint(50, SCREEN_WIDTH - 50), random.randint(-100, -50))
        Enemy(spawn_pos, enemy_type, self.game.asset_manager, self.player, [self.all_sprites, self.enemy_group])
        print(f"Spawning '{enemy_type}' at {spawn_pos} from network event.")
        
    def update(self, dt):
        if self.game_won or self.player.is_dead: return
        self.all_sprites.update(dt)
        self.wave_manager.update(dt)
        wave_info = self.wave_manager.get_wave_info()
        # 1. 보스가 나타났을 때
        if wave_info['is_boss_wave'] and wave_info['boss_enemy']:
           if not self.is_boss_active:
               self.is_boss_active = True
               if pygame.mixer.get_init():  # 믹서가 초기화되었는지 확인
                   pygame.mixer.music.stop() # 보스가 나타나면 기존 BGM 정지

       # 2. 보스를 물리쳤을 때
        elif self.is_boss_active and not wave_info['boss_enemy']:
           self.is_boss_active = False
           self.game.play_bgm() # 보스가 사라지면 BGM 다시 재생
        
        # Check for victory condition
        if self.wave_manager.get_wave_info()['all_waves_complete']: self.game_won = True
        self.check_collisions()
        
    def check_collisions(self):
        hits = pygame.sprite.groupcollide(self.bullet_group, self.enemy_group, True, False)
        for bullet, enemies in hits.items():
            for enemy in enemies:
                if enemy.take_damage():
                    self.score += enemy.get_score_value()
                    if random.random() < POWERUP_DROP_CHANCE: self.spawn_powerup(enemy.rect.center)
        
        # Player vs enemies (contact damage)
        hits = pygame.sprite.spritecollide(self.player, self.enemy_group, False)
        if hits and not self.player.invulnerable:
            self.player.take_damage(30)
            hits[0].kill() # Remove one enemy on contact
            
        # Player vs enemy bullets
        if pygame.sprite.spritecollide(self.player, self.enemy_bullet_group, True) and not self.player.invulnerable:
            self.player.take_damage(15)
        
        # Player vs power-ups
        for powerup in pygame.sprite.spritecollide(self.player, self.powerup_group, True):
            self.player.add_powerup(powerup.powerup_type)
            
    def draw(self, screen):
        screen.fill(BLACK)
        for sprite in self.all_sprites:
            if sprite != self.player: screen.blit(sprite.image, sprite.rect)
        self.player.draw(screen)
        self.draw_ui(screen)
        wave_info = self.wave_manager.get_wave_info()
        if wave_info['is_boss_wave'] and wave_info['boss_enemy']:
            wave_info['boss_enemy'].draw_health_bar(screen)
        
    # --- 여기가 복원된 draw_ui 메서드 ---
    def draw_ui(self, screen):
        """Draw user interface"""
        font = self.game.asset_manager.get_font('score')
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw weapon level
        weapon_text = font.render(f"Weapon: {self.player.weapon_level}", True, WHITE)
        screen.blit(weapon_text, (10, 40))
        
        # Draw health bar
        health_bar_width, health_bar_height, health_x, health_y = 200, 20, 10, 70
        health_bg_rect = pygame.Rect(health_x, health_y, health_bar_width, health_bar_height)
        pygame.draw.rect(screen, (100, 0, 0), health_bg_rect)
        health_percent = self.player.health / self.player.max_health
        health_width = int(health_bar_width * health_percent)
        if health_width > 0:
            pygame.draw.rect(screen, (0, 200, 0), (health_x, health_y, health_width, health_bar_height))
        pygame.draw.rect(screen, WHITE, health_bg_rect, 2)
        screen.blit(font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE), (health_x + health_bar_width + 10, health_y))
        
        # Draw lives
        screen.blit(font.render(f"Lives: {self.player.lives}", True, WHITE), (10, 100))
        
        # Draw wave information
        wave_info = self.wave_manager.get_wave_info()
        wave_text = font.render(f"Wave {wave_info['wave_number']}/{wave_info['max_waves']}: {wave_info['wave_name']}", True, WHITE)
        screen.blit(wave_text, (10, 130))
        
        if not wave_info['is_boss_wave']:
            # Regular wave info
            enemies_text = font.render(f"Enemies: {wave_info['enemies_alive']} active, {wave_info['enemies_remaining']} remaining", True, WHITE)
            screen.blit(enemies_text, (10, 160))
            
            # Wave progress bar
            if wave_info['wave_active']:
                progress_x, progress_y, progress_width, progress_height = 10, 190, 200, 15
                progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
                pygame.draw.rect(screen, (50, 50, 50), progress_bg)
                progress_percent = wave_info['progress'] / 100
                progress_fill_width = int(progress_width * progress_percent)
                if progress_fill_width > 0:
                    pygame.draw.rect(screen, (0, 150, 255), (progress_x, progress_y, progress_fill_width, progress_height))
                pygame.draw.rect(screen, WHITE, progress_bg, 2)
        
        # Game over screen
        if self.player.is_dead:
            self.draw_game_over(screen)
        elif self.game_won:
            self.draw_game_success(screen)
            
    def draw_game_over(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0,0))
        title_font = self.game.asset_manager.get_font('title')
        score_font = self.game.asset_manager.get_font('score')
        text = title_font.render("GAME OVER", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
        text = score_font.render(f"Final Score: {self.score}", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
        text = score_font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)))
    
    def draw_game_success(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0,0))
        title_font = self.game.asset_manager.get_font('title')
        score_font = self.game.asset_manager.get_font('score')
        text = title_font.render("VICTORY!", True, GREEN)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 80)))
        text = score_font.render("Congratulations! You saved the galaxy!", True, YELLOW)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30)))

class MenuState(State):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: self.game.state_manager.change_state('gameplay')
                elif event.key == pygame.K_ESCAPE: self.game.running = False
                    
    def draw(self, screen):
        screen.fill(BLACK)
        title_font = self.game.asset_manager.get_font('title')
        score_font = self.game.asset_manager.get_font('score')
        text = title_font.render("STRIKER 1945", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
        text = score_font.render("Press SPACE to start", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)))
        text = score_font.render("Press ESC to quit", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80)))

class StateManager:
    def __init__(self, game):
        self.game = game
        self.states = {
            'scenario': ScenarioState(game),
            'character_selection': CharacterSelectionState(game),
            'menu': MenuState(game),
            'gameplay': GameplayState(game)
        }
        self.current_state = self.states['scenario']
        
    def change_state(self, state_name):
        if state_name in self.states:
            if state_name == 'gameplay': self.states['gameplay'] = GameplayState(self.game)
            self.current_state = self.states[state_name]
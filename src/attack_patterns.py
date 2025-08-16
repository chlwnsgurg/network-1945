import math
import pygame
from src.settings import *
import random

class AttackPattern:
    """Base class for attack patterns"""
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        self.cooldown = config.get('cooldown', 1.0)
        self.last_attack_time = 0
        self.all_sprites = all_sprites
        self.bullet_group = bullet_group
        self.asset_manager = asset_manager

    def update(self, dt, enemy, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.cooldown * 1000:
            if self.should_attack(enemy, player):
                self.execute_attack(enemy, player)
                self.last_attack_time = current_time
                
    def should_attack(self, enemy, player):
        """Override this to add conditions for when to attack"""
        return True
        
    def execute_attack(self, enemy, player):
        """Override this to implement the actual attack"""
        pass

class NoAttack(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        
    def execute_attack(self, enemy, player):
        pass  # Do nothing

class SingleShotPlayer(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 300)
        
    def execute_attack(self, enemy, player):
        direction = player.pos - enemy.pos
        if direction.magnitude() > 0:
            direction = direction.normalize()
            EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class SingleShotDown(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 300)
        
    def execute_attack(self, enemy, player):
        direction = pygame.math.Vector2(0, 1)
        EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class SpreadShot(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 300)
        self.bullet_count = config.get('bullet_count', 3)
        self.spread_angle = config.get('spread_angle', 15)
        
    def execute_attack(self, enemy, player):
        base_direction = player.pos - enemy.pos if hasattr(self, 'target_player') and getattr(self, 'target_player', True) else pygame.math.Vector2(0, 1)
        if base_direction.magnitude() > 0: base_direction = base_direction.normalize()
            
        for i in range(self.bullet_count):
            angle = -self.spread_angle + (2 * self.spread_angle * i / (self.bullet_count - 1)) if self.bullet_count > 1 else 0
            rotated_dir = base_direction.rotate(angle)
            EnemyBullet(enemy.rect.center, rotated_dir * self.bullet_speed, [self.all_sprites, self.bullet_group])

class CircularShot(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 250)
        self.bullet_count = config.get('bullet_count', 8)
        
    def execute_attack(self, enemy, player):
        angle_step = 360 / self.bullet_count
        for i in range(self.bullet_count):
            direction = pygame.math.Vector2(1, 0).rotate(i * angle_step)
            EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class BurstFire(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 350)
        self.burst_count = config.get('burst_count', 3)
        self.burst_delay = config.get('burst_delay', 0.1)
        self.current_burst, self.burst_timer, self.in_burst = 0, 0, False
        
    def update(self, dt, enemy, player):
        if self.in_burst:
            self.burst_timer += dt
            if self.burst_timer >= self.burst_delay:
                self.execute_single_shot(enemy, player)
                self.current_burst += 1
                self.burst_timer = 0
                if self.current_burst >= self.burst_count: self.in_burst, self.current_burst, self.last_attack_time = False, 0, pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.last_attack_time > self.cooldown * 1000 and self.should_attack(enemy, player):
            self.in_burst, self.burst_timer = True, 0
            
    def execute_single_shot(self, enemy, player):
        direction = player.pos - enemy.pos
        if direction.magnitude() > 0:
            direction = direction.normalize()
            EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group])

class SpreadShotImage(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 300)
        self.bullet_count = config.get('bullet_count', 3)
        self.spread_angle = config.get('spread_angle', 15)
        self.image_key = config.get('image', 'jesus')
        self.sound=self.asset_manager.get_sound('Hallelujah')
        self.sound_channel = None

    def execute_attack(self, enemy, player):
        if self.sound and (self.sound_channel is None or not self.sound_channel.get_busy()):
            self.sound_channel = self.sound.play()
        base_direction = player.pos - enemy.pos
        if base_direction.magnitude() > 0: base_direction = base_direction.normalize()
        for i in range(self.bullet_count):
            angle = -self.spread_angle + (2 * self.spread_angle * i / (self.bullet_count - 1)) if self.bullet_count > 1 else 0
            rotated_dir = base_direction.rotate(angle)
            EnemyBullet(enemy.rect.center, rotated_dir * self.bullet_speed, [self.all_sprites, self.bullet_group], image_key=self.image_key, asset_manager=enemy.asset_manager)
    
    
    def stop(self):
        if self.sound_channel:
            self.sound_channel.stop()


class FastForwardShotImage(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.bullet_speed = config.get('bullet_speed', 300)
        self.image_key = config.get('image', 'tang')
        self.sound = self.asset_manager.get_sound('tangtang')
        self.sound_channel = None

    def execute_attack(self, enemy, player):
        if self.sound and (self.sound_channel is None or not self.sound_channel.get_busy()):
            self.sound_channel = self.sound.play()
        direction = pygame.math.Vector2(0, 1)
        EnemyBullet(enemy.rect.center, direction * self.bullet_speed, [self.all_sprites, self.bullet_group], image_key=self.image_key, asset_manager=enemy.asset_manager)
        if self.sound and (self.sound_channel is None or not self.sound_channel.get_busy()):
            self.sound_channel = self.sound.play()
            
    def stop(self):
        if self.sound_channel:
            self.sound_channel.stop()

class BlueScreenAttack(AttackPattern):
    def __init__(self, config, all_sprites, bullet_group, asset_manager):
        super().__init__(config, all_sprites, bullet_group, asset_manager)
        self.num_points = config.get('num_points', 5)
        self.delay = config.get('delay', 1.0)

    def execute_attack(self, enemy, player):
        for _ in range(self.num_points):
            x, y = random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)
            # --- 수정: player 객체를 WarningPoint에 전달 ---
            WarningPoint((x, y), self.delay, [self.all_sprites], enemy.asset_manager, player)
    def stop(self):
        for point in self.points:
            point.kill()
        self.points.clear()

class WarningPoint(pygame.sprite.Sprite):
    # --- 수정: __init__ 메서드에 player 매개변수 추가 ---
    def __init__(self, pos, delay, groups, asset_manager, player):
        super().__init__(groups)
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.delay = delay * 1000
        self.asset_manager = asset_manager
        self.player = player # 플레이어 객체 저장
        self.is_attack, self.damage_dealt = False, False
        self.attack_duration = 500
        self.sound = self.asset_manager.get_sound('bsod')
        self.sound_played = False

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if not self.is_attack:
            if current_time - self.spawn_time > self.delay:
                self.is_attack = True
                self.image = self.asset_manager.get_image('bsod')
                self.rect = self.image.get_rect(center=self.rect.center)
                self.spawn_time = current_time
                if self.sound and not self.sound_played:
                    self.sound.play()
                    self.sound_played = True
        else:
            # --- 수정: 데미지 처리 로직 추가 ---
            if not self.damage_dealt and self.rect.colliderect(self.player.rect):
                # 플레이어와 충돌했는지 확인하고, 데미지를 한 번만 줌
                self.player.take_damage(40) # 데미지 값 (예: 40)
                self.damage_dealt = True # 데미지를 줬다고 표시
                print("Blue Screen Attack Hit!")

            if current_time - self.spawn_time > self.attack_duration:
                self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos, velocity, groups, image_key=None, asset_manager=None):
        super().__init__(groups)
        self.image = asset_manager.get_image(image_key) if image_key and asset_manager else pygame.Surface((6, 6))
        if not (image_key and asset_manager): self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=pos)
        self.pos, self.velocity = pygame.math.Vector2(self.rect.center), velocity
        
    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()

def create_attack_pattern(config, all_sprites, bullet_group, asset_manager):
    pattern_type = config.get('type', 'none')
    patterns = {
        'none': NoAttack, 'single_shot_player': SingleShotPlayer,
        'single_shot_down': SingleShotDown, 'spread_shot': SpreadShot,
        'circular_shot': CircularShot, 'burst_fire': BurstFire,
        'spread_shot_image': SpreadShotImage, 'fast_forward_shot_image': FastForwardShotImage,
        'blue_screen_attack': BlueScreenAttack
    }
    pattern_class = patterns.get(pattern_type, NoAttack)
    return pattern_class(config, all_sprites, bullet_group, asset_manager)
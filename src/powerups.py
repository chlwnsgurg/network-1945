import pygame
from src.settings import *
import random

POWERUP_SPEED = 100

# Base class for power-up effects
class PowerUpEffect:
    def __init__(self, duration=0):
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

    def is_active(self):
        if self.duration == 0:  # 0 duration means permanent until broken/replaced
            return True
        return pygame.time.get_ticks() - self.start_time < self.duration

    def apply(self, player):
        raise NotImplementedError

    def remove(self, player):
        raise NotImplementedError

    def update(self, player):
        pass # For effects that need continuous updates, like shield visuals

# Specific power-up effect implementations
class RapidFireEffect(PowerUpEffect):
    def __init__(self, duration=20000): # 5 seconds
        super().__init__(duration)
        self.original_delay = None

    def apply(self, player):
        self.original_delay = player.shoot_delay
        player.shoot_delay /= 2

    def remove(self, player):
        player.shoot_delay = self.original_delay

class SpreadShotEffect(PowerUpEffect):
    def __init__(self, duration=10000): # 5 seconds
        super().__init__(duration)

    def apply(self, player):
        player.has_spread_shot = True

    def remove(self, player):
        player.has_spread_shot = False

class EnergyShieldEffect(PowerUpEffect):
    def __init__(self):
        super().__init__(duration=0) # Lasts until broken

    def apply(self, player):
        player.shield_health = 3
        # Load shield image if not already loaded
        if player.shield_image is None:
            shield_img = player.asset_manager.get_image('shield')
            if shield_img:
                # Scale shield to be slightly larger than the player
                new_size = (int(player.rect.width * 1.5), int(player.rect.height * 1.5))
                player.shield_image = pygame.transform.scale(shield_img, new_size)

    def remove(self, player):
        player.shield_health = 0

# Power-up sprite that falls from the screen
class PowerUp(pygame.sprite.Sprite):
    POWERUP_TYPES = ['rapid_fire', 'spread_shot', 'shield']

    def __init__(self, pos, asset_manager, groups):
        super().__init__(groups)
        self.powerup_type = random.choice(self.POWERUP_TYPES)
        
        self.image = asset_manager.get_image(self.powerup_type)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, POWERUP_SPEED)

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
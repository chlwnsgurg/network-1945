import math
import pygame
from src.settings import *

class MovementPattern:
    """Base class for movement patterns"""
    def update(self, dt, enemy):
        pass

class StraightMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 100)
        self.direction = pygame.math.Vector2(config.get('direction_x', 0), config.get('direction_y', 1))
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
    def update(self, dt, enemy):
        enemy.pos += self.direction * self.speed * dt

class SineWaveMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 150)
        self.amplitude = config.get('amplitude', 60)
        self.frequency = config.get('frequency', 2)
        self.initial_x = None
        
    def update(self, dt, enemy):
        if self.initial_x is None:
            self.initial_x = enemy.pos.x
            
        enemy.pos.y += self.speed * dt
        enemy.pos.x = self.initial_x + self.amplitude * math.sin(enemy.age * self.frequency)

class CosineWaveMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 150)
        self.amplitude = config.get('amplitude', 60)
        self.frequency = config.get('frequency', 2)
        self.initial_x = None
        
    def update(self, dt, enemy):
        if self.initial_x is None:
            self.initial_x = enemy.pos.x
            
        enemy.pos.y += self.speed * dt
        enemy.pos.x = self.initial_x + self.amplitude * math.cos(enemy.age * self.frequency)

class DiveMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 120)
        self.dive_y = config.get('dive_y', 100)
        self.dive_speed_multiplier = config.get('dive_speed_multiplier', 1.5)
        self.state = 'down'
        self.direction = None
        
    def update(self, dt, enemy):
        if self.state == 'down':
            enemy.pos.y += self.speed * dt
            if enemy.pos.y >= self.dive_y:
                self.state = 'dive'
                # Aim at where the player is now
                player_pos = enemy.player.pos if hasattr(enemy, 'player') and enemy.player else pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                direction_to_player = player_pos - enemy.pos
                if direction_to_player.magnitude() > 0:
                    self.direction = direction_to_player.normalize()
                else:
                    self.direction = pygame.math.Vector2(0, 1)
        elif self.state == 'dive':
            if self.direction:
                enemy.pos += self.direction * self.speed * self.dive_speed_multiplier * dt

class CircularMovement(MovementPattern):
    def __init__(self, config):
        self.radius = config.get('radius', 80)
        self.angular_speed = config.get('angular_speed', 2)  # radians per second
        self.center_speed = config.get('center_speed', 50)  # speed at which center moves down
        self.center = None
        self.angle = config.get('start_angle', 0)
        
    def update(self, dt, enemy):
        if self.center is None:
            self.center = pygame.math.Vector2(enemy.pos)
            
        # Move the center point down
        self.center.y += self.center_speed * dt
        
        # Update angle
        self.angle += self.angular_speed * dt
        
        # Calculate position on circle
        enemy.pos.x = self.center.x + self.radius * math.cos(self.angle)
        enemy.pos.y = self.center.y + self.radius * math.sin(self.angle)

class ZigZagMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 120)
        self.zigzag_width = config.get('zigzag_width', 100)
        self.zigzag_frequency = config.get('zigzag_frequency', 3)
        self.initial_x = None
        self.direction = 1
        
    def update(self, dt, enemy):
        if self.initial_x is None:
            self.initial_x = enemy.pos.x
            
        enemy.pos.y += self.speed * dt
        
        # Calculate zigzag offset
        time_factor = enemy.age * self.zigzag_frequency
        if math.sin(time_factor) > 0 and self.direction == -1:
            self.direction = 1
        elif math.sin(time_factor) < 0 and self.direction == 1:
            self.direction = -1
            
        enemy.pos.x = self.initial_x + (self.zigzag_width / 2) * self.direction

class BossHoverMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 50)
        self.amplitude = config.get('amplitude', 80)
        self.frequency = config.get('frequency', 0.8)
        self.initial_pos = None
        self.hover_y = 80  # Stay near top of screen
        
    def update(self, dt, enemy):
        if self.initial_pos is None:
            self.initial_pos = pygame.math.Vector2(enemy.pos)
            self.initial_pos.y = self.hover_y
            
        # Gentle horizontal movement
        enemy.pos.x = self.initial_pos.x + self.amplitude * math.sin(enemy.age * self.frequency)
        enemy.pos.y = self.hover_y + 20 * math.sin(enemy.age * self.frequency * 0.5)
        
        # Keep boss on screen
        screen_width = SCREEN_WIDTH
        enemy.pos.x = max(60, min(screen_width - 60, enemy.pos.x))

class BossTeleportMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 80)
        self.teleport_frequency = config.get('teleport_frequency', 4.0)
        self.last_teleport = 0
        self.target_pos = None
        self.moving_to_target = False
        
    def update(self, dt, enemy):
        current_time = enemy.age
        
        # Check if it's time to teleport
        if current_time - self.last_teleport > self.teleport_frequency:
            self.initiate_teleport(enemy)
            self.last_teleport = current_time
            
        # Move towards target position
        if self.moving_to_target and self.target_pos:
            direction = self.target_pos - enemy.pos
            if direction.magnitude() > 5:
                direction = direction.normalize()
                enemy.pos += direction * self.speed * dt
            else:
                self.moving_to_target = False
                
    def initiate_teleport(self, enemy):
        # Choose a new position on screen
        import random
        new_x = random.randint(80, SCREEN_WIDTH - 80)
        new_y = random.randint(50, 150)
        self.target_pos = pygame.math.Vector2(new_x, new_y)
        self.moving_to_target = True

class BossFortressMovement(MovementPattern):
    def __init__(self, config):
        self.speed = config.get('speed', 30)
        self.settled = False
        self.target_y = 100
        
    def update(self, dt, enemy):
        if not self.settled:
            # Move to center top and settle
            target_x = SCREEN_WIDTH // 2
            direction_x = target_x - enemy.pos.x
            direction_y = self.target_y - enemy.pos.y
            
            if abs(direction_x) > 5:
                enemy.pos.x += (direction_x / abs(direction_x)) * self.speed * dt
            if abs(direction_y) > 5:
                enemy.pos.y += (direction_y / abs(direction_y)) * self.speed * dt
            else:
                self.settled = True
        else:
            # Very slow side-to-side movement
            enemy.pos.x += self.speed * 0.5 * math.sin(enemy.age * 0.3) * dt

def create_movement_pattern(config):
    """Factory function to create movement patterns"""
    pattern_type = config.get('type', 'straight')
    
    if pattern_type == 'straight':
        return StraightMovement(config)
    elif pattern_type == 'sine_wave':
        return SineWaveMovement(config)
    elif pattern_type == 'cosine_wave':
        return CosineWaveMovement(config)
    elif pattern_type == 'dive':
        return DiveMovement(config)
    elif pattern_type == 'circular':
        return CircularMovement(config)
    elif pattern_type == 'zigzag':
        return ZigZagMovement(config)
    elif pattern_type == 'boss_hover':
        return BossHoverMovement(config)
    elif pattern_type == 'boss_teleport':
        return BossTeleportMovement(config)
    elif pattern_type == 'boss_fortress':
        return BossFortressMovement(config)
    else:
        # Default to straight movement
        return StraightMovement(config)
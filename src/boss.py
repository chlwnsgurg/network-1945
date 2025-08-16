import pygame
import json
import os
import math
import random
from src.movement_patterns import create_movement_pattern
from src.attack_patterns import create_attack_pattern

class Boss(pygame.sprite.Sprite):
    """Boss enemy with enhanced health, multiple attack phases, and complex patterns"""
    
    def __init__(self, pos, boss_type, asset_manager, player, groups):
        super().__init__(groups)
        
        # Load boss configuration
        self.config = self.load_boss_config(boss_type)
        
        # Core attributes from config
        self.max_health = self.config['health']
        self.health = self.max_health
        self.boss_type = boss_type
        
        # Load sprite (try boss-specific sprite, fallback to scaled enemy sprite)
        asset_key = self.config.get('asset_key', 'boss')
        self.original_image = asset_manager.get_image(asset_key)
        if not self.original_image:
            # Fallback to scaled enemy sprite
            enemy_sprite = asset_manager.get_image('enemy')
            if enemy_sprite:
                # Scale up enemy sprite to make it boss-sized
                scale_factor = self.config.get('scale_factor', 2.0)
                new_size = (int(enemy_sprite.get_width() * scale_factor), 
                           int(enemy_sprite.get_height() * scale_factor))
                self.original_image = pygame.transform.scale(enemy_sprite, new_size)
            else:
                # Last resort: create a colored rectangle
                self.original_image = pygame.Surface((80, 80))
                self.original_image.fill((255, 0, 0))  # Red boss
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=pos)
        
        # Position vector for smooth movement
        self.pos = pygame.math.Vector2(self.rect.center)
        
        # References
        self.player = player
        self.asset_manager = asset_manager
        
        # Get sprite groups for attack patterns
        all_sprites = groups[0] if groups else None
        # enemy_bullet_group을 groups 리스트에서 직접 가져옵니다.
        enemy_bullet_group = groups[2] if len(groups) > 2 else pygame.sprite.Group()

        # Boss-specific attributes
        self.phase = 1
        self.max_phases = self.config.get('phases', 3)
        self.phase_transition_timer = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # Attack patterns for different phases
        self.attack_patterns = []
        for i in range(self.max_phases):
            phase_config = self.config['attack_phases'][i] if i < len(self.config['attack_phases']) else self.config['attack_phases'][-1]
            pattern = create_attack_pattern(phase_config, all_sprites, enemy_bullet_group, self.asset_manager)
            self.attack_patterns.append(pattern)
        # Movement pattern
        self.movement = create_movement_pattern(self.config['movement'])
        
        # Visual effects
        self.flash_timer = 0
        self.entrance_timer = 0
        self.entrance_duration = 2.0  # 2 seconds entrance
        self.is_entering = True
        
        # Internal state
        self.age = 0.0
        
        # Health bar properties
        self.health_bar_width = 200
        self.health_bar_height = 10
        
    def load_boss_config(self, boss_type):
        """Load boss configuration from JSON file"""
        boss_configs = {
            "angry_migam": {
                "health": 1000,
                "asset_key": "migamboss",
                "phases": 3,
                "movement": { "type": "boss_hover" },
                "attack_phases": [
                    { "type": "spread_shot_image", "image": "jesus", "bullet_count": 5, "spread_angle": 30, "cooldown": 1.5 },
                    { "type": "fast_forward_shot_image", "image": "tang", "bullet_speed": 600, "cooldown": 0.5 },
                    { "type": "blue_screen_attack", "num_points": 5, "delay": 1.0, "cooldown": 3.0 }
                ]
            },
            "handsome_gilgil": {
                "health": 1500,
                "asset_key": "gilgilboss",
                "phases": 1,
                "movement": { "type": "boss_hover", "speed": 30, "amplitude": 120 },
                "attack_phases": [
                    { "type": "circular_shot", "bullet_count": 16, "cooldown": 1.0 }
                ]
            }
        }
        
        if boss_type in boss_configs:
            return boss_configs[boss_type]

        config_path = os.path.join('data', 'boss_config.json')
        try:
            with open(config_path, 'r') as f:
                configs = json.load(f)
                return configs.get(boss_type, configs.get('basic', self.get_default_config()))
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_config()

    def get_default_config(self):
        """Default boss configuration"""
        return {
            'health': 500,
            'asset_key': 'boss',
            'scale_factor': 2.0,
            'phases': 3,
            'movement': {
                'type': 'boss_hover',
                'speed': 50
            },
            'attack_phases': [
                {
                    'type': 'rapid_fire',
                    'bullet_speed': 200,
                    'fire_rate': 0.3
                },
                {
                    'type': 'spiral',
                    'bullet_speed': 150,
                    'fire_rate': 0.2
                },
                {
                    'type': 'barrage',
                    'bullet_speed': 250,
                    'fire_rate': 0.1
                }
            ]
        }
    
    def update(self, dt):
        """Update boss state"""
        self.age += dt
        
        # Handle entrance animation
        if self.is_entering:
            self.entrance_timer += dt
            if self.entrance_timer >= self.entrance_duration:
                self.is_entering = False
            # Slow entrance from top
            if self.pos.y < 100:
                self.pos.y += 30 * dt
            return
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Check for phase transitions
        health_percentage = self.health / self.max_health
        target_phase = self.max_phases - int(health_percentage * self.max_phases)
        target_phase = max(1, min(target_phase, self.max_phases))
        
        if target_phase != self.phase:
            self.transition_to_phase(target_phase)
        
        # Update movement
        self.movement.update(dt, self)
        
        # Update attack pattern for current phase
        if self.player and not self.invulnerable:
            current_attack = self.attack_patterns[self.phase - 1]
            current_attack.update(dt, self, self.player)
        
        # Update visual effects
        if self.flash_timer > 0:
            self.flash_timer -= dt
            
        # Update image based on effects
        self.update_visual_effects()
        
        # Update rect from position
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
        # Keep boss on screen
        screen_rect = pygame.display.get_surface().get_rect()
        self.rect.clamp_ip(screen_rect)
        self.pos = pygame.math.Vector2(self.rect.center)
    
    def transition_to_phase(self, new_phase):
        """Transition to a new attack phase"""
        self.attack_patterns[self.phase - 1].stop()  # Stop current attack pattern
        self.phase = new_phase
        self.invulnerable = True
        self.invulnerable_timer = 1.0  # 1 second invulnerability during transition
        self.flash_timer = 1.0
        print(f"Boss entering phase {new_phase}!")
    
    def update_visual_effects(self):
        """Update visual effects like flashing"""
        self.image = self.original_image.copy()
        
        # Flash effect during invulnerability or phase transition
        if self.invulnerable and int(self.age * 10) % 2:
            # Create flash effect by blending with white
            flash_surface = pygame.Surface(self.image.get_size())
            flash_surface.fill((255, 255, 255))
            self.image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_ADD)
    
    def take_damage(self, damage=10):
        """Take damage and return True if boss is destroyed"""
        if self.invulnerable or self.is_entering:
            return False
            
        self.health -= damage
        self.flash_timer = 0.1  # Brief flash when hit
        
        if self.health <= 0:
            for pattern in self.attack_patterns:
                pattern.stop()
            self.kill()
            return True
        return False
    
    def draw_health_bar(self, surface):
        """Draw boss health bar at top of screen"""
        if self.is_entering:
            return
            
        # Calculate position (centered at top of screen)
        screen_width = surface.get_width()
        x = (screen_width - self.health_bar_width) // 2
        y = 20
        
        # Background bar (dark)
        bg_rect = pygame.Rect(x, y, self.health_bar_width, self.health_bar_height)
        pygame.draw.rect(surface, (100, 0, 0), bg_rect)
        
        # Health bar (red to yellow based on health)
        health_percentage = self.health / self.max_health
        health_width = int(self.health_bar_width * health_percentage)
        
        if health_percentage > 0:
            # Color changes from red to yellow as health decreases
            if health_percentage > 0.5:
                color = (255, int(255 * (1 - health_percentage) * 2), 0)  # Red to yellow
            else:
                color = (255, 255, 0)  # Yellow to red
            
            health_rect = pygame.Rect(x, y, health_width, self.health_bar_height)
            pygame.draw.rect(surface, color, health_rect)
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)
        
        # Boss name and phase
        font = pygame.font.Font(None, 24)
        boss_text = f"{self.boss_type.upper()} - Phase {self.phase}"
        text_surface = font.render(boss_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(centerx=screen_width // 2, y=y + self.health_bar_height + 5)
        surface.blit(text_surface, text_rect)
    
    def get_score_value(self):
        """Get the score value for destroying this boss"""
        base_score = 5000
        phase_bonus = (self.max_phases - self.phase + 1) * 1000  # Bonus for defeating in earlier phases
        return base_score + phase_bonus
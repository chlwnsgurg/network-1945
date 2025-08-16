import pygame
import json
import os
import random
from src.enemy import Enemy
from src.boss import Boss
from src.settings import SCREEN_WIDTH

class WaveManager:
    """Manages wave-based enemy spawning and progression"""
    
    def __init__(self, asset_manager, player, sprite_groups):
        self.asset_manager = asset_manager
        self.player = player
        self.sprite_groups = sprite_groups  # [all_sprites, enemy_group, enemy_bullet_group]
        
        # Wave state
        self.current_wave = 1
        self.max_waves = 10  # Total waves to complete the game
        self.wave_active = False
        self.wave_complete = False
        self.all_waves_complete = False  # Victory condition
        self.enemies_spawned = 0
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.spawn_delay = 1000  # Base spawn delay in milliseconds
        
        # Boss battle state
        self.is_boss_wave = False
        self.boss_enemy = None
        
        # Wave transition
        self.wave_transition_timer = 0
        self.wave_transition_duration = 3000  # 3 seconds between waves
        self.in_transition = False
        
        # Wave duration (1 minute per wave)
        self.wave_start_time = 0
        self.wave_duration = 10000  # 10 seconds in milliseconds

        # Current wave configuration
        self.current_wave_config = None
        
        # Load wave configurations
        self.wave_configs = self.load_wave_configs()
        
        # Start first wave
        self.start_wave(1)
        
    def load_wave_configs(self):
        """Load wave configurations from JSON file"""
        config_path = os.path.join('data', 'wave_config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_wave_configs()
            
    def get_default_wave_configs(self):
        """Default wave configurations if file doesn't exist"""
        return {
            "1": {
                "name": "Scout Wave",
                "enemies": {
                    "scout": 8
                },
                "spawn_delay": 1200,
                "spawn_pattern": "random"
            },
            "2": {
                "name": "Fighter Squadron", 
                "enemies": {
                    "fighter": 6,
                    "scout": 6
                },
                "spawn_delay": 1000,
                "spawn_pattern": "random"
            },
            "3": {
                "name": "Heavy Assault",
                "enemies": {
                    "gunship": 4,
                    "fighter": 8,
                    "interceptor": 3
                },
                "spawn_delay": 800,
                "spawn_pattern": "formation"
            },
            "4": {
                "name": "Bomber Wing",
                "enemies": {
                    "bomber": 3,
                    "interceptor": 6,
                    "gunship": 4,
                    "fighter": 6
                },
                "spawn_delay": 700,
                "spawn_pattern": "waves"
            },
            "5": {
                "name": "Elite Forces",
                "enemies": {
                    "bomber": 4,
                    "interceptor": 8,
                    "gunship": 6,
                    "fighter": 10,
                    "scout": 5
                },
                "spawn_delay": 600,
                "spawn_pattern": "mixed"
            }
        }
        
    def start_wave(self, wave_number):
        """Start a specific wave or boss battle"""
        self.current_wave = wave_number
        
        # Check if this is a boss wave (every 5 waves)
        self.is_boss_wave = (wave_number % 5 == 0)
        
        if self.is_boss_wave:
            self.start_boss_battle()
        else:
            self.start_regular_wave(wave_number)
            
    def start_regular_wave(self, wave_number):
        """Start a regular enemy wave"""
        wave_key = str(wave_number)
        
        # Get wave config or generate procedural wave
        if wave_key in self.wave_configs:
            self.current_wave_config = self.wave_configs[wave_key]
        else:
            self.current_wave_config = self.generate_procedural_wave(wave_number)
            
        # Calculate total enemies to spawn
        self.enemies_to_spawn = sum(self.current_wave_config["enemies"].values())
        self.enemies_spawned = 0
        
        # Set spawn timing
        self.spawn_delay = self.current_wave_config.get("spawn_delay", 1000)
        self.spawn_timer = 0
        
        # Start wave
        self.wave_active = True
        self.wave_complete = False
        self.in_transition = False
        self.wave_start_time = pygame.time.get_ticks()
        
    def start_boss_battle(self):
        """Start a boss battle"""
        if pygame.mixer.get_init():  # 믹서가 초기화되었는지 확인
            pygame.mixer.music.stop()  # Stop background music during boss battle
        # Determine boss type based on wave number
        boss_type = self.get_boss_type_for_wave(self.current_wave)
        # Spawn the boss
        spawn_pos = (SCREEN_WIDTH // 2, -50)  # Center top of screen
        self.boss_enemy = Boss(spawn_pos, boss_type, self.asset_manager, self.player, self.sprite_groups)
        
        # Boss wave configuration
        self.current_wave_config = {
            "name": f"Boss Battle - {boss_type.replace('_', ' ').title()}",
            "enemies": {},
            "spawn_delay": 0,
            "spawn_pattern": "boss"
        }
        
        self.enemies_to_spawn = sum(self.current_wave_config["enemies"].values())
        self.enemies_spawned = 0
        
        # Start wave
        self.wave_active = True
        self.wave_complete = False
        self.in_transition = False
        self.wave_start_time = pygame.time.get_ticks()
        
        print(f"Boss battle started! Wave {self.current_wave} - {boss_type}")
        
    def get_boss_type_for_wave(self, wave_number):
        """Determine which boss to spawn based on wave number"""
        if wave_number == 5:
            return "angry_migam"
        elif wave_number == 10:
            return "angry_migam"  # "handsome_gilgil"에서 변경
        else:
            # For other boss waves, cycle through a default list
            boss_types = ["cyber_fortress", "network_overlord", "packet_storm"]
            boss_cycle = (wave_number // 5) - 1
            return boss_types[boss_cycle % len(boss_types)]
        
    def generate_procedural_wave(self, wave_number):
        """Generate a procedural wave for high wave numbers"""
        difficulty_multiplier = min(wave_number / 5.0, 3.0)  # Cap at 3x difficulty
        
        base_enemies = {
            "scout": int(5 * difficulty_multiplier),
            "basic": int(3 * difficulty_multiplier), 
            "fighter": int(4 * difficulty_multiplier),
            "gunship": int(2 * difficulty_multiplier),
            "interceptor": int(2 * difficulty_multiplier),
            "bomber": int(1 * difficulty_multiplier)
        }
        
        return {
            "name": f"Wave {wave_number}",
            "enemies": base_enemies,
            "spawn_delay": max(300, 1000 - (wave_number * 30)),  # Faster spawning
            "spawn_pattern": random.choice(["random", "formation", "waves", "mixed"])
        }
        
    def update(self, dt):
        """Update wave manager"""
        current_time = pygame.time.get_ticks()
        
        if self.in_transition:
            # Handle wave transition
            if current_time - self.wave_transition_timer > self.wave_transition_duration:
                if self.current_wave < self.max_waves:
                    self.start_wave(self.current_wave + 1)
        elif self.wave_active:
            if self.is_boss_wave:
                # Boss battle logic
                if self.boss_enemy and not self.boss_enemy.alive():
                    # Boss defeated
                    self.boss_enemy = None
                    self.complete_wave()
                # Boss battles don't have time limits
            else:
                # Regular wave logic
                if (self.enemies_spawned < self.enemies_to_spawn and 
                    current_time - self.spawn_timer > self.spawn_delay):
                    self.spawn_next_enemy()
                    self.spawn_timer = current_time
                    
                # Check if wave is complete (either all enemies killed or time limit reached)
                wave_time_elapsed = current_time - self.wave_start_time
                if (wave_time_elapsed >= self.wave_duration or 
                    (self.enemies_spawned >= self.enemies_to_spawn and 
                     len(self.sprite_groups[1]) == 0)):  # Time limit or no enemies left
                    self.complete_wave()
                
    def spawn_next_enemy(self):
        """Spawn the next enemy in the current wave"""
        if not self.current_wave_config:
            return
            
        # Choose which enemy type to spawn
        available_enemies = []
        for enemy_type, count in self.current_wave_config["enemies"].items():
            if count > 0:
                available_enemies.extend([enemy_type] * count)
                
        if not available_enemies:
            return
            
        # Select enemy type and reduce count
        enemy_type = random.choice(available_enemies)
        self.current_wave_config["enemies"][enemy_type] -= 1
        
        # Determine spawn position based on pattern
        spawn_pos = self.get_spawn_position(enemy_type)
        
        # Create enemy
        enemy = Enemy(spawn_pos, enemy_type, self.asset_manager, self.player, self.sprite_groups)
        
        self.enemies_spawned += 1
        
    def get_spawn_position(self, enemy_type):
        """Get spawn position based on wave pattern and enemy type"""
        pattern = self.current_wave_config.get("spawn_pattern", "random")
        
        if pattern == "random":
            x = random.randint(50, 750)  # SCREEN_WIDTH - 50
            y = random.randint(-100, -50)
            
        elif pattern == "formation":
            # Spawn in formation from left to right
            formation_spacing = 80
            formation_x = 100 + (self.enemies_spawned % 7) * formation_spacing
            formation_y = -50 - (self.enemies_spawned // 7) * 60
            x = formation_x
            y = formation_y
            
        elif pattern == "waves":
            # Spawn in horizontal waves
            wave_y = -50 - (self.enemies_spawned // 8) * 80
            wave_x = 50 + (self.enemies_spawned % 8) * 90
            x = wave_x
            y = wave_y
            
        elif pattern == "mixed":
            # Mix of patterns
            if self.enemies_spawned % 3 == 0:
                x = random.randint(50, 750)
                y = random.randint(-100, -50)
            else:
                x = 100 + (self.enemies_spawned % 6) * 100
                y = -50
        else:
            # Default to random
            x = random.randint(50, 750)
            y = random.randint(-100, -50)
            
        return (x, y)
        
    def complete_wave(self):
        """Mark current wave as complete and start transition"""
        self.wave_active = False
        self.wave_complete = True
        
        # Check if all waves are complete (victory condition)
        if self.current_wave >= self.max_waves:
            self.all_waves_complete = True
        else:
            self.in_transition = True
            self.wave_transition_timer = pygame.time.get_ticks()
        
    def get_wave_progress(self):
        """Get current wave progress as a percentage based on time elapsed"""
        if not self.wave_active:
            return 100
        current_time = pygame.time.get_ticks()
        wave_time_elapsed = current_time - self.wave_start_time
        return min(100, (wave_time_elapsed / self.wave_duration) * 100)
        
    def get_wave_info(self):
        """Get current wave information for UI display"""
        return {
            "wave_number": self.current_wave,
            "max_waves": self.max_waves,
            "wave_name": self.current_wave_config.get("name", f"Wave {self.current_wave}") if self.current_wave_config else "Wave",
            "enemies_remaining": max(0, self.enemies_to_spawn - self.enemies_spawned),
            "enemies_alive": len(self.sprite_groups[1]) if len(self.sprite_groups) > 1 else 0,
            "progress": self.get_wave_progress(),
            "in_transition": self.in_transition,
            "wave_active": self.wave_active,
            "is_boss_wave": self.is_boss_wave,
            "boss_enemy": self.boss_enemy,
            "all_waves_complete": self.all_waves_complete
        }
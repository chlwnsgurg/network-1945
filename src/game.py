import pygame
import sys
from src.settings import *
from src.asset_manager import AssetManager
from src.states import StateManager
from src.network_monitor import NetworkMonitor  # NetworkMonitor 임포트

class Game:
    def __init__(self):
        # Initialize pygame
        """Initialize the game, display, and assets."""
        try:
            # 사운드 끊김 방지를 위해 pygame.init()보다 먼저 호출합니다.
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
        except pygame.error:
            print("Warning: No audio device available, running without sound")
        
        # Initialize audio (optional - skip if no audio device available)
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Warning: No audio device available, running without sound")
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Striker 1945")
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Asset manager
        self.asset_manager = AssetManager()
        self.asset_manager.load_all()
        
        self.play_bgm() # 배경음악 재생
        
        # State manager
        self.state_manager = StateManager(self)
        
        # --- 네트워크 모니터 시작 ---
        self.network_monitor = NetworkMonitor()
        self.network_monitor.start()
        
# src/game.py

    def play_bgm(self):
       """배경음악을 재생합니다."""
       if not pygame.mixer.get_init():  # 믹서가 초기화되었는지 확인
           return

       bgm_path = self.asset_manager.get_sound('background')
       if bgm_path:
           try:
               pygame.mixer.music.load(bgm_path)
               pygame.mixer.music.set_volume(0.4)
               pygame.mixer.music.play(loops=-1)
           except pygame.error as e:
               print(f"Error playing background music: {e}")

    def run(self):
        """Main game loop"""
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # Update current state
            self.state_manager.current_state.handle_events(events)
            self.state_manager.current_state.update(dt)
            
            # Draw current state
            self.state_manager.current_state.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
            
        # --- 네트워크 모니터 종료 ---
        self.network_monitor.stop()
        
        # Quit
        pygame.quit()
        sys.exit()
# Game constants and settings
import pygame

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_SPEED = 300
PLAYER_SHOOT_DELAY = 200  # milliseconds

# Bullet settings
BULLET_SPEED = 500

# Enemy settings
ENEMY_SPEED = 150
POWERUP_DROP_CHANCE = 0.1  # 10% chance for an enemy to drop a powerup

# Game settings
SCORE_FONT_SIZE = 24

# --- 네트워크 스폰 설정 추가 ---
# Pygame 커스텀 이벤트 정의
ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1

# 패킷 타입과 적 종류 매핑
PACKET_TO_ENEMY_MAP = {
    'tcp': 'interceptor',       # TCP -> 인터셉터 
    'icmp': 'fighter',  # ICMP -> 파이터
    'arp': 'scout',         # ARP -> 스카우트 
    'udp': 'gunship',       # UDP -> 건쉽 
}

# 네트워크 스폰 쿨다운 (초)
NETWORK_SPAWN_COOLDOWN = 1.0
import pygame
import os
import random

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        # 캐릭터 선택 이미지를 저장할 딕셔너리 추가
        self.player_character_images = {}
        
    def load_images(self):
        """Load all game images"""
        image_path = os.path.join('assets', 'images')
        
        if not os.path.exists(image_path):
            os.makedirs(image_path)
            
        # --- 캐릭터 선택 이미지 불러오기 (player1 ~ player4) ---
        for i in range(1, 5): # player1부터 player4까지
            key = f'player{i}'
            try:
                img_path = os.path.join(image_path, f'{key}.png')
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    # 선택 화면에서 보여줄 이미지 크기 조절
                    img = pygame.transform.scale(img, (120, 160))
                    self.player_character_images[key] = img
                else:
                    raise FileNotFoundError(f"{key}.png not found")
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load {key}.png. Creating placeholder. Error: {e}")
                # 이미지가 없을 경우를 대비한 임시 이미지 생성
                placeholder_surf = pygame.Surface((120, 160), pygame.SRCALPHA)
                placeholder_surf.fill((random.randint(50,200), random.randint(50,200), random.randint(50,200)))
                self.player_character_images[key] = placeholder_surf

        # 게임 시작 시 기본 캐릭터 설정
        self.set_player_character('player1')
        
        try:
            if os.path.exists(os.path.join(image_path, 'bullet.png')):
                self.images['bullet'] = pygame.image.load(os.path.join(image_path, 'bullet.png')).convert_alpha()
            else:
                raise FileNotFoundError()
        except (pygame.error, FileNotFoundError):
            bullet_surf = pygame.Surface((4, 12), pygame.SRCALPHA)
            bullet_surf.fill((255, 255, 0))
            self.images['bullet'] = bullet_surf
            
        try:
            if os.path.exists(os.path.join(image_path, 'enemy.png')):
                self.images['enemy'] = pygame.image.load(os.path.join(image_path, 'enemy.png')).convert_alpha()
            else:
                raise FileNotFoundError()
        except (pygame.error, FileNotFoundError):
            enemy_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(enemy_surf, (255, 0, 0), (12, 12), 12)
            self.images['enemy'] = enemy_surf
            
        enemy_types = {
            'enemy_scout': (20, 20, (255, 165, 0)),
            'enemy_fighter': (28, 28, (255, 100, 100)),
            'enemy_gunship': (32, 24, (128, 128, 255)),
            'enemy_interceptor': (24, 16, (255, 255, 100)),
            'enemy_bomber': (36, 32, (128, 255, 128))
        }
        
        for enemy_key, (width, height, color) in enemy_types.items():
            try:
                if os.path.exists(os.path.join(image_path, f'{enemy_key}.png')):
                    img = pygame.image.load(os.path.join(image_path, f'{enemy_key}.png')).convert_alpha()
                    scale_factor = 0.1
                    new_size = (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
                    img = pygame.transform.smoothscale(img, new_size)
                    self.images[enemy_key] = img
                else:
                    raise FileNotFoundError()
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                if 'scout' in enemy_key:
                    points = [(width//2, 0), (0, height), (width, height)]
                    pygame.draw.polygon(surf, color, points)
                elif 'fighter' in enemy_key:
                    points = [(width//2, 0), (width, height//2), (width//2, height), (0, height//2)]
                    pygame.draw.polygon(surf, color, points)
                else:
                    pygame.draw.circle(surf, color, (width//2, height//2), min(width, height)//2)
                self.images[enemy_key] = surf
        
        try:
            if os.path.exists(os.path.join(image_path, 'migamboss.png')):
                img = pygame.image.load(os.path.join(image_path, 'migamboss.png')).convert_alpha()
                scale_factor = 0.3
                new_size = (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
                img = pygame.transform.smoothscale(img, new_size)
                self.images['migamboss'] = img
            else:
                boss_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(boss_surf, (255, 0, 255), (30, 30), 30)
                self.images['migamboss'] = boss_surf
        except (pygame.error, FileNotFoundError):
            boss_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(boss_surf, (255, 0, 255), (30, 30), 30)
            self.images['migamboss'] = boss_surf
            
        custom_images = {'jesus': (100, 100, (255, 255, 255)), 'tang': (50, 50, (255, 100, 100)), 'bsod': (100, 100, (0, 0, 255))}
        for key, (width, height, color) in custom_images.items():
            try:
                img_path = os.path.join(image_path, f"{key}.png")
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    if key == "tang":
                        scale_factor = 0.35
                    elif key == "jesus":
                        scale_factloador = 0.5
                    elif key == "bsod":
                        scale_factor = 0.4
                    w, h = img.get_size()
                    new_size = (int(w * scale_factor), int(h * scale_factor))
                    img = pygame.transform.scale(img, new_size)
                    self.images[key] = img
                else:
                    raise FileNotFoundError()
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                surf.fill(color)
                self.images[key] = surf

        powerup_images = {'shield': (32, 32, (0, 191, 255)), 'rapid_fire': (32, 32, (255, 215, 0)), 'spread_shot': (32, 32, (148, 0, 211))}
        for key, (width, height, color) in powerup_images.items():
            try:
                img_path = os.path.join(image_path, f"{key}.png")
                if os.path.exists(img_path):
                    self.images[key] = pygame.image.load(img_path).convert_alpha()
                else:
                    raise FileNotFoundError()
            except (pygame.error, FileNotFoundError):
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                if key == 'shield':
                    pygame.draw.circle(surf, color, (width//2, height//2), width//2, 3)
                elif key == 'rapid_fire':
                    pygame.draw.polygon(surf, color, [(16, 2), (8, 16), (14, 16), (6, 30), (24, 14), (18, 14)])
                elif key == 'spread_shot':
                    pygame.draw.circle(surf, color, (width//2, 8), 4)
                    pygame.draw.circle(surf, color, (8, 24), 4)
                    pygame.draw.circle(surf, color, (width - 8, 24), 4)
                self.images[key] = surf
    def load_sounds(self):
        """Load all sound files."""
        sound_path = os.path.join('assets', 'sounds')
        
        if not os.path.exists(sound_path):
            os.makedirs(sound_path)

        # 배경음악(BGM) 로드 (경로로 저장)
        try:
            bgm_path = os.path.join(sound_path, 'bgm.mp3')
            if os.path.exists(bgm_path):
                self.sounds['background'] = bgm_path
        except Exception as e:
            print(f"Error loading background music path: {e}")

        # 효과음(SFX) 로드 (Sound 객체로 저장)
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion': 'explosion.wav',
            'hallelujah': 'Hallelujah.mp3',
            'tangtang': 'tangtang.mp3',
            'bsod': 'BSOD.mp3'
        }
        for key, filename in sound_files.items():
            try:
                file_path = os.path.join(sound_path, filename)
                if os.path.exists(file_path):
                    sound = pygame.mixer.Sound(file_path)
                    
                    # 개별 사운드 볼륨 조절
                    if key == 'tangtang':
                        sound.set_volume(0.3)
                    elif key == 'hallelujah':
                        sound.set_volume(1.2)
                        
                    self.sounds[key] = sound
                else:
                    # 파일이 없을 경우 None으로 설정
                    self.sounds[key] = None
            except pygame.error as e:
                print(f"Error loading sound {filename}: {e}")
                self.sounds[key] = None
            
    def load_fonts(self):
        font_path = os.path.join('assets', 'fonts')
        if not os.path.exists(font_path): os.makedirs(font_path)
        korean_font_path = os.path.join(font_path, 'NanumGothic.ttf')
        try:
            if not os.path.exists(korean_font_path): raise FileNotFoundError("NanumGothic.ttf not found in assets/fonts/")
            self.fonts['score'] = pygame.font.Font(korean_font_path, 24)
            self.fonts['title'] = pygame.font.Font(korean_font_path, 48)
            print(f"성공: 한글 폰트를 불러왔습니다: {korean_font_path}")
        except (pygame.error, FileNotFoundError) as e:
            print(f"경고: 한글 폰트를 불러올 수 없습니다. {e}\n기본 폰트를 사용합니다. (한글이 깨질 수 있습니다)")
            self.fonts['score'] = pygame.font.Font(None, 24)
            self.fonts['title'] = pygame.font.Font(None, 48)
        
    def load_all(self):
        self.load_images(); self.load_sounds(); self.load_fonts()
        
    def get_image(self, key): return self.images.get(key)
    def get_sound(self, key): return self.sounds.get(key)
    def get_font(self, key): return self.fonts.get(key)
        
    def play_sound(self, key):
        sound = self.sounds.get(key)
        if sound: sound.play()
            
    def set_player_character(self, character_key):
        """선택된 캐릭터 이미지를 실제 플레이어 이미지로 설정합니다."""
        image_path = os.path.join('assets', 'images')
        original_image = None
        try:
            # 원본 이미지 경로 설정 (player1은 player.png 시도, 나머지는 이름 그대로)
            png_name = 'player.png' if character_key == 'player1' else f'{character_key}.png'
            img_path = os.path.join(image_path, png_name)
            if os.path.exists(img_path):
                original_image = pygame.image.load(img_path).convert_alpha()
            else:
                raise FileNotFoundError
        except (pygame.error, FileNotFoundError):
             # 이미지 로드 실패 시, 미리 로드된 placeholder 사용
             original_image = self.player_character_images[character_key]

        # 실제 게임 플레이에 사용될 크기로 최종 조절
        game_size = (60, 80) 
        self.images['player'] = pygame.transform.scale(original_image, game_size)
        print(f"플레이어 캐릭터가 '{character_key}'로 설정되었습니다.")

    def get_character_image(self, key):
        """캐릭터 선택 화면을 위한 이미지를 가져옵니다."""
        return self.player_character_images.get(key)
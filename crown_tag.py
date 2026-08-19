import sys
import math
import pygame
import os
import random

# --- INITIALIZATION & CONSTANTS ---
pygame.init()

WIDTH, HEIGHT = 610, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King of the Crown")
clock = pygame.time.Clock()
FPS = 60

# Colors
COLOR_BG = (118, 198, 88)
COLOR_GRASS_DARK = (88, 168, 62)
COLOR_GRASS_LIGHT = (148, 222, 112)
COLOR_ROOF = (195, 88, 60)
COLOR_ROOF_DARK = (145, 55, 35)
COLOR_ROOF_LIGHT = (225, 115, 85)
COLOR_ROOF_EDGE = (110, 40, 25)
COLOR_WALL = (244, 219, 161)
COLOR_WATER = (91, 160, 226)
COLOR_POOL_RIM = (230, 210, 190)
COLOR_BRIDGE = (180, 180, 160)
COLOR_MUD = (110, 70, 35)
COLOR_MUD_DARK = (75, 45, 20)
COLOR_MUD_LIGHT = (135, 85, 45)
COLOR_P1 = (0, 150, 255)       # Blue player shirt
COLOR_P2 = (230, 60, 60)        # Red player shirt
COLOR_SKIN = (240, 195, 150)
COLOR_HAIR_1 = (40, 30, 20)     # Dark Hair
COLOR_HAIR_2 = (200, 150, 60)   # Blonde Hair
COLOR_CROWN = (255, 215, 0)
COLOR_CROWN_GEM = (220, 20, 60)
COLOR_WHITE = (255, 255, 255)
COLOR_BTN_NORMAL = (40, 40, 50)
COLOR_BTN_HOVER = (70, 70, 90)

# Boost Colors
COLOR_BOOST_BLUE = (0, 180, 255)
COLOR_BOOST_GLOW = (0, 180, 255, 60)
COLOR_BOOST_THUNDER = (255, 240, 0)

# Game Rules
WIN_TIME = 20.0
STEAL_COOLDOWN_TIME = 0.8
NORMAL_SPEED = 4.2
MUD_SPEED = 1.9
BOOST_DURATION = 4.0
BOOST_MULTIPLIER = 1.5

# Game States
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"

# --- AUDIO LOAD ---
try:
    sound_path = os.path.join("sounds", "bg_music.mp3")
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
except Exception as e:
    print("Could not load background music:", e)

# --- MAP ENVIRONMENT DATA ---

def get_grass_tufts(width, height, count=160, seed=101):
    random.seed(seed)
    tufts = []
    for _ in range(count):
        gx = random.randint(25, width - 25)
        gy = random.randint(25, height - 25)
        tufts.append((gx, gy))
    return tufts

GRASS_TUFTS = get_grass_tufts(WIDTH, HEIGHT)

def get_mud_patches():
    return [
        {
            "cx": 180, "cy": 370, "r": 38,
            "blobs": [
                (180, 370, 34), (165, 365, 24), (195, 375, 24), 
                (180, 355, 22), (175, 382, 22)
            ]
        },
        {
            "cx": 470, "cy": 220, "r": 42,
            "blobs": [
                (470, 220, 38), (450, 215, 26), (490, 225, 28), 
                (475, 205, 24), (465, 238, 24)
            ]
        },
        {
            "cx": 300, "cy": 540, "r": 36,
            "blobs": [
                (300, 540, 32), (285, 535, 22), (315, 545, 24), 
                (300, 525, 20), (295, 552, 20)
            ]
        },
        {
            "cx": 300, "cy": 170, "r": 36,
            "blobs": [
                (300, 540, 32), (285, 535, 22), (315, 545, 24), 
                (300, 525, 20), (295, 552, 20)
            ]
        }
    ]

def get_static_obstacles():
    return [
        pygame.Rect(0, 80, 180, 140),
        pygame.Rect(0, 220, 80, 60),
        pygame.Rect(410, 370, 65, 160),
        pygame.Rect(515, 370, 65, 160)
    ]

# --- CLASSES ---

class Lawnmower:
    def __init__(self, x_min, x_max, y):
        self.x = x_min
        self.y = y
        self.width = 30
        self.height = 40
        self.x_min = x_min
        self.x_max = x_max
        self.speed = 2.0
        self.direction = 1

    def update(self):
        self.x += self.speed * self.direction
        if self.x >= self.x_max or self.x <= self.x_min:
            self.direction *= -1

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        mower_rect = self.get_rect()
        
        # Main Body
        pygame.draw.rect(surface, (210, 40, 40), mower_rect, border_radius=6)
        pygame.draw.rect(surface, (120, 20, 20), mower_rect, width=2, border_radius=6)
        
        # Engine Deck Cover
        engine_rect = pygame.Rect(mower_rect.x + 4, mower_rect.y + 10, mower_rect.width - 8, mower_rect.height - 20)
        pygame.draw.rect(surface, (40, 40, 40), engine_rect, border_radius=3)
        pygame.draw.circle(surface, (80, 80, 80), engine_rect.center, 5)
        
        # Wheels
        wheel_w, wheel_h = 4, 10
        pygame.draw.rect(surface, (10, 10, 10), (mower_rect.x - 2, mower_rect.y + 4, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surface, (10, 10, 10), (mower_rect.right - 2, mower_rect.y + 4, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surface, (10, 10, 10), (mower_rect.x - 2, mower_rect.bottom - 14, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surface, (10, 10, 10), (mower_rect.right - 2, mower_rect.bottom - 14, wheel_w, wheel_h), border_radius=2)

        # Handlebar Bar and Grip
        if self.direction == 1:
            pygame.draw.line(surface, (60, 60, 60), (mower_rect.x, mower_rect.y + 10), (mower_rect.x - 10, mower_rect.y + 10), 3)
            pygame.draw.line(surface, (60, 60, 60), (mower_rect.x, mower_rect.bottom - 10), (mower_rect.x - 10, mower_rect.bottom - 10), 3)
            pygame.draw.line(surface, (20, 20, 20), (mower_rect.x - 10, mower_rect.y + 8), (mower_rect.x - 10, mower_rect.bottom - 8), 4)
        else:
            pygame.draw.line(surface, (60, 60, 60), (mower_rect.right, mower_rect.y + 10), (mower_rect.right + 10, mower_rect.y + 10), 3)
            pygame.draw.line(surface, (60, 60, 60), (mower_rect.right, mower_rect.bottom - 10), (mower_rect.right + 10, mower_rect.bottom - 10), 3)
            pygame.draw.line(surface, (20, 20, 20), (mower_rect.right + 10, mower_rect.y + 8), (mower_rect.right + 10, mower_rect.bottom - 8), 4)


class SpeedBoost:
    def __init__(self, mud_patches):
        self.radius = 14
        self.active = False
        self.x = 0
        self.y = 0
        self.respawn_timer = random.uniform(2.0, 5.0)
        self.mud_patches = mud_patches

    def is_valid_position(self, px, py):
        if px < 35 or px > WIDTH - 35 or py < 45 or py > HEIGHT - 45:
            return False

        house_rect = pygame.Rect(0, 70, 200, 220)
        if house_rect.collidepoint(px, py):
            return False

        pool_rect = pygame.Rect(400, 360, 190, 180)
        if pool_rect.collidepoint(px, py):
            return False

        for p in self.mud_patches:
            if math.hypot(px - p["cx"], py - p["cy"]) < (self.radius + p["r"] + 10):
                return False

        return True

    def spawn(self):
        for _ in range(100):
            tx = random.randint(40, WIDTH - 40)
            ty = random.randint(50, HEIGHT - 50)
            if self.is_valid_position(tx, ty):
                self.x = tx
                self.y = ty
                self.active = True
                break

    def update(self, dt):
        if not self.active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.spawn()

    def draw(self, surface):
        if not self.active:
            return

        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, COLOR_BOOST_GLOW, (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow_surf, (self.x - self.radius * 2, self.y - self.radius * 2))

        pygame.draw.circle(surface, COLOR_BOOST_BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.x), int(self.y)), self.radius, width=2)

        thunder_pts = [
            (self.x + 2, self.y - 8),
            (self.x - 5, self.y + 1),
            (self.x + 1, self.y + 1),
            (self.x - 2, self.y + 8),
            (self.x + 5, self.y - 1),
            (self.x - 1, self.y - 1)
        ]
        pygame.draw.polygon(surface, COLOR_BOOST_THUNDER, thunder_pts)

    def trigger_pickup(self):
        self.active = False
        self.respawn_timer = random.uniform(5.0, 10.0)


class Player:
    def __init__(self, x, y, color, hair_color, controls, initial_angle=0):
        self.start_x = x
        self.start_y = y
        self.initial_angle = initial_angle
        self.shirt_color = color
        self.hair_color = hair_color
        self.controls = controls
        self.radius = 16
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.speed = NORMAL_SPEED
        self.has_crown = False
        self.hold_time = 0.0
        self.angle = self.initial_angle
        self.boost_timer = 0.0

    def handle_input(self, keys, obstacles, mud_patches, boost, dt):
        if self.boost_timer > 0:
            self.boost_timer -= dt

        in_mud = any(math.hypot(self.x - p["cx"], self.y - p["cy"]) < (self.radius + p["r"]) for p in mud_patches)
        base_spd = MUD_SPEED if in_mud else NORMAL_SPEED
        self.speed = base_spd * (BOOST_MULTIPLIER if self.boost_timer > 0 else 1.0)

        dx, dy = 0, 0
        if keys[self.controls['up']]:    dy -= 1
        if keys[self.controls['down']]:  dy += 1
        if keys[self.controls['left']]:  dx -= 1
        if keys[self.controls['right']]: dx += 1

        if dx != 0 or dy != 0:
            self.angle = math.degrees(math.atan2(-dy, dx))
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

        min_bounds_x = 20 + self.radius
        max_bounds_x = WIDTH - 20 - self.radius
        min_bounds_y = 20 + self.radius
        max_bounds_y = HEIGHT - 20 - self.radius

        target_x = max(min_bounds_x, min(max_bounds_x, self.x + dx * self.speed))
        target_y = max(min_bounds_y, min(max_bounds_y, self.y + dy * self.speed))

        if not self.check_obstacle_collision(target_x, target_y, obstacles):
            self.x = target_x
            self.y = target_y
        else:
            if not self.check_obstacle_collision(target_x, self.y, obstacles):
                self.x = target_x
            if not self.check_obstacle_collision(self.x, target_y, obstacles):
                self.y = target_y

        if boost.active and math.hypot(self.x - boost.x, self.y - boost.y) < (self.radius + boost.radius):
            self.boost_timer = BOOST_DURATION
            boost.trigger_pickup()

    def check_obstacle_collision(self, next_x, next_y, obstacles):
        player_rect = pygame.Rect(next_x - self.radius, next_y - self.radius, 
                                  self.radius * 2, self.radius * 2)
        return any(player_rect.colliderect(obs) for obs in obstacles)

    def draw(self, surface):
        size = 48
        char_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        pygame.draw.ellipse(surface, (0, 0, 0, 70), (self.x - 14, self.y + 8, 28, 12))

        pygame.draw.circle(char_surf, COLOR_SKIN, (center + 14, center - 10), 4)
        pygame.draw.circle(char_surf, COLOR_SKIN, (center + 14, center + 10), 4)

        pygame.draw.ellipse(char_surf, self.shirt_color, (center - 10, center - 14, 20, 28))
        pygame.draw.ellipse(char_surf, (20, 20, 20), (center - 10, center - 14, 20, 28), width=2)

        pygame.draw.circle(char_surf, COLOR_SKIN, (center, center), 10)
        pygame.draw.circle(char_surf, self.hair_color, (center - 2, center), 9)
        pygame.draw.circle(char_surf, (20, 20, 20), (center, center), 10, width=1)

        if self.has_crown:
            draw_topdown_crown(char_surf, center, center, scale=0.7)

        rotated_surf = pygame.transform.rotate(char_surf, self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, new_rect.topleft)

        if self.boost_timer > 0:
            boost_aura = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(boost_aura, (0, 180, 255, 80), (int(self.radius * 1.5), int(self.radius * 1.5)), int(self.radius * 1.4))
            surface.blit(boost_aura, (self.x - self.radius * 1.5, self.y - self.radius * 1.5))

        if self.has_crown:
            glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, 45), (self.radius * 2, self.radius * 2), self.radius * 2)
            surface.blit(glow_surf, (self.x - self.radius * 2, self.y - self.radius * 2))


def draw_topdown_crown(surface, cx, cy, scale=1.0):
    base_r = int(14 * scale)
    inner_r = int(7 * scale)
    spike_r = int(18 * scale)

    pygame.draw.circle(surface, COLOR_CROWN, (cx, cy), base_r)
    pygame.draw.circle(surface, (180, 140, 0), (cx, cy), inner_r)
    pygame.draw.circle(surface, (0, 0, 0), (cx, cy), base_r, width=1)

    num_spikes = 5
    for i in range(num_spikes):
        angle = math.radians(i * (360 / num_spikes) - 90)
        tip_x = cx + math.cos(angle) * spike_r
        tip_y = cy + math.sin(angle) * spike_r
        pygame.draw.circle(surface, COLOR_CROWN, (int(tip_x), int(tip_y)), int(4 * scale))
        pygame.draw.circle(surface, (0, 0, 0), (int(tip_x), int(tip_y)), int(4 * scale), width=1)

        gem_x = cx + math.cos(angle) * (base_r * 0.7)
        gem_y = cy + math.sin(angle) * (base_r * 0.7)
        pygame.draw.circle(surface, COLOR_CROWN_GEM, (int(gem_x), int(gem_y)), max(1, int(2.5 * scale)))


class Crown:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.radius = 16
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.is_picked_up = False

    def draw(self, surface):
        if not self.is_picked_up:
            draw_topdown_crown(surface, int(self.x), int(self.y), scale=1.1)


# --- DRAWING FUNCTIONS ---

def draw_grass_tufts(surface):
    for gx, gy in GRASS_TUFTS:
        pygame.draw.line(surface, COLOR_GRASS_DARK, (gx, gy), (gx - 3, gy - 6), 2)
        pygame.draw.line(surface, COLOR_GRASS_LIGHT, (gx, gy), (gx, gy - 7), 2)
        pygame.draw.line(surface, COLOR_GRASS_DARK, (gx, gy), (gx + 3, gy - 6), 2)


def draw_tree(surface, cx, cy, r=24):
    shadow_surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, r * 2.4, r * 1.6))
    surface.blit(shadow_surf, (cx - r * 0.9, cy + r * 0.3))

    pygame.draw.circle(surface, (90, 50, 20), (cx, cy + int(r * 0.3)), int(r * 0.35))
    pygame.draw.circle(surface, (40, 20, 5), (cx, cy + int(r * 0.3)), int(r * 0.35), width=2)

    layers = [
        (r * 1.0,  (20, 70, 20)),
        (r * 0.85, (30, 95, 30)),
        (r * 0.68, (45, 125, 45)),
        (r * 0.50, (65, 155, 65)),
        (r * 0.30, (90, 180, 80))
    ]

    for radius, color in layers:
        pygame.draw.circle(surface, color, (cx, cy), int(radius))

    blobs = [
        (-0.4, -0.3, 0.45, (55, 135, 55)),
        (0.4, -0.2, 0.4, (55, 135, 55)),
        (-0.3, 0.4, 0.35, (35, 105, 35)),
        (0.3, 0.3, 0.38, (35, 105, 35)),
        (-0.2, -0.5, 0.25, (85, 175, 75))
    ]
    for ox, oy, scale, color in blobs:
        bx = int(cx + ox * r)
        by = int(cy + oy * r)
        br = int(r * scale)
        pygame.draw.circle(surface, color, (bx, by), br)

    pygame.draw.circle(surface, (15, 50, 15), (cx, cy), int(r), width=2)


def draw_house(surface, offset_x=25, offset_y=20):
    # Wall base
    pygame.draw.rect(surface, COLOR_WALL, (offset_x, offset_y + 90, 170, 180))

    # Roof Shadow
    roof_shadow = pygame.Surface((205, 220), pygame.SRCALPHA)
    roof_shadow_pts = [(0, 75), (195, 75), (195, 168), (105, 168), (105, 288), (0, 288)]
    pygame.draw.polygon(roof_shadow, (0, 0, 0, 65), roof_shadow_pts)
    surface.blit(roof_shadow, (offset_x, offset_y))

    # Roof Base / Edge
    base_pts = [
        (offset_x + 0, offset_y + 70), 
        (offset_x + 190, offset_y + 70), 
        (offset_x + 190, offset_y + 160), 
        (offset_x + 100, offset_y + 160), 
        (offset_x + 100, offset_y + 280), 
        (offset_x + 0, offset_y + 280)
    ]
    pygame.draw.polygon(surface, COLOR_ROOF_EDGE, base_pts)

    # Main Roof Surface
    main_roof_pts = [
        (offset_x + 0, offset_y + 70), 
        (offset_x + 185, offset_y + 70), 
        (offset_x + 185, offset_y + 155), 
        (offset_x + 95, offset_y + 155), 
        (offset_x + 95, offset_y + 275), 
        (offset_x + 0, offset_y + 275)
    ]
    pygame.draw.polygon(surface, COLOR_ROOF, main_roof_pts)

    # Top Section Shading Lines
    for y in range(85, 155, 12):
        pygame.draw.line(surface, COLOR_ROOF_DARK, (offset_x, offset_y + y), (offset_x + 185, offset_y + y), 2)
        pygame.draw.line(surface, COLOR_ROOF_LIGHT, (offset_x, offset_y + y + 2), (offset_x + 185, offset_y + y + 2), 1)

    # Lower Section Shading Lines
    for y in range(165, 275, 12):
        pygame.draw.line(surface, COLOR_ROOF_DARK, (offset_x, offset_y + y), (offset_x + 95, offset_y + y), 2)
        pygame.draw.line(surface, COLOR_ROOF_LIGHT, (offset_x, offset_y + y + 2), (offset_x + 95, offset_y + y + 2), 1)

    # Roof Highlights & Borders
    pygame.draw.polygon(surface, COLOR_ROOF_LIGHT, [
        (offset_x + 0, offset_y + 70), 
        (offset_x + 185, offset_y + 70), 
        (offset_x + 185, offset_y + 78), 
        (offset_x + 0, offset_y + 78)
    ])
    pygame.draw.polygon(surface, COLOR_ROOF_DARK, [
        (offset_x + 177, offset_y + 70), 
        (offset_x + 185, offset_y + 70), 
        (offset_x + 185, offset_y + 155), 
        (offset_x + 177, offset_y + 155)
    ])
    pygame.draw.polygon(surface, COLOR_ROOF_DARK, [
        (offset_x + 87, offset_y + 155), 
        (offset_x + 95, offset_y + 155), 
        (offset_x + 95, offset_y + 275), 
        (offset_x + 87, offset_y + 275)
    ])
    pygame.draw.polygon(surface, (30, 20, 15), main_roof_pts, width=2)


def draw_white_picket_fence(surface, rect, house_rect=None):
    x, y, w, h = rect
    post_spacing = 16
    post_w = 6
    rail_thick = 3

    # Helper function to check if a point or rect overlaps the house
    def is_blocked(test_x, test_y, test_w=1, test_h=1):
        if house_rect is None:
            return False
        return house_rect.colliderect(pygame.Rect(test_x, test_y, test_w, test_h))

    # --- Horizontal Rails (Top and Bottom) ---
    # Top Rail: Skipped where it overlaps the house roof
    for rx in range(x, x + w):
        if not is_blocked(rx, y, 1, 6):
            pygame.draw.line(surface, (200, 200, 200), (rx, y + 6), (rx + 1, y + 6), rail_thick)
            pygame.draw.line(surface, COLOR_WHITE, (rx, y + 5), (rx + 1, y + 5), rail_thick)

    # Bottom Rail
    pygame.draw.line(surface, (200, 200, 200), (x, y + h - 6), (x + w, y + h - 6), rail_thick)
    pygame.draw.line(surface, COLOR_WHITE, (x, y + h - 5), (x + w, y + h - 5), rail_thick)

    # --- Vertical Rails (Left and Right) ---
    # Left Rail: Skipped where it overlaps the house roof
    for ry in range(y, y + h):
        if not is_blocked(x, ry, 6, 1):
            pygame.draw.line(surface, (200, 200, 200), (x + 6, ry), (x + 6, ry + 1), rail_thick)
            pygame.draw.line(surface, COLOR_WHITE, (x + 5, ry), (x + 5, ry + 1), rail_thick)

    # Right Rail
    pygame.draw.line(surface, (200, 200, 200), (x + w - 6, y), (x + w - 6, y + h), rail_thick)
    pygame.draw.line(surface, COLOR_WHITE, (x + w - 5, y), (x + w - 5, y + h), rail_thick)

    # --- Posts along Top and Bottom ---
    for px in range(x, x + w + 1, post_spacing):
        post_x = px - post_w // 2
        # Top posts (skip if blocked by house)
        if not is_blocked(post_x, y, post_w, 10):
            pygame.draw.rect(surface, COLOR_WHITE, (post_x, y, post_w, 10))
            pygame.draw.rect(surface, (180, 180, 180), (post_x, y, post_w, 10), width=1)
        
        # Bottom posts
        pygame.draw.rect(surface, COLOR_WHITE, (post_x, y + h - 10, post_w, 10))
        pygame.draw.rect(surface, (180, 180, 180), (post_x, y + h - 10, post_w, 10), width=1)

    # --- Posts along Left and Right ---
    for py in range(y, y + h + 1, post_spacing):
        post_y = py - post_w // 2
        # Left posts (skip if blocked by house)
        if not is_blocked(x, post_y, 10, post_w):
            pygame.draw.rect(surface, COLOR_WHITE, (x, post_y, 10, post_w))
            pygame.draw.rect(surface, (180, 180, 180), (x, post_y, 10, post_w), width=1)
            
        # Right posts
        pygame.draw.rect(surface, COLOR_WHITE, (x + w - 10, post_y, 10, post_w))
        pygame.draw.rect(surface, (180, 180, 180), (x + w - 10, post_y, 10, post_w), width=1)


def draw_map(surface, mud_patches):
    surface.fill(COLOR_BG)
    draw_grass_tufts(surface)

    for p in mud_patches:
        for bx, by, br in p["blobs"]:
            pygame.draw.circle(surface, COLOR_MUD_DARK, (bx, by), br + 3)

        for bx, by, br in p["blobs"]:
            pygame.draw.circle(surface, COLOR_MUD, (bx, by), br)

        for bx, by, br in p["blobs"]:
            pygame.draw.circle(surface, COLOR_MUD_LIGHT, (bx - 2, by - 2), int(br * 0.65))

        for bx, by, br in p["blobs"]:
            pygame.draw.circle(surface, COLOR_MUD_LIGHT, (bx - 2, by - 2), int(br * 0.65))

    draw_house(surface)

    pygame.draw.rect(surface, COLOR_POOL_RIM, (410, 370, 170, 160), border_radius=8)
    pygame.draw.rect(surface, COLOR_WATER, (425, 385, 140, 130), border_radius=4)
    pygame.draw.rect(surface, (0, 0, 0), (410, 370, 170, 160), width=3, border_radius=8)
    
    bridge_x = 475
    for i in range(3):
        pygame.draw.rect(surface, COLOR_BRIDGE, (bridge_x, 395 + (i * 38), 40, 28), border_radius=4)
        pygame.draw.rect(surface, (40, 40, 40), (bridge_x, 395 + (i * 38), 40, 28), width=2, border_radius=4)

    draw_white_picket_fence(surface, (10, 10, WIDTH - 20, HEIGHT - 20))

    trees = [(230, 130), (420, 140), (500, 220), (280, 580)]
    for tx, ty in trees:
        draw_tree(surface, tx, ty, r=26)


def draw_hud(surface, font, p1, p2):
    p1_bg = pygame.Rect(20, 20, 175, 40)
    pygame.draw.rect(surface, (20, 20, 20), p1_bg, border_radius=8)
    pygame.draw.rect(surface, COLOR_P1, p1_bg, width=3, border_radius=8)
    p1_txt = font.render(f"P1: {p1.hold_time:04.1f}s / {WIN_TIME:.0f}s", True, COLOR_WHITE)
    surface.blit(p1_txt, (p1_bg.x + 12, p1_bg.y + 8))

    p2_bg = pygame.Rect(WIDTH - 195, 20, 175, 40)
    pygame.draw.rect(surface, (20, 20, 20), p2_bg, border_radius=8)
    pygame.draw.rect(surface, COLOR_P2, p2_bg, width=3, border_radius=8)
    p2_txt = font.render(f"P2: {p2.hold_time:04.1f}s / {WIN_TIME:.0f}s", True, COLOR_WHITE)
    surface.blit(p2_txt, (p2_bg.x + 12, p2_bg.y + 8))


def resolve_player_collision(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = math.hypot(dx, dy)
    min_dist = p1.radius + p2.radius

    if 0 < distance < min_dist:
        overlap = min_dist - distance
        nx = dx / distance
        ny = dy / distance

        p1.x -= nx * (overlap / 2)
        p1.y -= ny * (overlap / 2)
        p2.x += nx * (overlap / 2)
        p2.y += ny * (overlap / 2)


def draw_button(surface, rect, text, font, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    color = COLOR_BTN_HOVER if hovered else COLOR_BTN_NORMAL
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_CROWN if hovered else (180, 180, 180), rect, width=2, border_radius=10)
    
    txt_surf = font.render(text, True, COLOR_WHITE)
    surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))
    return hovered


def draw_welcome_screen(surface, font_title, font_sub, font_bold, start_bg=None):
    if start_bg:
        surface.blit(start_bg, (0, 0))
        tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 130))
        surface.blit(tint, (0, 0))
    else:
        surface.fill((25, 30, 35))

    title = font_title.render("KING OF THE CROWN", True, COLOR_CROWN)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    draw_topdown_crown(surface, WIDTH // 2, 125, scale=1.8)

    box_rect = pygame.Rect(50, 180, WIDTH - 100, 350)
    pygame.draw.rect(surface, (25, 30, 38, 220), box_rect, border_radius=12)
    pygame.draw.rect(surface, COLOR_CROWN, box_rect, width=2, border_radius=12)

    p1_head = font_bold.render("PLAYER 1 (BLUE)", True, COLOR_P1)
    p1_ctrl = font_sub.render("Controls:  W, A, S, D", True, COLOR_WHITE)
    
    p2_head = font_bold.render("PLAYER 2 (RED)", True, COLOR_P2)
    p2_ctrl = font_sub.render("Controls:  ARROW KEYS", True, COLOR_WHITE)

    rules_head = font_bold.render("HOW TO PLAY", True, COLOR_CROWN)
    rule_1 = font_sub.render("• Grab the crown & hold it for 20 seconds!", True, COLOR_WHITE)
    rule_2 = font_sub.render("• Bump into the crown holder to steal it.", True, COLOR_WHITE)
    rule_3 = font_sub.render("• Grab blue thunder boost for extra speed!", True, COLOR_WHITE)
    pause_info = font_sub.render("• Press 'P' at any time to Pause the game.", True, (200, 200, 200))

    surface.blit(p1_head, (75, 200))
    surface.blit(p1_ctrl, (75, 225))

    surface.blit(p2_head, (75, 265))
    surface.blit(p2_ctrl, (75, 290))

    surface.blit(rules_head, (75, 335))
    surface.blit(rule_1, (75, 365))
    surface.blit(rule_2, (75, 390))
    surface.blit(rule_3, (75, 415))
    surface.blit(pause_info, (75, 450))

    start_txt = font_bold.render("PRESS SPACE TO START", True, COLOR_CROWN)
    surface.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 560))


# --- MAIN LOOP ---

def main():
    font_hud = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
    font_sub = pygame.font.SysFont("Trebuchet MS", 16)
    font_bold = pygame.font.SysFont("Trebuchet MS", 20, bold=True)
    font_title = pygame.font.SysFont("Trebuchet MS", 36, bold=True)

    start_bg = None
    for bg_filename in ["background.jpg", "background.png"]:
        try:
            loaded_img = pygame.image.load(bg_filename).convert()
            start_bg = pygame.transform.scale(loaded_img, (WIDTH, HEIGHT))
            break
        except FileNotFoundError:
            continue

    game_state = STATE_MENU
    is_paused = False

    p1_controls = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d}
    p2_controls = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}

    p1 = Player(200, 320, COLOR_P1, COLOR_HAIR_1, p1_controls, initial_angle=0)
    p2 = Player(400, 320, COLOR_P2, COLOR_HAIR_2, p2_controls, initial_angle=180)
    crown = Crown(WIDTH // 2, HEIGHT // 2)
    lawnmower = Lawnmower(x_min=45, x_max=165, y=460)

    mud_patches = get_mud_patches()
    boost = SpeedBoost(mud_patches)

    game_over = False
    winner_text = ""
    steal_cooldown = 0.0

    btn_w, btn_h = 180, 45
    btn_resume = pygame.Rect(WIDTH // 2 - btn_w // 2, 230, btn_w, btn_h)
    btn_restart = pygame.Rect(WIDTH // 2 - btn_w // 2, 290, btn_w, btn_h)
    btn_home = pygame.Rect(WIDTH // 2 - btn_w // 2, 350, btn_w, btn_h)

    def reset_game():
        nonlocal game_over, winner_text, steal_cooldown, is_paused
        p1.reset()
        p2.reset()
        crown.reset()
        boost.active = False
        boost.respawn_timer = random.uniform(2.0, 5.0)
        game_over = False
        winner_text = ""
        steal_cooldown = 0.0
        is_paused = False

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_state == STATE_MENU and event.key == pygame.K_SPACE:
                    reset_game()
                    game_state = STATE_PLAYING

                elif game_state == STATE_PLAYING and event.key == pygame.K_p and not game_over:
                    is_paused = not is_paused

                elif game_over and event.key == pygame.K_r:
                    reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN and is_paused:
                if btn_resume.collidepoint(mouse_pos):
                    is_paused = False
                elif btn_restart.collidepoint(mouse_pos):
                    reset_game()
                elif btn_home.collidepoint(mouse_pos):
                    reset_game()
                    game_state = STATE_MENU

        # --- UPDATE & DRAW ---

        if game_state == STATE_MENU:
            draw_welcome_screen(screen, font_title, font_sub, font_bold, start_bg)

        elif game_state == STATE_PLAYING:
            if not is_paused and not game_over:
                if steal_cooldown > 0:
                    steal_cooldown -= dt

                boost.update(dt)

                keys = pygame.key.get_pressed()
                lawnmower.update()
                current_obstacles = get_static_obstacles() + [lawnmower.get_rect()]

                p1.handle_input(keys, current_obstacles, mud_patches, boost, dt)
                p2.handle_input(keys, current_obstacles, mud_patches, boost, dt)
                resolve_player_collision(p1, p2)

                if not crown.is_picked_up:
                    p1_dist = math.hypot(p1.x - crown.x, p1.y - crown.y)
                    p2_dist = math.hypot(p2.x - crown.x, p2.y - crown.y)

                    if p1_dist < (p1.radius + crown.radius):
                        p1.has_crown = True
                        crown.is_picked_up = True
                        steal_cooldown = STEAL_COOLDOWN_TIME
                    elif p2_dist < (p2.radius + crown.radius):
                        p2.has_crown = True
                        crown.is_picked_up = True
                        steal_cooldown = STEAL_COOLDOWN_TIME

                elif steal_cooldown <= 0:
                    player_dist = math.hypot(p1.x - p2.x, p1.y - p2.y)
                    if player_dist <= (p1.radius + p2.radius + 2):
                        if p1.has_crown:
                            p1.has_crown = False
                            p2.has_crown = True
                        elif p2.has_crown:
                            p2.has_crown = False
                            p1.has_crown = True
                        
                        steal_cooldown = STEAL_COOLDOWN_TIME

                if p1.has_crown:
                    p1.hold_time += dt
                    if p1.hold_time >= WIN_TIME:
                        p1.hold_time = WIN_TIME
                        game_over = True
                        winner_text = "PLAYER 1 WINS!"

                elif p2.has_crown:
                    p2.hold_time += dt
                    if p2.hold_time >= WIN_TIME:
                        p2.hold_time = WIN_TIME
                        game_over = True
                        winner_text = "PLAYER 2 WINS!"

            # Render World
            draw_map(screen, mud_patches)
            lawnmower.draw(screen)
            boost.draw(screen)
            crown.draw(screen)
            p1.draw(screen)
            p2.draw(screen)
            draw_hud(screen, font_hud, p1, p2)

            # Pause Overlay
            if is_paused:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))

                pause_box = pygame.Rect(WIDTH // 2 - 130, 140, 260, 280)
                pygame.draw.rect(screen, (30, 35, 45), pause_box, border_radius=12)
                pygame.draw.rect(screen, COLOR_CROWN, pause_box, width=2, border_radius=12)

                p_title = font_title.render("PAUSED", True, COLOR_CROWN)
                screen.blit(p_title, (WIDTH // 2 - p_title.get_width() // 2, 160))

                draw_button(screen, btn_resume, "Resume", font_bold, mouse_pos)
                draw_button(screen, btn_restart, "Restart", font_bold, mouse_pos)
                draw_button(screen, btn_home, "Home Page", font_bold, mouse_pos)

            elif game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                txt = font_title.render(winner_text, True, COLOR_CROWN)
                sub_txt = font_hud.render("Press 'R' to Restart", True, COLOR_WHITE)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
                screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

if __name__ == "__main__":
    main()
import sys
import math
import pygame

# --- INITIALIZATION & CONSTANTS ---
pygame.init()

WIDTH, HEIGHT = 600, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King of the Crown")
clock = pygame.time.Clock()
FPS = 60

# Colors
COLOR_BG = (118, 198, 88)
COLOR_ROOF = (212, 117, 86)
COLOR_WALL = (244, 219, 161)
COLOR_WATER = (91, 160, 226)
COLOR_POOL_RIM = (230, 210, 190)
COLOR_BRIDGE = (180, 180, 160)
COLOR_DARK_GREEN = (34, 100, 34)
COLOR_MUD = (139, 90, 43)
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

# Game Rules
WIN_TIME = 20.0
STEAL_COOLDOWN_TIME = 0.8
NORMAL_SPEED = 4.2
MUD_SPEED = 2.1

# Game States
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"

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
        pygame.draw.rect(surface, (200, 60, 40), mower_rect, border_radius=4)
        pygame.draw.rect(surface, (20, 20, 20), mower_rect, width=2, border_radius=4)
        
        handle_x = self.x + (5 if self.direction == 1 else self.width - 15)
        pygame.draw.rect(surface, (40, 40, 40), (handle_x, self.y + 10, 10, 20))


class Player:
    def __init__(self, x, y, color, hair_color, controls):
        self.x = x
        self.y = y
        self.radius = 16
        self.shirt_color = color
        self.hair_color = hair_color
        self.speed = NORMAL_SPEED
        self.controls = controls
        self.has_crown = False
        self.hold_time = 0.0
        self.angle = 0

    def handle_input(self, keys, obstacles, mud_patches):
        in_mud = any(math.hypot(self.x - mx, self.y - my) < (self.radius + mr) for mx, my, mr in mud_patches)
        self.speed = MUD_SPEED if in_mud else NORMAL_SPEED

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

        new_x = max(self.radius, min(WIDTH - self.radius, self.x + dx * self.speed))
        new_y = max(self.radius, min(HEIGHT - self.radius, self.y + dy * self.speed))

        if not self.check_obstacle_collision(new_x, self.y, obstacles):
            self.x = new_x
        if not self.check_obstacle_collision(self.x, new_y, obstacles):
            self.y = new_y

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
        self.x = x
        self.y = y
        self.radius = 16
        self.is_picked_up = False

    def draw(self, surface):
        if not self.is_picked_up:
            draw_topdown_crown(surface, int(self.x), int(self.y), scale=1.1)


# --- ENVIRONMENT & MAP ---

def get_mud_patches():
    return [(210, 350, 24), (480, 80, 28), (350, 500, 20)]

def get_static_obstacles():
    return [
        pygame.Rect(0, 80, 180, 140),
        pygame.Rect(0, 220, 80, 60),
        pygame.Rect(410, 370, 60, 160),
        pygame.Rect(520, 370, 60, 160)
    ]

def draw_map(surface, mud_patches):
    surface.fill(COLOR_BG)

    for mx, my, mr in mud_patches:
        pygame.draw.circle(surface, COLOR_MUD, (mx, my), mr)
        pygame.draw.circle(surface, (90, 50, 20), (mx, my), mr, 2)

    pygame.draw.rect(surface, COLOR_WALL, (0, 90, 170, 180))
    pygame.draw.polygon(surface, COLOR_ROOF, [(0, 70), (190, 70), (190, 160), (100, 160), (100, 280), (0, 280)])
    pygame.draw.polygon(surface, (0, 0, 0), [(0, 70), (190, 70), (190, 160), (100, 160), (100, 280), (0, 280)], 3)

    pygame.draw.rect(surface, COLOR_POOL_RIM, (410, 370, 170, 160), border_radius=8)
    pygame.draw.rect(surface, COLOR_WATER, (425, 385, 140, 130), border_radius=4)
    pygame.draw.rect(surface, (0, 0, 0), (410, 370, 170, 160), width=3, border_radius=8)
    
    bridge_x = 475
    for i in range(3):
        pygame.draw.rect(surface, COLOR_BRIDGE, (bridge_x, 395 + (i * 38), 40, 28), border_radius=4)
        pygame.draw.rect(surface, (40, 40, 40), (bridge_x, 395 + (i * 38), 40, 28), width=2, border_radius=4)

    pygame.draw.rect(surface, COLOR_BG, (30, 390, 180, 180))
    pygame.draw.rect(surface, COLOR_DARK_GREEN, (30, 390, 180, 180), width=6)

    trees = [(230, 130), (420, 140), (500, 220), (280, 580)]
    for tx, ty in trees:
        pygame.draw.circle(surface, (45, 130, 45), (tx, ty), 18)
        pygame.draw.circle(surface, (20, 80, 20), (tx, ty), 18, 2)

    pygame.draw.rect(surface, COLOR_DARK_GREEN, (0, 0, WIDTH, 25))
    pygame.draw.rect(surface, COLOR_DARK_GREEN, (0, HEIGHT - 25, WIDTH, 25))


def draw_hud(surface, font, p1, p2):
    p1_bg = pygame.Rect(15, 35, 175, 40)
    pygame.draw.rect(surface, (20, 20, 20), p1_bg, border_radius=8)
    pygame.draw.rect(surface, COLOR_P1, p1_bg, width=3, border_radius=8)
    p1_txt = font.render(f"P1: {p1.hold_time:04.1f}s / {WIN_TIME:.0f}s", True, COLOR_WHITE)
    surface.blit(p1_txt, (p1_bg.x + 12, p1_bg.y + 8))

    p2_bg = pygame.Rect(WIDTH - 190, 35, 175, 40)
    pygame.draw.rect(surface, (20, 20, 20), p2_bg, border_radius=8)
    pygame.draw.rect(surface, COLOR_P2, p2_bg, width=3, border_radius=8)
    p2_txt = font.render(f"P2: {p2.hold_time:04.1f}s / {WIN_TIME:.0f}s", True, COLOR_WHITE)
    surface.blit(p2_txt, (p2_bg.x + 12, p2_bg.y + 8))


def resolve_player_collision(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = math.hypot(dx, dy)
    min_dist = p1.radius + p2.radius

    if distance < min_dist and distance > 0:
        overlap = min_dist - distance
        nx = dx / distance
        ny = dy / distance

        p1.x -= nx * (overlap / 2)
        p1.y -= ny * (overlap / 2)
        p2.x += nx * (overlap / 2)
        p2.y += ny * (overlap / 2)


# --- UI HELPERS ---

def draw_button(surface, rect, text, font, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    color = COLOR_BTN_HOVER if hovered else COLOR_BTN_NORMAL
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, COLOR_CROWN if hovered else (180, 180, 180), rect, width=2, border_radius=10)
    
    txt_surf = font.render(text, True, COLOR_WHITE)
    surface.blit(txt_surf, (rect.cx - txt_surf.get_width() // 2, rect.cy - txt_surf.get_height() // 2))
    return hovered


# --- UI SCREENS ---

def draw_welcome_screen(surface, font_title, font_sub, font_bold, start_bg=None):
    if start_bg:
        surface.blit(start_bg, (0, 0))
        # Dark translucent overlay to keep text easily readable over any image
        tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        tint.fill((0, 0, 0, 130))
        surface.blit(tint, (0, 0))
    else:
        surface.fill((25, 30, 35))

    # Title & Decor
    title = font_title.render("KING OF THE CROWN", True, COLOR_CROWN)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    
    draw_topdown_crown(surface, WIDTH // 2, 125, scale=1.8)

    # Controls Info Box
    box_rect = pygame.Rect(50, 180, WIDTH - 100, 350)
    pygame.draw.rect(surface, (25, 30, 38, 220), box_rect, border_radius=12)
    pygame.draw.rect(surface, COLOR_CROWN, box_rect, width=2, border_radius=12)

    # Instructions
    p1_head = font_bold.render("PLAYER 1 (BLUE)", True, COLOR_P1)
    p1_ctrl = font_sub.render("Controls:  W, A, S, D", True, COLOR_WHITE)
    
    p2_head = font_bold.render("PLAYER 2 (RED)", True, COLOR_P2)
    p2_ctrl = font_sub.render("Controls:  ARROW KEYS", True, COLOR_WHITE)

    rules_head = font_bold.render("HOW TO PLAY", True, COLOR_CROWN)
    rule_1 = font_sub.render("• Grab the crown & hold it for 20 seconds!", True, COLOR_WHITE)
    rule_2 = font_sub.render("• Bump into the crown holder to steal it.", True, COLOR_WHITE)
    rule_3 = font_sub.render("• Mud slows you down | Cross pool via bridge.", True, COLOR_WHITE)
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

    # Start Prompt
    start_txt = font_bold.render("PRESS SPACE TO START", True, COLOR_CROWN)
    surface.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 560))


# --- MAIN LOOP ---

def main():
    font_hud = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
    font_sub = pygame.font.SysFont("Trebuchet MS", 16)
    font_bold = pygame.font.SysFont("Trebuchet MS", 20, bold=True)
    font_title = pygame.font.SysFont("Trebuchet MS", 36, bold=True)

    # Try loading custom start menu background image
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

    # Player and Objects Initialization
    p1_controls = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d}
    p2_controls = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}

    p1 = Player(200, 320, COLOR_P1, COLOR_HAIR_1, p1_controls)
    p2 = Player(400, 320, COLOR_P2, COLOR_HAIR_2, p2_controls)
    crown = Crown(WIDTH // 2, HEIGHT // 2)
    lawnmower = Lawnmower(x_min=45, x_max=165, y=460)

    mud_patches = get_mud_patches()
    game_over = False
    winner_text = ""
    steal_cooldown = 0.0

    # Pause Menu Buttons
    btn_w, btn_h = 180, 45
    btn_resume = pygame.Rect(WIDTH // 2 - btn_w // 2, 230, btn_w, btn_h)
    btn_restart = pygame.Rect(WIDTH // 2 - btn_w // 2, 290, btn_w, btn_h)
    btn_home = pygame.Rect(WIDTH // 2 - btn_w // 2, 350, btn_w, btn_h)

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Start game from Welcome Screen
                if game_state == STATE_MENU and event.key == pygame.K_SPACE:
                    game_state = STATE_PLAYING

                # Pause Toggle
                elif game_state == STATE_PLAYING and event.key == pygame.K_p and not game_over:
                    is_paused = not is_paused

                # Restart shortcut on game over
                elif game_over and event.key == pygame.K_r:
                    main()

            # Mouse Clicks in Pause Menu
            if event.type == pygame.MOUSEBUTTONDOWN and is_paused:
                if btn_resume.collidepoint(mouse_pos):
                    is_paused = False
                elif btn_restart.collidepoint(mouse_pos):
                    main()
                elif btn_home.collidepoint(mouse_pos):
                    main()

        # --- UPDATE & DRAW ---

        if game_state == STATE_MENU:
            draw_welcome_screen(screen, font_title, font_sub, font_bold, start_bg)

        elif game_state == STATE_PLAYING:
            if not is_paused and not game_over:
                if steal_cooldown > 0:
                    steal_cooldown -= dt

                keys = pygame.key.get_pressed()
                lawnmower.update()
                current_obstacles = get_static_obstacles() + [lawnmower.get_rect()]

                p1.handle_input(keys, current_obstacles, mud_patches)
                p2.handle_input(keys, current_obstacles, mud_patches)
                resolve_player_collision(p1, p2)

                # Crown pickup & stealing
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

                # Victory timers
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

            # Render Game World
            draw_map(screen, mud_patches)
            lawnmower.draw(screen)
            crown.draw(screen)
            p1.draw(screen)
            p2.draw(screen)
            draw_hud(screen, font_hud, p1, p2)

            # Pause Overlay Pop-up
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

            # Game Over Overlay
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
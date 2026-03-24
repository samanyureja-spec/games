import pygame
import math
import random
import sys

# --- 1. INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GLITCH PROTOCOL // terminal_flux.exe")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 18, bold=True)
large_font = pygame.font.SysFont("monospace", 45, bold=True)

# COLORS
BG = (5, 5, 15);
CYAN = (0, 255, 255);
RED = (255, 40, 40)
YELLOW = (255, 230, 0);
WHITE = (255, 255, 255);
GRID = (15, 15, 30)
DARK_GRAY = (40, 40, 40);
LEAK_RED = (60, 0, 0);
CODE_COLOR = (15, 25, 60)


# --- 2. CLASSES ---

class CodeStream:
    """The background flowing text feature."""

    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = -20
        self.speed = random.uniform(1, 3)
        self.text = random.choice(["0x1F", "0xAA", "ERR", "01", "0xBC", "SYS", "VOID", "NULL"])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT: self.reset()

    def draw(self, surface):
        surf = font.render(self.text, True, CODE_COLOR)
        surface.blit(surf, (self.x, self.y))


class Particle:
    def __init__(self, pos, color):
        self.pos = pygame.Vector2(pos);
        self.vel = pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        self.life = 255;
        self.color = color

    def update(self):
        self.pos += self.vel;
        self.life -= 12;
        self.vel *= 0.93

    def draw(self, surface):
        if self.life > 0:
            s = pygame.Surface((3, 3));
            s.set_alpha(self.life);
            s.fill(self.color)
            surface.blit(s, (self.pos.x, self.pos.y))


class Virus:
    def __init__(self, x, y, is_scout=False, is_mini=False):
        self.pos = pygame.Vector2(x, y)
        self.is_scout, self.is_mini = is_scout, is_mini
        self.last_shot = pygame.time.get_ticks()
        self.size = 8 if is_mini else (18 if is_scout else 30)
        self.color = (255, 100, 100) if is_mini else ((200, 0, 0) if is_scout else RED)

    def update(self, target, packets, r_time):
        mult = 1.6 if self.is_scout else (1.2 if self.is_mini else 1.0)
        speed = (2.7 + (r_time // 15) * 0.7) * mult
        dist = target - self.pos
        if dist.length() > 0: self.pos += dist.normalize() * speed
        if not self.is_mini:
            now = pygame.time.get_ticks()
            delay = max(180 if self.is_scout else 300, 1100 - (r_time // 10) * 100)
            if now - self.last_shot > delay:
                packets.append([pygame.Vector2(self.pos), dist.normalize() * (11 if self.is_scout else 9)])
                self.last_shot = now


# --- 3. MAIN ENGINE ---

def run_game():
    player_pos, player_vel, player_health = pygame.Vector2(WIDTH // 2, HEIGHT // 2), pygame.Vector2(0, 0), 100
    viruses = [Virus(random.randint(0, WIDTH), 0)]
    packets, particles = [], []
    streams = [CodeStream() for _ in range(40)]  # Background text
    has_split = False

    # KILLER FEATURE VARIABLES
    leak_active = False
    leak_rect = pygame.Rect(0, 0, 0, 0)
    next_leak_time = 30
    last_mini_spawn = 0
    warning_active = False

    start_time = pygame.time.get_ticks()
    dash_cooldown, last_dash = 1800, -1800
    score = 0

    while True:
        now = pygame.time.get_ticks()
        r_time = (now - start_time) // 1000
        screen.fill(BG)

        # --- DATA LEAK LOGIC ---
        if not leak_active:
            if r_time >= next_leak_time - 10: warning_active = True
            if r_time >= next_leak_time:
                leak_active = True;
                warning_active = False
                leak_rect = pygame.Rect(random.randint(100, WIDTH - 300), random.randint(100, HEIGHT - 300), 250, 250)
        else:
            if now - last_mini_spawn > 2000:
                viruses.append(Virus(leak_rect.centerx, leak_rect.centery, is_mini=True))
                last_mini_spawn = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and now - last_dash > dash_cooldown:
                    if player_vel.length() > 0:
                        player_pos += player_vel.normalize() * 135
                        last_dash = now
                        for _ in range(15): particles.append(Particle(player_pos, CYAN))
                if event.key == pygame.K_a and leak_active:
                    leak_active = False
                    next_leak_time = r_time + random.randint(20, 40)
                    viruses = [v for v in viruses if not v.is_mini]
                    for _ in range(30): particles.append(Particle(leak_rect.center, WHITE))

        # BACKGROUND DRAWING (Text Streams + Grid)
        for s in streams: s.update(); s.draw(screen)
        for x in range(0, WIDTH, 60): pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 60): pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

        if leak_active:
            pygame.draw.rect(screen, LEAK_RED, leak_rect)
            for _ in range(4):
                corrupt_txt = font.render("CORRUPT_" + "".join(random.choices("01!", k=4)), True, RED)
                screen.blit(corrupt_txt, (leak_rect.x + random.randint(0, 150), leak_rect.y + random.randint(0, 220)))

        # MOVEMENT
        keys = pygame.key.get_pressed()
        acc = 0.8
        if keys[pygame.K_LEFT]: player_vel.x -= acc
        if keys[pygame.K_RIGHT]: player_vel.x += acc
        if keys[pygame.K_UP]: player_vel.y -= acc
        if keys[pygame.K_DOWN]: player_vel.y += acc
        player_vel *= 0.91;
        player_pos += player_vel
        player_pos.x = max(25, min(WIDTH - 25, player_pos.x))
        player_pos.y = max(25, min(HEIGHT - 25, player_pos.y))

        # FISSION & VIRUS LOGIC
        if r_time >= 30 and not has_split:
            viruses.append(Virus(WIDTH, HEIGHT, is_scout=True))
            has_split = True

        for v in viruses: v.update(player_pos, packets, r_time)
        for p in packets[:]:
            p[0] += p[1]
            pygame.draw.rect(screen, YELLOW, (p[0].x, p[0].y, 5, 5))
            if p[0].distance_to(player_pos) < 22:
                player_health -= 12
                for _ in range(12): particles.append(Particle(player_pos, RED))
                packets.remove(p)
            elif not (0 < p[0].x < WIDTH and 0 < p[0].y < HEIGHT):
                packets.remove(p)

        # RENDER ENTITIES
        for part in particles[:]:
            part.update();
            part.draw(screen)
            if part.life <= 0: particles.remove(part)
        for v in viruses:
            pygame.draw.rect(screen, v.color, (v.pos.x - v.size / 2, v.pos.y - v.size / 2, v.size, v.size))

        dash_ratio = min(1.0, (now - last_dash) / dash_cooldown)
        pts = [(player_pos.x + 20 * math.cos(math.radians(60 * i)), player_pos.y + 20 * math.sin(math.radians(60 * i)))
               for i in range(6)]
        pygame.draw.polygon(screen, CYAN if dash_ratio == 1.0 else (80, 80, 130), pts, 2)

        # --- UI SCORE & HUD ---
        if not leak_active: score += 1
        screen.blit(font.render(f"DATA_RECOVERED: {score // 10}KB", True, CYAN), (20, 20))
        screen.blit(font.render(f"RECOVERY_TIME: {r_time}s", True, YELLOW), (WIDTH - 220, 20))
        if warning_active:
            msg = font.render("!! WARNING: SYSTEM LEAK IMMINENT - READY DATA BURST (A) !!", True, YELLOW)
            screen.blit(msg, (WIDTH // 2 - 250, 50))

        # HUD BARS
        pygame.draw.rect(screen, DARK_GRAY, (20, HEIGHT - 35, 200, 10))
        pygame.draw.rect(screen, CYAN if player_health > 35 else RED, (20, HEIGHT - 35, player_health * 2, 10))
        pygame.draw.rect(screen, DARK_GRAY, (20, HEIGHT - 18, 200, 6))
        pygame.draw.rect(screen, WHITE if dash_ratio == 1.0 else (0, 180, 255), (20, HEIGHT - 18, dash_ratio * 200, 6))

        if player_health <= 0: break
        pygame.display.flip()
        clock.tick(60)

    show_crash(score // 10)


def show_crash(s):
    while True:
        screen.fill((25, 5, 5))
        screen.blit(large_font.render("CRITICAL SYSTEM FAILURE", True, RED), (WIDTH // 2 - 300, HEIGHT // 2 - 50))
        screen.blit(font.render(f"FINAL LOG: {s}KB RECOVERED", True, WHITE), (WIDTH // 2 - 130, HEIGHT // 2 + 20))
        screen.blit(font.render("PRESS 'R' TO REBOOT", True, CYAN), (WIDTH // 2 - 100, HEIGHT // 2 + 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: run_game()


run_game()


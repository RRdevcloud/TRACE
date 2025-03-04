import pygame
import random
import json
import time

pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 400
GRAVITY = 0.5
FLAP_STRENGTH = -7
OBSTACLE_SPEED = 2  
GAP_SIZE = 200  
LEADERBOARD_FILE = "leaderboard.json"

# Colors (Cyberpunk Theme)
NEON_RED = (255, 49, 49)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
BLACK = (0, 0, 0)

# Load Assets
BACKGROUND_IMAGE = pygame.image.load("background.png")
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
TRACE_IMAGE = pygame.image.load("trace.png")
TRACE_IMAGE = pygame.transform.scale(TRACE_IMAGE, (40, 40))
PIPE_IMAGE = pygame.image.load("barrier.png")
PIPE_IMAGE = pygame.transform.scale(PIPE_IMAGE, (50, HEIGHT // 2))

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts (Cyberpunk Style)
font = pygame.font.SysFont("Arial Black", 36)
large_font = pygame.font.SysFont("Arial Black", 80)

# Clear leaderboard at the start
def reset_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump([], f)

# Load the leaderboard or return an empty one
def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save the leaderboard (Reset if full)
def save_leaderboard(leaderboard):
    if len(leaderboard) >= 5:  # Full reset after 5 players
        leaderboard = []
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

# Display text with cyberpunk colors
def show_text(text, color, y_offset=0, font_size=36):
    selected_font = pygame.font.SysFont("Arial Black", font_size)
    text_surface = selected_font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

# Display leaderboard
def show_leaderboard():
    screen.fill(BLACK)
    show_text("LEADERBOARD", NEON_BLUE, -120, 50)
    
    leaderboard = load_leaderboard()
    
    for i, entry in enumerate(leaderboard[:5]):
        color = NEON_PINK if i % 2 == 0 else NEON_BLUE
        show_text(f"{entry['name']}: {entry['score']}", color, -50 + i * 30, 40)
    
    show_text("Press SPACE to Continue", NEON_RED, 100, 30)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

# Get player name before the game starts
def game_start_screen():
    screen.fill(BLACK)
    show_text("Enter your name: ", NEON_BLUE, -40, 40)
    pygame.display.update()
    
    name = ""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        screen.fill(BLACK)
        show_text("Enter your name: " + name, NEON_PINK, -40, 40)
        show_text("Press ENTER to start", NEON_BLUE, 20, 30)
        pygame.display.update()

# Game over screen with neon "WASTED" effect
def game_over_screen(score, name):
    leaderboard = load_leaderboard()
    
    leaderboard.append({"name": name, "score": score})
    
    if len(leaderboard) >= 5:
        leaderboard = []  # Full reset if 5 players played
    
    save_leaderboard(leaderboard)  

    screen.fill(BLACK)
    fade_alpha = 0
    text_surface = large_font.render("WASTED", True, NEON_RED)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    
    for i in range(50):
        screen.fill(BLACK)
        fade_surface = text_surface.copy()
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, text_rect)
        pygame.display.update()
        fade_alpha += 5
        time.sleep(0.02)
    
    time.sleep(2)
    show_leaderboard()
    return True

# Character Class
class Trace:
    def __init__(self):
        self.x, self.y = 100, HEIGHT // 3
        self.velocity_y = 0
    
    def flap(self):
        self.velocity_y = FLAP_STRENGTH

    def update(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        if self.y <= 0:
            self.y = 0
        if self.y >= HEIGHT - 40:
            self.y = HEIGHT - 40

    def draw(self):
        screen.blit(TRACE_IMAGE, (self.x, self.y))

# Obstacle Class
class Pipe:
    def __init__(self, x, difficulty):
        self.x = x
        self.gap_y = random.randint(50, HEIGHT - GAP_SIZE - 50 - difficulty)

    def update(self):
        self.x -= OBSTACLE_SPEED
    
    def draw(self):
        screen.blit(PIPE_IMAGE, (self.x, 0))
        screen.blit(PIPE_IMAGE, (self.x, self.gap_y + GAP_SIZE))

# Reset leaderboard before game starts
reset_leaderboard()

while True:
    player_name = game_start_screen()
    trace = Trace()
    difficulty = 0
    pipes = [Pipe(WIDTH + i * 300, difficulty) for i in range(3)]
    score = 0
    running = True
    
    while running:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        trace.update()
        trace.draw()
        
        for pipe in pipes[:]:
            pipe.update()
            pipe.draw()
            if pipe.x + 50 < 0:
                pipes.remove(pipe)
                difficulty += 5  
                pipes.append(Pipe(WIDTH, difficulty))
                score += 1
            
            if (trace.x < pipe.x + 50 and trace.x + 40 > pipe.x and
                (trace.y < pipe.gap_y or trace.y + 40 > pipe.gap_y + GAP_SIZE)):
                running = False
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                trace.flap()
    
    if not game_over_screen(score, player_name):
        break

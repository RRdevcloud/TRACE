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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)

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
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 80)

def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

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

class Pipe:
    def __init__(self, x, difficulty):
        self.x = x
        self.gap_y = random.randint(50, HEIGHT - GAP_SIZE - 50 - difficulty)

    def update(self):
        self.x -= OBSTACLE_SPEED
    
    def draw(self):
        screen.blit(PIPE_IMAGE, (self.x, 0))
        screen.blit(PIPE_IMAGE, (self.x, self.gap_y + GAP_SIZE))

while True:
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
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            trace.flap()
    
    pygame.quit()
    break

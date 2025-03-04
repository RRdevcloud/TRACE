import pygame
import random
import json
import time
import cv2
import mediapipe as mp
import math

pygame.init()

# Initialize OpenCV webcam
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

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

# Function to detect hand gesture
def get_hand_gesture():
    ret, frame = cap.read()
    if not ret:
        return "idle"
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            wrist = hand_landmarks.landmark[0]
            index_tip = hand_landmarks.landmark[8]
            
            dx = index_tip.x - wrist.x
            dy = index_tip.y - wrist.y
            angle = math.degrees(math.atan2(-dy, dx))
            
            if angle < 0:
                angle += 360
            
            if angle > 45 and angle < 135:
                return "jump"
    
    return "idle"

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
        
        gesture = get_hand_gesture()
        keys = pygame.key.get_pressed()
        if gesture == "jump" or keys[pygame.K_SPACE]:
            trace.flap()
    
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    break

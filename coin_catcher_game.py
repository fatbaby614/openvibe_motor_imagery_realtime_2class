import pygame
import sys
import random
from pylsl import StreamInlet, resolve_streams

# ================= Configuration =================
STREAM_NAME = "BCI_Control_Signal"  # Must match OpenViBE Python box name
SCREEN_W, SCREEN_H = 800, 600
PLAYER_WIDTH, PLAYER_HEIGHT = 80, 80
COIN_RADIUS = 15
SPEED_SCALE = 6.0     # Speed sensitivity: increase if movement is too slow
COIN_FALL_SPEED = 2.0
# ================================================

class Coin:
    """Falling coin object"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS
    
    def update(self):
        """Update coin position"""
        self.y += COIN_FALL_SPEED
    
    def draw(self, screen):
        """Draw coin as yellow circle"""
        pygame.draw.circle(screen, (255, 215, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius - 3)
    
    def is_off_screen(self):
        """Check if coin fell off screen"""
        return self.y > SCREEN_H

def find_lsl_stream():
    """Find BCI control signal stream from OpenViBE"""
    print(f"Scanning for LSL stream (Target: {STREAM_NAME})...")
    
    streams = resolve_streams(wait_time=1.0)
    
    for s in streams:
        if s.name() == STREAM_NAME:
            print(f">>> Successfully connected to stream: {s.name()} <<<")
            return StreamInlet(s)
            
    print(f"[Error] Stream '{STREAM_NAME}' not found!")
    print("Please check:\n1. Is OpenViBE running and clicked Play?\n2. Is the Python box stream name correct?")
    sys.exit(1)

def check_collision(player_x, player_y, coin):
    """Check if player catches coin"""
    # Player bounding box: approximate player center
    player_left = player_x - PLAYER_WIDTH // 2
    player_right = player_x + PLAYER_WIDTH // 2
    player_top = player_y
    player_bottom = player_y + PLAYER_HEIGHT
    
    # Check if coin center is within player bounds
    coin_caught = (player_left <= coin.x <= player_right and
                   player_top <= coin.y <= player_bottom)
    return coin_caught

def main():
    # 1. Connect to BCI
    inlet = find_lsl_stream()

    # 2. Initialize game
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("BCI Coin Catcher - Motor Imagery Control")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("arial", 36, bold=True)
    font_medium = pygame.font.SysFont("arial", 24)
    font_small = pygame.font.SysFont("arial", 18)

    # Load player image
    try:
        player_image = pygame.image.load("res/xiaohui.png")
        # Scale image to fit player dimensions
        player_image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))
    except pygame.error:
        print("[Warning] Could not load res/xiaohui.png, using colored rectangle instead")
        player_image = None

    # 3. Game variables initialization
    player_x = SCREEN_W // 2
    player_y = SCREEN_H - 100
    
    coins = []
    score = 0
    coin_spawn_timer = 0
    coin_spawn_interval = 50  # Spawn new coin every 30 frames (~0.5 seconds at 60 FPS)
    
    running = True
    while running:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- BCI data reading ---
        sample, timestamp = inlet.pull_sample(timeout=0.0)

        raw_val = 0.0
        if sample:
            raw_val = sample[0]
            
            # [Physics] Update player position (negative = left, positive = right)
            player_x += raw_val * SPEED_SCALE

        # --- Boundary constraints ---
        if player_x < PLAYER_WIDTH // 2:
            player_x = PLAYER_WIDTH // 2
        if player_x > SCREEN_W - PLAYER_WIDTH // 2:
            player_x = SCREEN_W - PLAYER_WIDTH // 2

        # --- Coin spawning ---
        coin_spawn_timer += 1
        if coin_spawn_timer >= coin_spawn_interval:
            # Spawn new coin at random x position
            coin_x = random.randint(COIN_RADIUS + 20, SCREEN_W - COIN_RADIUS - 20)
            coins.append(Coin(coin_x, -COIN_RADIUS))
            coin_spawn_timer = 0

        # --- Update coins ---
        coins_to_remove = []
        for i, coin in enumerate(coins):
            coin.update()
            
            # Check collision with player
            if check_collision(player_x, player_y, coin):
                score += 1
                coins_to_remove.append(i)
            # Check if coin fell off screen
            elif coin.is_off_screen():
                coins_to_remove.append(i)
        
        # Remove caught or fallen coins
        for i in reversed(coins_to_remove):
            coins.pop(i)

        # --- Rendering ---
        screen.fill((25, 25, 35))  # Dark blue background
        
        # Draw sky gradient effect (optional visual enhancement)
        pygame.draw.line(screen, (50, 50, 100), (0, SCREEN_H - 150), (SCREEN_W, SCREEN_H - 150), 2)
        
        # Draw all coins
        for coin in coins:
            coin.draw(screen)
        
        # Draw player
        if player_image:
            screen.blit(player_image, (int(player_x - PLAYER_WIDTH // 2), int(player_y)))
        else:
            # Fallback: draw colored rectangle
            pygame.draw.rect(screen, (100, 200, 50), 
                           (int(player_x - PLAYER_WIDTH // 2), int(player_y), 
                            PLAYER_WIDTH, PLAYER_HEIGHT))
        
        # Draw score
        score_text = font_large.render(f"Score: {score}", True, (255, 215, 0))
        screen.blit(score_text, (20, 20))
        
        # Draw instructions
        info_text = font_small.render(f"BCI Output: {raw_val:.3f}", 
                                     True, (200, 200, 200))
        screen.blit(info_text, (20, SCREEN_H - 40))
        
        hint_left = font_small.render("Left Hand <- Move Left", True, (100, 150, 255))
        hint_right = font_small.render("Right Hand -> Move Right", True, (100, 150, 255))
        screen.blit(hint_left, (20, 60))
        screen.blit(hint_right, (SCREEN_W - 250, 60))
        
        # Draw active coins count
        coins_text = font_small.render(f"Coins falling: {len(coins)}", True, (200, 200, 200))
        screen.blit(coins_text, (SCREEN_W - 200, SCREEN_H - 40))

        pygame.display.flip()
        clock.tick(60)  # Lock at 60 FPS

    pygame.quit()
    print(f"Game Over! Final Score: {score}")

if __name__ == "__main__":
    main()

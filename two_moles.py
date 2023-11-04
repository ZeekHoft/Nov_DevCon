import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
DOT_SIZE = 80
BACKGROUND_COLOR = (139, 115, 85)
FPS = 60
MIN_DISTANCE = 100  # Minimum distance between dots
GAME_DURATION = 10  # Game duration in seconds

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Click the Dots!")

# Initialize score
score = 0

# Load the image for the dot and scale it to the desired size
dot_image = pygame.image.load("hole.png")
dot_image = pygame.transform.scale(dot_image, (DOT_SIZE, DOT_SIZE))

# Load the image for the hit dot
hit_image = pygame.image.load("hit.png")
hit_image = pygame.transform.scale(hit_image, (DOT_SIZE, DOT_SIZE))

# Load the image for the mole dot
mole_image = pygame.image.load("mole.png")
mole_image = pygame.transform.scale(mole_image, (DOT_SIZE, DOT_SIZE))

# Load the image for the bad mole dot that deducts points
bad_mole_image = pygame.image.load("mole3.png")
bad_mole_image = pygame.transform.scale(bad_mole_image, (DOT_SIZE, DOT_SIZE))

# Create a font for the score and timer display
font = pygame.font.Font(None, 36)

# Set the initial spawn rate and counter
spawn_rate = 0.01  # Adjust this value to change the spawn rate (higher values mean more frequent spawns)
spawn_counter = 0

# Store the dots and their states (0 for normal, 1 for hit, 2 for mole that increases points, 3 for bad mole that deducts points)
dots = [{'position': (100, 100), 'state': 0, 'start_time': time.time()}]

# Function to check if a new dot is too close to existing dots
def is_too_close(new_dot, existing_dots):
    for dot in existing_dots:
        x1, y1 = new_dot['position']
        x2, y2 = dot['position']
        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        if distance < MIN_DISTANCE:
            return True
    return False

# Start the game timer
start_time = time.time()

# Main game loop
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for dot in dots:
                dot_x, dot_y = dot['position']
                distance = ((dot_x - mouse_x) ** 2 + (dot_y - mouse_y) ** 2) ** 0.5
                if distance <= DOT_SIZE / 2:
                    if dot['state'] == 2:  # Existing mole that increases points
                        dot['state'] = 1
                        dot['start_time'] = time.time()
                        score += 1
                    elif dot['state'] == 3:  # New mole that deducts points
                        dot['state'] = 1
                        dot['start_time'] = time.time()
                        score = max(0, score - 1)

    screen.fill(BACKGROUND_COLOR)

    for dot in list(dots):
        dot_x, dot_y = dot['position']
        if dot['state'] == 0:
            if time.time() - dot['start_time'] >= 2:
                dot['state'] = 2
                dot['start_time'] = time.time()
            else:
                screen.blit(dot_image, (dot_x - DOT_SIZE / 2, dot_y - DOT_SIZE / 2))
        elif dot['state'] == 1:
            if time.time() - dot['start_time'] >= 1:
                dots.remove(dot)
            else:
                screen.blit(hit_image, (dot_x - DOT_SIZE / 2, dot_y - DOT_SIZE / 2))
        elif dot['state'] == 2:
            if time.time() - dot['start_time'] >= 3:
                dots.remove(dot)
            else:
                screen.blit(mole_image, (dot_x - DOT_SIZE / 2, dot_y - DOT_SIZE / 2))
        elif dot['state'] == 3:
            if time.time() - dot['start_time'] >= 3:
                dots.remove(dot)
            else:
                screen.blit(bad_mole_image, (dot_x - DOT_SIZE / 2, dot_y - DOT_SIZE / 2))

        # Adjust the spawn rate here
        if spawn_counter >= 1 / spawn_rate:
            if len(dots) < 5:
                # Existing mole
                new_dot = {'position': (random.randint(DOT_SIZE, WIDTH - DOT_SIZE), random.randint(DOT_SIZE, HEIGHT - DOT_SIZE)), 'state': 0, 'start_time': time.time()}
                while is_too_close(new_dot, dots):
                    new_dot = {'position': (random.randint(DOT_SIZE, WIDTH - DOT_SIZE), random.randint(DOT_SIZE, HEIGHT - DOT_SIZE)), 'state': 0, 'start_time': time.time()}
                dots.append(new_dot)
                # New mole that deducts points
                new_dot = {'position': (random.randint(DOT_SIZE, WIDTH - DOT_SIZE), random.randint(DOT_SIZE, HEIGHT - DOT_SIZE)), 'state': 3, 'start_time': time.time()}
                while is_too_close(new_dot, dots):
                    new_dot = {'position': (random.randint(DOT_SIZE, WIDTH - DOT_SIZE), random.randint(DOT_SIZE, HEIGHT - DOT_SIZE)), 'state': 3, 'start_time': time.time()}
                dots.append(new_dot)
            spawn_counter = 0
        else:
            spawn_counter += 1

    # Display the score at the top left corner
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Calculate the remaining time
    remaining_time = max(0, GAME_DURATION - (time.time() - start_time))
    timer_text = font.render(f"Time: {int(remaining_time)}", True, (0, 0, 0))
    screen.blit(timer_text, (WIDTH - 100, 10))

    # End the game when the timer runs out
    if remaining_time == 0:
        running = False

    pygame.display.update()

    clock.tick(FPS)

# Game over screen
game_over_text = font.render(f"Game Over! Your Score: {score}", True, (0, 0, 0))
game_over_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))

screen.fill(BACKGROUND_COLOR)
screen.blit(game_over_text, game_over_rect)


# Display "Thank you for playing" text
thank_you_text = font.render("PAKYU YOURE GAY", True, (0, 0, 0))
thank_you_rect = thank_you_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
screen.blit(thank_you_text, thank_you_rect)

pygame.display.update()

# Wait for a moment before exiting
pygame.time.delay(3000)

# Quit Pygame
pygame.quit()
sys.exit()

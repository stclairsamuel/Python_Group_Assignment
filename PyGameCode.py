import pygame
import sys
import math
import numpy as np

pygame.init()

keycodes = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
}

acceleration = 4000
maxSpeed = 800
speed = maxSpeed
dashSpeed = 800
xVel = 0
yVel = 0
drag = 0.9

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLOR = (200, 230, 83)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Text Display")

# Create a font object
font = pygame.font.SysFont("Times New Roman", 50) # Use the default system font with size 50

# Render the text surface
text_surface = font.render('Text is showing in the window!', True, COLOR)
text_rect = text_surface.get_rect()
text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

xPos = SCREEN_WIDTH / 2
yPos = SCREEN_HEIGHT / 2

clock = pygame.time.Clock()

# Game loop
running = True

yInput = 0
xInput = 0

getInput = True

isDashing = False
dashTime = 0.2
dashTimer = 0



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    inpList = pygame.key.get_pressed()

    yInput = 0
    xInput = 0

    if (isDashing):
        getInput = False
    else:
        getInput = True

    if (getInput):
        if (inpList[pygame.K_w]):
            yInput += 1
        if (inpList[pygame.K_s]):
            yInput -= 1
        if (inpList[pygame.K_a]):
            xInput -= 1
        if (inpList[pygame.K_d]):
            xInput += 1
    
        if (inpList[pygame.K_LSHIFT]):
            isDashing = True

    if (isDashing and dashTimer == 0):
        isDashing = False

        
    mag = math.sqrt(xInput * xInput + yInput * yInput)
    dirVector = [xInput, yInput]
    if mag > 0:
        dirVector = [xInput / mag, yInput / mag]
    
    if (isDashing):
        xVel += dirVector[0] * dashSpeed
        yVel += dirVector[1] * dashSpeed

    dt = clock.tick() / 1000.0

    yVel += dirVector[1] * acceleration * dt
    xVel += dirVector[0] * acceleration * dt

    if (xInput == 0 and yInput == 0):
        xVel = xVel * (drag ** (dt * 60))
        yVel = yVel * (drag ** (dt * 60))
    if (speed > maxSpeed):
        speed = speed * (0.9 ** (dt * 60))

    magnitude = (math.sqrt(yVel * yVel + xVel * xVel))
    if (magnitude > maxSpeed):
        xVel = (xVel / magnitude) * speed
        yVel = (yVel / magnitude) * speed
    
    

    # Drawing
    screen.fill(WHITE) # Fill screen with white background
    screen.blit(text_surface, text_rect) # Draw the text

    yPos -= yVel * dt
    xPos += xVel * dt
    posVector = [xPos, yPos]
    pygame.draw.circle(screen, COLOR, posVector, 20)

    # Update the display
    pygame.display.update()

    # Timers

    if (dashTimer > 0):
        dashTimer -= dt
    else:
        dashTimer = 0


# Quit Pygame
pygame.quit()
sys.exit()

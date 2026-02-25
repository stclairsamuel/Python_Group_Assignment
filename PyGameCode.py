import pygame
import sys
import math
import numpy as np
import random
import os

pygame.init()

keycodes = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
}

acceleration = 4000
maxSpeed = 400
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

imagePath = os.path.join("Images", "Background_Image_Test-export.png")

backgroundImage = pygame.image.load(imagePath).convert_alpha()

width = backgroundImage.get_width()
height = backgroundImage.get_height()
scale = 1

bigBgImage = pygame.transform.smoothscale(backgroundImage, (width * scale, height * scale)).convert_alpha()

imageRect = backgroundImage.get_rect()

xPos = SCREEN_WIDTH / 2
yPos = SCREEN_HEIGHT / 2

running = True

clock = pygame.time.Clock()

yInput = 0
xInput = 0

getInput = True

isDashing = False
dashTime = 0.2
dashTimer = 0

dashCdTime = 0.2
dashCdTimer = 0

dashDir = [0, 0]

magnitude = 0

inpList = []

def StartDash():
    global isDashing, dashTimer, dashDir

    isDashing = True
    dashTimer = dashTime
    normedXVel = xVel/magnitude
    normedYVel = yVel/magnitude
    dashDir = [normedXVel, normedYVel]

def GetInput():

    global xInput, yInput, running, isDashing, dashTimer, dashDir, dashCdTimer, inpList

    inpList = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if (inpList[pygame.K_w]):
            yInput += 1
        if (inpList[pygame.K_s]):
            yInput -= 1
        if (inpList[pygame.K_a]):
            xInput -= 1
        if (inpList[pygame.K_d]):
            xInput += 1
        
        if (inpList[pygame.K_LSHIFT] and not dashCdTimer > 0):
            StartDash()

# Game Running

while running:

    magnitude = math.sqrt((xVel * xVel) + (yVel * yVel))

    if (isDashing):
        getInput = False
    else:
        getInput = True

    if (getInput):
        GetInput()

    if (isDashing and dashTimer == 0):
        isDashing = False
        dashCdTimer = dashCdTime
    
    if (isDashing): 
        xVel = dashDir[0] * dashSpeed
        yVel = dashDir[1] * dashSpeed

    else:
        mag = math.sqrt(xInput * xInput + yInput * yInput)
        dirVector = [xInput, yInput]
        if mag > 0:
            dirVector = [xInput / mag, yInput / mag]
        
        if (isDashing):
            xVel += dirVector[0] * dashSpeed
            yVel += dirVector[1] * dashSpeed
    
    print(magnitude)

    dt = clock.tick() / 1000.0

    yVel += dirVector[1] * acceleration * dt
    xVel += dirVector[0] * acceleration * dt

    if (xInput == 0 and yInput == 0):
        xVel = xVel * (drag ** (dt * 1000))
        yVel = yVel * (drag ** (dt * 1000))
    if (speed > maxSpeed):
        speed = speed * (0.9 ** (dt * 60))

    magnitude = (math.sqrt(yVel * yVel + xVel * xVel))
    if (magnitude > maxSpeed and not isDashing):
        xVel = (xVel / magnitude) * speed
        yVel = (yVel / magnitude) * speed
    
    

    # Drawing
    screen.fill(WHITE) # Fill screen with white background

    screen.blit(bigBgImage, imageRect)

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
    
    if (dashCdTimer > 0):
        dashCdTimer -= dt
    else:
        dashCdTimer = 0


# Quit Pygame
pygame.quit()
sys.exit()

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
drag = 0.995

maxHealth = currentHealth = 5

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (200, 230, 83)
RED = (255, 0, 0)

playerColor = GREEN



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

playerHitbox = pygame.Rect(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 10, 10)

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

iFrameTime = 0.2
iFrameTimer = 0

dashDir = [0, 0]

magnitude = 0

inpList = []

projectiles = []

spawnProjTime = 1
spawnProjTimer = 0

projSize = 10

class Projectile:
    def __init__(self):

        if (random.choice([True, False])):
            self.xPos = random.randint(0, SCREEN_WIDTH)
            self.yPos = random.choice([0, SCREEN_HEIGHT])
        else:
            self.xPos = random.choice([0, SCREEN_WIDTH])
            self.yPos = random.randint(0, SCREEN_HEIGHT)

        self.xVel = 0
        self.yVel = 0

        self.size = 10

        self.acceleration = 300

        self.drag = 0.9

        self.lifeTime = self.lifeTimer = 10
    
    def Move(self):
        global xPos, yPos
        pPos = [xPos, yPos]
        myPos = [self.xPos, self.yPos]

        xDist = (pPos[0] - myPos[0])
        yDist = (pPos[1] - myPos[1])
        totalDist = math.sqrt(math.pow(xDist, 2) + math.pow(yDist, 2))

        dirToPlayer = [xDist / totalDist, yDist / totalDist]

        self.xVel += dirToPlayer[0] * self.acceleration * dt
        self.yVel += dirToPlayer[1] * self.acceleration * dt

        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt
    
    def CheckCollision(self):
        global playerHitbox

        myPos = [self.xPos, self.yPos]

        myHitbox = pygame.Rect(myPos[0], myPos[1], self.size, self.size)

        return (pygame.Rect.colliderect(myHitbox, playerHitbox))

def StartDash():
    global isDashing, dashTimer, dashDir

    isDashing = True
    dashTimer = dashTime
    normedXVel = xVel/magnitude
    normedYVel = yVel/magnitude
    dashDir = [normedXVel, normedYVel]

def GetInput():
    global xInput, yInput, running, isDashing, dashTimer, dashDir, dashCdTimer, inpList

    xInput = 0
    yInput = 0

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

def Die():
    pygame.quit()

def TakeDamage():
    global iFrameTimer, currentHealth

    currentHealth -= 1

    iFrameTimer = iFrameTime

    if (currentHealth <= 0):
        Die()


def SpawnProjectile():
    newProjectile = Projectile()

    projectiles.append(newProjectile)

def CreateHealthBar():
    global currentHealth

    size = 15
    horizontalDistance = 40

    position1 = [40, 40]

    for i in range(currentHealth):
        pygame.draw.circle(screen, RED, [position1[0] + (i * horizontalDistance), position1[1]], size)
    

# Game Running

while running:

    if (getInput):
        GetInput()

    magnitude = math.sqrt((xVel * xVel) + (yVel * yVel))

    if (isDashing):
        getInput = False
    else:
        getInput = True

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
    
    playerHitbox = pygame.Rect(xPos, yPos, 10, 10)

    # Drawing
    screen.fill(WHITE) # Fill screen with white background

    screen.blit(bigBgImage, imageRect)

    yPos -= yVel * dt
    xPos += xVel * dt
    posVector = [xPos, yPos]

    if (iFrameTimer > 0):
        playerColor = RED
    else:
        playerColor = GREEN

    pygame.draw.circle(screen, playerColor, posVector, 20)

    for p in projectiles:
        pygame.draw.circle(screen, RED, [p.xPos, p.yPos], p.size)
        p.Move()
    
    for p in projectiles:
        p.lifeTimer -= dt
        outOfBounds = (not (0 < xPos and xPos < SCREEN_WIDTH) or not (0 < yPos and yPos < SCREEN_HEIGHT))
        if (p.lifeTimer <= 0 or outOfBounds):
            projectiles.remove(p)
    
        if (p.CheckCollision() and iFrameTimer == 0):
            TakeDamage()
    
    # Timers

    if (dashTimer > 0):
        dashTimer -= dt
    else:
        dashTimer = 0
    
    if (dashCdTimer > 0):
        dashCdTimer -= dt
    else:
        dashCdTimer = 0

    if (spawnProjTimer > 0):
        spawnProjTimer -= dt
    else:
        spawnProjTimer = spawnProjTime
        SpawnProjectile()
    
    if (iFrameTimer > 0):
        iFrameTimer -= dt
    else:
        iFrameTimer = 0

    CreateHealthBar()
    
    # Update the display
    pygame.display.update()
    
    
        


# Quit Pygame
pygame.quit()
sys.exit()

import pygame
import sys
import math
import numpy as np
import random
import os
import json
import MapGen
import PlayerScript
import ObstaclesScript

pygame.init()

keycodes = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
}

maxHealth = currentHealth = 5

dt = 0

tileSize = 64

mapPath = "MapFiles/RandomMap.json"
mapFile = open(mapPath, "r")
mapContents = json.load(mapFile)

SCREEN_WIDTH = len(mapContents[0]) * tileSize
SCREEN_HEIGHT = len(mapContents) * tileSize

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

running = True

clock = pygame.time.Clock()

iFrameTime = 0.2
iFrameTimer = 0

dashDir = [0, 0]

magnitude = 0

inpList = []

projectiles = []

spawnProjTime = 1
spawnProjTimer = 0

projSize = 10

def ReflectVector(vectorToReflect, normal):
    # R = V - 2(V DOT N)N

    reflectedVector = [0, 0]

    dotProduct = vectorToReflect[0] * normal[0] + vectorToReflect[1] * normal[1]


    reflectedVector[0] - (2 * dotProduct * normal[0])
    reflectedVector[1] - (2 * dotProduct * normal[0])

    return reflectedVector


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
    
    def CheckCollision(self):
        global playerHitbox

        myPos = [self.xPos, self.yPos]

        myHitbox = pygame.Rect(myPos[0], myPos[1], self.size, self.size)

        return (pygame.Rect.colliderect(myHitbox, playerHitbox))


                

    #def StartDash(self):


    
    #def TakeDamage(self):

    
    #def Die(self):

player = PlayerScript.Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)




    
    

map = MapGen.Map()


map.MakeNewRandomMap()

obstacles = []
for t in map.tileList:
    if (t.tileLetter == "x" or t.tileLetter == "z"):
        obstacles.append(ObstaclesScript.Obstacle(t.hitbox[0], t.hitbox[1], t.hitbox[2], t.hitbox[3]))

#mapFile = "TestMap"
#map.GenerateMap(mapFile)

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

    imagePath = os.path.join("Images", "PygameHeart.png")

    heartImage = pygame.image.load(imagePath).convert_alpha()

    scale = 2
    width = heartImage.get_width()
    height = heartImage.get_height()

    pygame.draw.rect(screen, WHITE, (30, 35, 210, 40))

    biggerHeart = pygame.transform.scale(heartImage, (width * scale, height * scale)).convert_alpha()

    horizontalDistance = 40

    position1 = [40, 40]

    for i in range(currentHealth):
        screen.blit(biggerHeart, (position1[0] + (i * horizontalDistance), position1[1]))


def Timers():
    global dashTimer, spawnProjTimer, iFrameTimer

    #if (dashTimer > 0):
    #    player.dashTimer -= dt
    #else:
    #    player.dashTimer = 0
    
    #if (dashCdTimer > 0):
    #    player.dashCdTimer -= dt
    #else:
    #    player.dashCdTimer = 0

    if (spawnProjTimer > 0):
        spawnProjTimer -= dt
    else:
        spawnProjTimer = spawnProjTime
        SpawnProjectile()
    
    if (iFrameTimer > 0):
        player.iFrameTimer -= dt
    else:
        player.iFrameTimer = 0

def DrawMap():
    for t in map.tileList:
        tile = t.DrawTile(tileSize)
        screen.blit(tile[0], tile[1])

# Game Running

while running:
    dt = clock.tick() / 1000.0

    if (player.getInput):
        player.GetInput()
    
    player.Move(dt, obstacles)

    # Drawing
    screen.fill(WHITE) # Fill screen with white background

    DrawMap()

    if (iFrameTimer > 0):
        playerColor = RED
    else:
        playerColor = GREEN

    pygame.draw.circle(screen, playerColor, [player.xPos, player.yPos], 20)
    
    '''
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
    '''
    
    # Timers
    Timers()

    CreateHealthBar()

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()

import pygame
import sys
import math
import numpy as np
import random
import os
import json
import MapGen2
import PlayerScript
import ObstaclesScript
import PathfindingScript
import EnemyScripts

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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

player = PlayerScript.Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

mapXSize = 8
mapYSize = 6

startRoom = (0, 3)

map = MapGen2.Map(mapXSize, mapYSize, 8)

map.MakeNewMap()

map.currentRoom.GenerateMap(player)

#room = MapGen.Room()

#room.MakeNewRandomMap()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (200, 230, 83)
RED = (255, 0, 0)

playerColor = GREEN

found_room = next((room for room in map.rooms if room.mapPos == (map.currentRoom.mapPos[0], map.currentRoom.mapPos[1])), None)

if (found_room):
    room = found_room
else:
    print("fail")

obstacles = []
for t in room.tileList:
    if (t.tileLetter == "x" or t.tileLetter == "z"):
        obstacles.append(ObstaclesScript.Obstacle(t.hitbox[0], t.hitbox[1], t.hitbox[2], t.hitbox[3]))

# Set up the display

scale = 1

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

obstacles = []
for t in room.tileList:
    if (t.tileLetter == "x" or t.tileLetter == "z"):
        obstacles.append(ObstaclesScript.Obstacle(t.hitbox[0], t.hitbox[1], t.hitbox[2], t.hitbox[3]))

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
    global spawnProjTimer, iFrameTimer

    if (player.dashCdTimer > 0):
        player.dashCdTimer -= dt
    else:
        player.dashCdTimer = 0
    
    if (player.dashTimer > 0):
        player.dashTimer -= dt
    else:
        player.dashTimer = 0

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
    for t in map.currentRoom.tileList:
        t.DrawTile(screen)
    #for d in map.currentRoom.doors:
    #    pygame.draw.rect(screen, WHITE, d.hitbox)

# Game Running

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    dt = clock.tick(60) / 1000.0

    player.getInput = not player.isDashing

    if (player.getInput):
        player.GetInput()
    
    player.Move(dt, map.currentRoom.obstacles)

    myHitbox = pygame.Rect(player.xPos, player.yPos, player.hitboxSize, player.hitboxSize)

    # Drawing
    screen.fill(WHITE) # Fill screen with white background

    DrawMap()

    obstacleRects = list(o.hitbox for o in map.currentRoom.obstacles)

    for i in map.currentRoom.enemyGroup.activeEnemies:
        color = RED

        i.FindPathToTarget(pygame.Rect(player.xPos, player.yPos, 15, 15), obstacleRects)
        i.Move(dt, map.currentRoom)

        pygame.draw.circle(screen, RED, (i.xPos, i.yPos), 10)

    #for i in (myAlgo.path):
        #pygame.draw.circle(screen, RED, (32 + i[0] * 64, 32 + i[1] * 64), 20)

    #pygame.draw.circle(screen, GREEN, (32 + myAlgo.endPos[0] * 64, 32 + myAlgo.endPos[1] * 64), 20)

    if (iFrameTimer > 0):
        playerColor = RED
    else:
        playerColor = GREEN

    pygame.draw.circle(screen, playerColor, [player.xPos, player.yPos], 20)

    map.currentRoom.CheckDoorCollisions(myHitbox, player)
    
    # Timers
    Timers()

    CreateHealthBar()

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()

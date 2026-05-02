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
import ProjectileScript
import pynput
from pynput import mouse
import UpgradesScript
import Rendering

pygame.init()

keycodes = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
}

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

map = MapGen2.Map(mapXSize, mapYSize, 6)

player.map = map

newUpgradeTracker = UpgradesScript.upgrade_tracker(player)

map.upgradesTracker = newUpgradeTracker
player.upgradesTracker = newUpgradeTracker


map.MakeNewMap()

map.currentRoom.GenerateMap(player)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (200, 230, 83)
RED = (255, 0, 0)

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

ts = 0

def ReflectVector(vectorToReflect, normal):
    # R = V - 2(V DOT N)N

    reflectedVector = [0, 0]

    dotProduct = vectorToReflect[0] * normal[0] + vectorToReflect[1] * normal[1]


    reflectedVector[0] - (2 * dotProduct * normal[0])
    reflectedVector[1] - (2 * dotProduct * normal[0])

    return reflectedVector

obstacles = []
for t in room.tileList:
    if (t.tileLetter == "x" or t.tileLetter == "z"):
        obstacles.append(ObstaclesScript.Obstacle(t.hitbox[0], t.hitbox[1], t.hitbox[2], t.hitbox[3]))

def DrawMap():
    for t in map.currentRoom.tileList:
        t.Render(screen)

# Game Running

def StopTime(timeStop):
    global ts
    ts = timeStop

pygame.event.set_grab(True)

class cursor:
    def __init__(self):
        self.xPos = 0
        self.yPos = 0

        self.xOff = 10
        self.yOff = 10

        self.scale = 0.5

        self.isClick = False

        filePath = "CursorFrames"

        self.spriteRenderer = Rendering.sprite_renderer(self)
        self.animator = Rendering.animator(filePath, self.spriteRenderer)

        self.spriteRenderer.ChangeSize(self.scale)

        self.sortingLayer = 1

    def Update(self, dt):
        mousePos = pygame.mouse.get_pos()

        self.xPos, self.yPos = mousePos[0] + self.xOff, mousePos[1] + self.yOff
    
    def Click(self):
        self.animator.SwitchAnimation("click")
    
    def Release(self):
        self.animator.SwitchAnimation("release")
    

    def Render(self, dt):
        self.spriteRenderer.Render(dt)

class game_handler:
    def __init__(self):
        self.timeStop = 0

        self.cursor = cursor()
    
    def StopTime(self, ts):
        self.timeStop = ts
    
    def Timers(self, dt):
        if (self.timeStop > 0):
            self.timeStop -= dt
        else:
            self.timeStop = 0

map.handler = game_handler()

for r in map.rooms:
    r.AddGameObject(player)
    r.AddGameObject(map.handler.cursor)

pygame.mouse.set_visible(False)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if (event.type == pygame.MOUSEBUTTONDOWN):
            if (event.button == 1):
                player.Attack()
                map.handler.cursor.Click()

        if (event.type == pygame.MOUSEBUTTONUP):
            if (event.button == 1):
                map.handler.cursor.Release()
    
    dt = clock.tick(60) / 1000.0

    map.handler.Timers(dt)

    if (map.handler.timeStop > 0):
        dt = 0
    
    # Drawing
    screen.fill(WHITE) # Fill screen with white background

    DrawMap()

    map.currentRoom.UpdateObjects(dt)
    map.currentRoom.RenderObjects(dt)

    obstacleRects = list(o.hitbox for o in map.currentRoom.obstacles)
    
    for p in map.currentRoom.activeEnemyProjectiles:
        color = BLACK

        p.Move(dt)
        p.CheckHit()

        pygame.draw.circle(screen, BLACK, (p.xPos, p.yPos), 5)

    if (iFrameTimer > 0):
        playerColor = RED
    else:
        playerColor = GREEN

    player.animator.Update(dt)

    if (map.currentRoom.enemyGroup):
        if (len(map.currentRoom.enemyGroup.activeEnemies) == 0 and not map.currentRoom.roomCleared):
            map.currentRoom.ClearRoom()
    
    map.upgradesTracker.Update(map.currentRoom, dt)

    player.CreateHealthBar()
    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()

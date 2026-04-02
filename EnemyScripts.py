import pygame
import sys
import math
import numpy as np
import random
import os
import json
import PathfindingScript
import ObstaclesScript
import copy
import PlayerScript
import MapGen2
import ProjectileScript

class enemy_group:
    def __init__(self, room, player):
        self.spawnableTiles = []
        self.enemiesPerTile = 10

        self.target = player

        self.minSpawnDist = 5

        self.activeEnemies = []

        room.enemyGroup = self

        self.GetSpawningTiles(room)

        if (not room.roomCleared):
            self.SpawnEnemies()

        self.obstacleRects = list(o.hitbox for o in room.obstacles)

    def GetSpawningTiles(self, room):
        self.spawnableTiles = []
        if (not room.parentRoom):
            return()
        for y in range(len(room.info)):
            for x in range(len(room.info[y])):
                if (room.info[y][x] != "o"):
                    continue
                myAlgo = PathfindingScript.AStarMap(room.info, room.exitDoor.entrancePos, (x, y))
                myAlgo.MakeAlgo()
                if (len(myAlgo.path) > self.minSpawnDist):
                    self.spawnableTiles.append((x, y))
        print(len(self.spawnableTiles))
    
    def SpawnEnemies(self):
        enemiesToSpawn = int(np.round(len(self.spawnableTiles) / self.enemiesPerTile))

        for i in range(enemiesToSpawn):
            newEnemy = enemy(self, self.target)
            self.activeEnemies.append(newEnemy)
        

class enemy:
    def __init__(self, group, player):
        self.acceleration = 3000

        RED = (255, 0, 0)
        WHITE = (255, 255, 255)

        self.color = RED

        self.drag = 0.999

        self.idealRange = 125
        self.rangeSlack = 75
        self.withinRange = False
        self.tooClose = False

        self.hasSeenPlayer = False

        self.maxSpeed = 300
        self.speed = 0

        self.xVel = 0
        self.yVel = 0

        self.group = group

        self.target = player

        self.currentHealth = self.maxHealth = 4
        self.mySpawnTile = random.choice(group.spawnableTiles)

        self.hitboxSize = 30

        self.xPos = self.mySpawnTile[0] * 64 + 32
        self.yPos = self.mySpawnTile[1] * 64 + 32

        self.hitbox = pygame.Rect(self.xPos - self.hitboxSize/2, self.yPos - self.hitboxSize/2, self.hitboxSize, self.hitboxSize)

        self.canSeePlayer = False

        self.shootCooldownTime = 3
        self.shootCooldownTimer = 1

        self.inaccuracy = 15

        self.stunTimer = self.stunTime = 0
        
        self.drag = 0.98

        self.isStrafing = False

        self.hitbox = pygame.Rect(self.xPos - self.hitboxSize/2, self.yPos - self.hitboxSize/2, self.hitboxSize, self.hitboxSize)

        self.runTimer = 0
        self.runTime = 2
    
    def FindPathToTarget(self, target, obstacles):
        raycast = PathfindingScript.Raycast((self.xPos, self.yPos), (self.target.xPos, self.target.yPos), target, obstacles)

        self.canSeePlayer = raycast.hit
        if (self.canSeePlayer):
            self.withinRange = (raycast.distance < self.idealRange + self.rangeSlack)
            self.tooClose = (raycast.distance < self.idealRange - self.rangeSlack)

    def Move(self, dt, currentRoom):
        pXPos = self.target.xPos
        pYPos = self.target.yPos

        dirToMove = (0, 0)

        if (self.runTimer > 0):
            self.idealRange = 200
            self.rangeSlack = 25
        else:
            self.idealRange = 125
            self.rangeSlack = 75

        if (self.canSeePlayer):
            targetPos = (pXPos, pYPos)

            if (self.hasSeenPlayer == False): self.hasSeenPlayer = True

            if (not self.withinRange):
                dirToMove = PlayerScript.NormalizeVector((targetPos[0] - self.xPos, targetPos[1] - self.yPos))

            if (self.tooClose):
                dirToMove = PlayerScript.NormalizeVector((self.xPos - targetPos[0], self.yPos - targetPos[1]))
            
            #if (self.shootCooldownTimer > 0.5):
                #dirToMove = (dirToMove[1], -dirToMove[0])

        elif (self.hasSeenPlayer):
            myAlgo = PathfindingScript.AStarMap(currentRoom.info, (int(pXPos / 64), int(pYPos / 64)), (int(self.xPos / 64), int(self.yPos / 64)))
            myAlgo.MakeAlgo()

            #for p in myAlgo.path:
                #pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (p[0] * 64 + 32, p[1] * 62 + 32), 15)

            try:
                nextCoord = myAlgo.path[1]
                nextPos = (nextCoord[0] * 64 + 32, nextCoord[1] * 64 + 32)

                dirToMove = PlayerScript.NormalizeVector((nextPos[0] - self.xPos, nextPos[1] - self.yPos))
            except IndexError:
                pass

        enemyRects = [e.hitbox for e in currentRoom.enemyGroup.activeEnemies if e != self]

        for e in enemyRects:
            if (pygame.Rect.colliderect(self.hitbox, e)):
                dirToMove = PlayerScript.NormalizeVector((self.hitbox[0] - e[0], self.hitbox[1] - e[1]))
        
        lastXVel = self.xVel
        lastYVel = self.yVel

        isStunned = self.stunTimer > 0
        
        if (not isStunned):
            self.xVel += dirToMove[0] * self.acceleration * dt
            self.yVel += dirToMove[1] * self.acceleration * dt
            self.color = (255, 0, 0)
        else:
            self.xVel *= (self.drag ** (dt * 1000))
            self.yVel *= (self.drag ** (dt * 1000))
            self.color = (255, 255, 255)

        if (PlayerScript.Magnitude([lastXVel, lastYVel]) > self.maxSpeed or dirToMove == (0, 0)):
                self.xVel = self.xVel * (self.drag ** (dt * 1000))
                self.yVel = self.yVel * (self.drag ** (dt * 1000))
        
        speed = PlayerScript.Magnitude([self.xVel, self.yVel])

        if (speed > self.maxSpeed and PlayerScript.Magnitude([lastXVel, lastYVel]) <= self.maxSpeed):
            self.xVel = (self.xVel / speed) * self.maxSpeed
            self.yVel = (self.yVel / speed) * self.maxSpeed

        obstacleRects = self.group.obstacleRects.copy()
        
        #for o in obstacleRects:
            #pygame.draw.rect(pygame.display.get_surface(), (255, 255, 255), o)

        predictedX = self.xPos + self.xVel * dt
        predictedY = self.yPos + self.yVel * dt

        predictedXHitbox = pygame.Rect(predictedX - self.hitboxSize/2, self.yPos - self.hitboxSize/2, self.hitboxSize, self.hitboxSize)
        predictedYHitbox = pygame.Rect(self.xPos - self.hitboxSize/2, predictedY - self.hitboxSize/2, self.hitboxSize, self.hitboxSize)

        skinWidth = 0.02

        for o in obstacleRects:

            if (pygame.Rect.colliderect(o, predictedXHitbox)):
                if (self.xVel > 0):
                    self.xPos = o.left - self.hitboxSize/2 - skinWidth
                if (self.xVel < 0):
                    self.xPos = o.right + self.hitboxSize/2 + skinWidth
                self.xVel = 0

            if (pygame.Rect.colliderect(o, predictedYHitbox)):
                if (self.yVel > 0):
                    self.yPos = o.top - self.hitboxSize/2 - skinWidth
                if (self.yVel < 0):
                    self.yPos = o.bottom + self.hitboxSize/2 + skinWidth
                self.yVel = 0

        mapSize = pygame.display.get_window_size()
        
        if (predictedXHitbox.right > mapSize[0]):
            self.xPos = mapSize[0] - self.hitboxSize/2 - skinWidth
            self.xVel = 0
        if (predictedXHitbox.left < 0):
            self.xPos = self.hitboxSize/2 + skinWidth
            self.xVel = 0
        if (predictedYHitbox.right > mapSize[1]):
            self.yPos = mapSize[1] - self.hitboxSize/2 - skinWidth
            self.yVel = 0
        if (predictedYHitbox.left < 0):
            self.yPos = self.hitboxSize/2 + skinWidth
            self.yVel = 0
        

        
        if (self.canSeePlayer and self.shootCooldownTimer == 0):
            self.Shoot(currentRoom)

        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt

        self.hitbox.center = (self.xPos, self.yPos)
    
    def Shoot(self, currentRoom):
        ProjectileScript.SpawnProjectile(self, self.target, currentRoom)

        self.shootCooldownTimer = self.shootCooldownTime
    
    def TakeDamage(self, damageAmt, knockbackDir, knockbackAmt = 1, stunTime = 0.1):
        if (self.stunTimer > 0):
            return
        
        self.runTimer = self.runTime
        
        self.shootCooldownTimer = 1
        self.currentHealth -= damageAmt
        self.stunTimer = stunTime
        self.xVel = knockbackDir[0] * knockbackAmt
        self.yVel = knockbackDir[1] * knockbackAmt

        if (self.currentHealth <= 0):
            self.group.activeEnemies.remove(self)
            
    
    def Timers(self, dt):
        if (self.shootCooldownTimer > 0):
            self.shootCooldownTimer -= dt
        else:
            self.shootCooldownTimer = 0

        if (self.shootCooldownTimer < 1 and not self.canSeePlayer):
            self.shootCooldownTimer = 1
        
        if (self.stunTimer > 0):
            self.stunTimer -= dt
        else:
            self.stunTimer = 0
        
        if (self.runTimer > 0):
            self.runTimer -= dt
        else:
            self.runTimer = 0

        
    
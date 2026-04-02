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
import PlayerScript

def SpawnProjectile(source, target, currentRoom):
    newProjectile = EnemyProjectile(source, target, currentRoom)
    currentRoom.activeEnemyProjectiles.append(newProjectile)

class EnemyProjectile:
    def __init__(self, source, target, currentRoom):
        self.handler = currentRoom

        self.damageAmt = 1

        self.target = target

        self.flySpeed = 500

        self.xPos = source.xPos
        self.yPos = source.yPos
        
        self.hitboxSize = 5

        targetDir = PlayerScript.NormalizeVector([target.xPos - source.xPos, target.yPos - source.yPos])
        offset = random.randint(-source.inaccuracy, source.inaccuracy)
        cosA = math.cos(math.radians(offset))
        sinA = math.sin(math.radians(offset))

        rotatedX = targetDir[0] * cosA - targetDir[1] * sinA
        rotatedY = targetDir[0] * sinA + targetDir[1] * cosA
    
        self.flyDir = PlayerScript.NormalizeVector(((rotatedX), (rotatedY)))

    def Move(self, dt):
        obstacleRects = [o.hitbox for o in self.handler.obstacles]

        self.xPos += self.flyDir[0] * self.flySpeed * dt
        self.yPos += self.flyDir[1] * self.flySpeed * dt

        myHitbox = pygame.Rect(self.xPos, self.yPos, self.hitboxSize, self.hitboxSize)

        for o in obstacleRects:
            if pygame.Rect.colliderect(myHitbox, o):
                try:
                    self.handler.activeEnemyProjectiles.remove(self)
                except:
                    pass
        
    def CheckHit(self):
        myHitbox = pygame.Rect(self.xPos, self.yPos, self.hitboxSize, self.hitboxSize)

        playerHitboxSize = self.target.hitboxSize
        playerHitbox = pygame.Rect(self.target.xPos, self.target.yPos, playerHitboxSize, playerHitboxSize)
        
        if (pygame.Rect.colliderect(playerHitbox, myHitbox)):
            self.target.TakeDamage(self.damageAmt)
            try:
                self.handler.activeEnemyProjectiles.remove(self)
            except:
                pass

        
        
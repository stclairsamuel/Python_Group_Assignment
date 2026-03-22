import pygame
import sys
import math
import numpy as np
import random
import os
import json
import ObstaclesScript
import pynput
from pynput import mouse

def Magnitude(vector):
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

def NormalizeVector(vector):
    magnitude = Magnitude(vector)

    try: 
        return [vector[0] / magnitude, vector[1] / magnitude]
    except:
        return [0, 0]
    

def PointsToLines(polygonPoints):
    myLines = []
    for p in range(len(polygonPoints) - 1):
        point1 = polygonPoints[p]
        point2 = polygonPoints[p + 1]

        newLine = (point1, point2)
        myLines.append(newLine)
    
    return myLines

def CheckPolygonCollisions(pLines, rects):
    for r in rects:
        for l in pLines:
            if r.clipline(*l):
                return r
    
    return None


class Player:
    def __init__(self, startX, startY):
        #Constants
        self.acceleration = 4000
        self.maxSpeed = 400
        self.speed = 0
        self.dashSpeed = 800

        self.currentHealth = self.maxHealth = 5

        self.getInput = True
        
        self.xPos = startX
        self.yPos = startY

        self.xVel = 0
        self.yVel = 0

        self.displaySize = 20
        self.hitboxSize = 15

        self.xInput = 0
        self.yInput = 0

        self.facingDir = [1, 0]

        self.isDashing = False

        self.dashTime = 0.2
        self.dashTimer = 0

        self.dashDir = [0, 0]

        self.dashCdTime = 0.2
        self.dashCdTimer = 0

        self.maxSpeed = 400
        self.acceleration = 3000

        self.drag = 0.97

        self.movingInto = [0, 0]

        self.activeAttacks = []

        
    
    def GetInput(self):
        xInput = 0
        yInput = 0

        inpList = pygame.key.get_pressed()
        mouseList = pygame.mouse.get_pressed()

        if (inpList[pygame.K_w]):
            yInput -= 1
            self.facingDir[1] = -1
        if (inpList[pygame.K_s]):
            yInput += 1
            self.facingDir[1] = 1
        if (inpList[pygame.K_a]):
            xInput -= 1
            self.facingDir[0] = -1
        if (inpList[pygame.K_d]):
            xInput += 1
            self.facingDir[0] = 1
        
        if (yInput and not xInput ):
            self.facingDir[0] = 0
        if (xInput and not yInput):
            self.facingDir[1] = 0
        
        self.xInput = xInput
        self.yInput = yInput
            
        if (inpList[pygame.K_LSHIFT] and not self.dashCdTimer > 0):
            self.StartDash()
    
    def Move(self, dt, obstacles):
        lastXVel = self.xVel
        lastYVel = self.yVel

        '''
        if (self.dashTimer > 0):
            self.isDashing = True
            myVector = NormalizeVector([self.facingDir[0], -self.facingDir[1]])
            self.xVel = self.dashSpeed * myVector[0]
            self.yVel = self.dashSpeed * myVector[1]
        '''

        if (self.movingInto[0] or self.movingInto[1]):
            self.StopDash()
        
        if (self.isDashing and self.dashTimer == 0):
            self.StopDash()
            
        if (not self.isDashing):
            if ((self.xInput != 0 or self.yInput != 0)):
                inputVector = NormalizeVector([self.xInput, self.yInput])

                self.xVel += inputVector[0] * self.acceleration * dt
                self.yVel += inputVector[1] * self.acceleration * dt

                if (Magnitude([lastXVel, lastYVel]) > self.maxSpeed):
                    self.xVel = self.xVel * (self.drag ** (dt * 1000))
                    self.yVel = self.yVel * (self.drag ** (dt * 1000))

            else:
                self.xVel = self.xVel * (self.drag ** (dt * 1000))
                self.yVel = self.yVel * (self.drag ** (dt * 1000))

        speed = Magnitude([self.xVel, self.yVel])

        if (speed > self.maxSpeed and Magnitude([lastXVel, lastYVel]) <= self.maxSpeed and not self.dashTimer > 0):
            self.xVel = (self.xVel / speed) * self.maxSpeed
            self.yVel = (self.yVel / speed) * self.maxSpeed

        nextPos = [self.xPos + (self.xVel * dt), self.yPos + (self.yVel * dt)]

        self.CheckObstacles(nextPos, obstacles, dt)

        wallCheckDist = 2
        left = self.xPos - self.hitboxSize/2
        top = self.yPos - self.hitboxSize/2
        xFacingBox = pygame.Rect(left + self.facingDir[0] * wallCheckDist, top, self.hitboxSize, self.hitboxSize)
        yFacingBox = pygame.Rect(left, top + self.facingDir[1] * wallCheckDist, self.hitboxSize, self.hitboxSize)
        
        for o in obstacles:
            if (pygame.Rect.colliderect(o.hitbox, xFacingBox)):
                self.movingInto[0] = self.facingDir[0]
            else:
                self.movingInto[0] = 0
            if (pygame.Rect.colliderect(o.hitbox, yFacingBox)):
                self.movingInto[1] = self.facingDir[1]
            else:
                self.movingInto[1] = 0

            if (self.movingInto[0] and self.xInput):
                self.yVel *= (o.friction ** (dt * 1000))
            if (self.movingInto[1] and self.yInput):
                self.xVel *= (o.friction ** (dt * 1000))
        
        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt

    def Attack(self):
        mousePos = pygame.mouse.get_pos()
        myPos = (self.xPos, self.yPos)

        dirToMouse = NormalizeVector((mousePos[0] - myPos[0], mousePos[1] - myPos[1]))

        angle = math.atan2(- dirToMouse[1], dirToMouse[0])

        print(math.degrees(angle))

        newAttack = PlayerAttack(math.degrees(angle), self)
        self.activeAttacks.append(newAttack)
    
    def StartDash(self):
        self.dashTimer = self.dashTime
        self.isDashing = True
        dashVector = NormalizeVector(self.facingDir)
        if (self.facingDir[0]):
            self.xVel = dashVector[0] * self.dashSpeed
        if (self.facingDir[1]):
            self.yVel = dashVector[1] * self.dashSpeed
    
    def StopDash(self):
        self.dashCdTimer = self.dashCdTime
        self.dashTimer = 0
        self.isDashing = False
        
    
    def DoDash(self):
        self.xVel = self.dashSpeed * self.facingDir[0]
        self.yVel = self.dashSpeed * self.facingDir[1]

    def CheckObstacles(self, nextPos, obstacles, dt):
        for o in obstacles:
            o.CheckPlayerCollision(self, [nextPos[0], nextPos[1]], dt)
    
    def TakeDamage(self, damageAmt):
        if (self.isDashing):
            return

        self.currentHealth -= damageAmt

        if (self.currentHealth <= 0):
            pygame.quit()
    
    def CreateHealthBar(self):
        imagePath = os.path.join("Images", "PygameHeart.png")

        heartImage = pygame.image.load(imagePath).convert_alpha()

        scale = 2
        width = heartImage.get_width()
        height = heartImage.get_height()

        screen = pygame.display.get_surface()
        WHITE = (255, 255, 255)

        pygame.draw.rect(screen, WHITE, (30, 35, 210, 40))

        biggerHeart = pygame.transform.scale(heartImage, (width * scale, height * scale)).convert_alpha()

        horizontalDistance = 40

        position1 = [40, 40]

        for i in range(self.currentHealth):
            screen.blit(biggerHeart, (position1[0] + (i * horizontalDistance), position1[1]))
            
class PlayerAttack:
    def __init__(self, rotation, player):
        self.hitboxLength = 40
        self.hitboxHeight = 20
        self.distanceFromPlayer = 30
        self.sizeScale = 4

        self.rotation = rotation

        self.player = player

        self.knockback = 600

        with open("PlayerAttackFrames.json", "r") as file:
            self.frames = json.load(file)

        self.editedFrames = []
        for i in range(len(self.frames)):
            newImage = pygame.image.load("Images/PlayerAttackFrames/" + self.frames[i]).convert_alpha()
            newFrame = pygame.transform.rotozoom(newImage, rotation, self.sizeScale).convert_alpha()
            self.editedFrames.insert(0, newFrame)
        
        self.attackTimer = self.attackTime = 0.3

        self.timePerFrame = self.attackTime / len(self.frames)

        self.screen = pygame.display.get_surface()

        d = self.distanceFromPlayer
        cosA = math.cos(math.radians(rotation))
        sinA = math.sin(math.radians(rotation))

        self.xPos = player.xPos + cosA * d
        self.yPos = player.yPos - sinA * d

        w = self.hitboxLength
        h = self.hitboxHeight

        self.hitboxPoints = [
            (self.xPos + ((cosA * d) + (sinA * h)), self.yPos - ((sinA * d) - (cosA * h))),
            (self.xPos + ((cosA * d) - (sinA * h)), self.yPos - ((sinA * d) + (cosA * h))),
            (self.xPos + ((cosA * d) - (sinA * h) - (cosA * w)), self.yPos - ((sinA * d) + (cosA * h) - (sinA * w))),
            (self.xPos + ((cosA * d) + (sinA * h) - (cosA * w)), self.yPos - ((sinA * d) - (cosA * h) - (sinA * w))),
            (self.xPos + ((cosA * d) + (sinA * h)), self.yPos - ((sinA * d) - (cosA * h)))
        ]
    
    def Update(self, dt):
        currentFrame = self.editedFrames[int(self.attackTimer / self.timePerFrame) - 1]

        imageRect = currentFrame.get_rect()

        imageRect.center = (self.xPos, self.yPos)

        self.screen.blit(currentFrame, imageRect) 

        if (self.attackTimer > 0.1):
            self.attackTimer -= dt
        else:
            self.player.activeAttacks.remove(self)
            del self
        
        try:
            myPoly = PointsToLines(self.hitboxPoints)

            for l in myPoly:
                pygame.draw.line(pygame.display.get_surface(), (255, 255, 255), *l)
        except:
            pass

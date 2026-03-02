import pygame
import sys
import math
import numpy as np
import random
import os
import json
import ObstaclesScript

def Magnitude(vector):
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

def NormalizeVector(vector):
    magnitude = Magnitude(vector)

    try: 
        return [vector[0] / magnitude, vector[1] / magnitude]
    except:
        return [0, 0]

class Player:
    def __init__(self, startX, startY):
        #Constants
        self.acceleration = 4000
        self.maxSpeed = 400
        self.speed = 0
        self.dashSpeed = 800

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

        self.dashCdTime = 0.1
        self.dashCdTimer = 0

        self.maxSpeed = 400
        self.acceleration = 3000

        self.drag = 0.97

        self.movingInto = [0, 0]

        self.dashCdTime = 0.2
        self.dashCdTimer = 0


    
    def GetInput(self):
        xInput = 0
        yInput = 0

        inpList = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if (inpList[pygame.K_w]):
            yInput -= 1
            self.facingDir[1] = 1
        if (inpList[pygame.K_s]):
            yInput += 1
            self.facingDir[1] = -1
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

        if (speed > self.maxSpeed and Magnitude([lastXVel, lastYVel]) <= self.maxSpeed):
            self.xVel = (self.xVel / speed) * self.maxSpeed
            self.yVel = (self.yVel / speed) * self.maxSpeed

        nextPos = [self.xPos + (self.xVel * dt), self.yPos + (self.yVel * dt)]

        self.CheckObstacles(nextPos, obstacles, dt)

        wallCheckDist = 2
        left = self.xPos - self.hitboxSize/2
        top = self.yPos - self.hitboxSize/2
        xFacingBox = pygame.Rect(left + self.facingDir[0] * wallCheckDist, top, self.hitboxSize, self.hitboxSize)
        yFacingBox = pygame.Rect(left, top - self.facingDir[1] * wallCheckDist, self.hitboxSize, self.hitboxSize)
        
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

    def CheckObstacles(self, nextPos, obstacles, dt):
        for o in obstacles:
            o.CheckPlayerCollision(self, [nextPos[0], nextPos[1]], dt)
            
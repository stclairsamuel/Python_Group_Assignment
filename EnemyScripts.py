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

        self.room = room

        self.GetSpawningTiles(room)

        if (not room.roomCleared):
            if (room == room.map.finalRoom):
                self.SpawnBoss()
            else:
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
    
    def SpawnBoss(self):
        newEnemy = boss(self, self.target)
        newEnemy.inaccuracy = 30
        newEnemy.shootCooldownTime = 0.1
        
        screen = pygame.display.get_window_size()
        newEnemy.xPos = screen[0]/2
        newEnemy.yPos = screen[1]/2
        newEnemy.maxSpeed = 150
        newEnemy.hitboxSize = 30

        self.activeEnemies.append(newEnemy)
    
    def DrawEnemies(self, dt):
        enemies = self.activeEnemies
        sortedEnemies = sorted(enemies, key=lambda e: e.yPos)

        for e in sortedEnemies:
            e.Animate()
            e.animator.Update(dt)
        

class enemy:
    def __init__(self, group, player):
        self.acceleration = 3000

        animationFile = "Enemy_Animation_Frames"
        animationFolder = "Images/EnemyAnimFrames"

        self.animator = enemy_animator(self, animationFile, animationFolder)

        RED = (255, 0, 0)
        WHITE = (255, 255, 255)

        self.color = RED

        self.drag = 0.999

        self.idealRange = 125
        self.rangeSlack = 75
        self.withinRange = False
        self.tooClose = False

        self.hasSeenPlayer = False

        self.maxSpeed = 200
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

        self.hurtTime = 0.2
        self.hurtTimer = 0
        self.hitflashTime = 0.1
        self.hitflashTimer = 0

    def Update(self, dt):
        self.FindPathToTarget()
        self.Move(dt)
        self.Timers(dt)
    
    def FindPathToTarget(self):
        tW = self.target.hitboxSize
        target = pygame.Rect(self.target.xPos - tW/2, self.target.yPos - tW/2, tW, tW)
        obstacleRects = self.group.obstacleRects
        raycast = PathfindingScript.Raycast((self.xPos, self.yPos), (self.target.xPos, self.target.yPos), target, obstacleRects)

        self.canSeePlayer = raycast.hit
        if (self.canSeePlayer):
            self.withinRange = (raycast.distance < self.idealRange + self.rangeSlack)
            self.tooClose = (raycast.distance < self.idealRange - self.rangeSlack)

    def Move(self, dt):
        currentRoom = self.group.room

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
        if (predictedYHitbox.bottom > mapSize[1]):
            self.yPos = mapSize[1] - self.hitboxSize/2 - skinWidth
            self.yVel = 0
        if (predictedYHitbox.top < 0):
            self.yPos = self.hitboxSize/2 + skinWidth
            self.yVel = 0
        

        
        if (self.canSeePlayer and self.shootCooldownTimer == 0):
            self.Shoot(currentRoom)

        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt

        self.hitbox.center = (self.xPos, self.yPos)
    
    def Animate(self):
        current = self.animator.currentAnimation.animName

        if (self.hitflashTimer > 0):
            self.animator.colorMask = (255, 255, 255)
        else:
            self.animator.colorMask = None

        if (self.hurtTimer > 0):
            if (current != "Rat_Mobster_Hurt"):
                self.animator.SwitchAnimation("Rat_Mobster_Hurt")
            return

        if (self.animator.currentAnimation.animName != "Rat_Mobster_Walk" and (math.pow(self.xVel, 2) + math.pow(self.yVel, 2) > 1)):
            self.animator.SwitchAnimation("Rat_Mobster_Walk")

        if (self.animator.currentAnimation.animName != "Rat_Mobster_Idle" and (math.pow(self.xVel, 2) + math.pow(self.yVel, 2) < 1)):
            self.animator.SwitchAnimation("Rat_Mobster_Idle")
    
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

        self.hurtTimer = self.hurtTime
        self.hitflashTimer = self.hitflashTime

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
        
        if (self.hurtTimer > 0):
            self.hurtTimer -= dt
        else:
            self.hurtTimer = 0
        if (self.hitflashTimer > 0):
            self.hitflashTimer -= dt
        else:
            self.hitflashTimer = 0

class boss:
    def __init__(self, group, player):
        self.acceleration = 3000

        animationFile = "Boss_Animation_Frames"
        animationFolder = "Images/BossAnimFrames"

        self.animator = enemy_animator(self, animationFile, animationFolder)

        RED = (255, 0, 0)
        WHITE = (255, 255, 255)

        self.color = RED

        self.drag = 0.999

        self.idealRange = 100
        self.rangeSlack = 100
        self.withinRange = False
        self.tooClose = False

        self.hasSeenPlayer = False

        self.maxSpeed = 200
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

        self.inaccuracy = 15

        self.stunTimer = self.stunTime = 0
        
        self.drag = 0.98

        self.isStrafing = False

        self.hitbox = pygame.Rect(self.xPos - self.hitboxSize/2, self.yPos - self.hitboxSize/2, self.hitboxSize, self.hitboxSize)

        self.runTimer = 0
        self.runTime = 2

        self.hurtTime = 0.2
        self.hurtTimer = 0
        self.hitflashTime = 0.1
        self.hitflashTimer = 0

        self.attacks = {
            0 : {"name" : "swipe",
                 "animation" : "Rat_Boss_Melee", "Ideal Range" : 15, "Range Slack" : 30, "Charge Time" : 0.5, "Attack Time" : 0.5},
            1 : {"name" : "rappid", 
                 "animation" : "Rat_Boss_Aim", "Ideal Range" : 200, "Range Slack" : 100, "Charge Time" : 0.5, "Attack Time" : 2},
            2 : {"name" : "blast",
                 "animation" : "Rat_Boss_Throw", "Ideal Range" : 100, "Range Slack" : 50, "Charge Time" : 0.5, "Attack Time" : 0.2, "Explosion Delay" : 1, "Explosion Duration" : 0.5}
        }

        self.cooldownTime = 2
        self.cooldownTimer = 0

        self.currentAttack = 1
        self.lastAttack = None

        self.playerLastSeen = None

        self.isAttacking = False
        self.attackChargeTimer = 0
        self.attackTimer = 0
    
    def Update(self, dt):
        self.Move(dt)
        #self.animator.Update(dt)
        self.Timers(dt)

        
    
    def Move(self, dt):
        couldSeePlayer = self.canSeePlayer

        dirToMove = (0, 0)
        
        self.canSeePlayer = self.CheckPlayerSight()

        pXPos = self.target.xPos
        pYPos = self.target.yPos

        lastXVel = self.xVel
        lastYVel = self.yVel

        if (self.canSeePlayer):
            self.playerLastSeen = (pXPos, pYPos)

        if (not self.currentAttack):
            self.DecideAttack()

        inRange = self.CheckRange()

        if (self.canSeePlayer):
            targetPos = (pXPos, pYPos)

            if (self.hasSeenPlayer == False): self.hasSeenPlayer = True

            if (not self.withinRange):
                dirToMove = PlayerScript.NormalizeVector((targetPos[0] - self.xPos, targetPos[1] - self.yPos))

            if (self.tooClose):
                dirToMove = PlayerScript.NormalizeVector((self.xPos - targetPos[0], self.yPos - targetPos[1]))

        else:
            myAlgo = PathfindingScript.AStarMap(self.group.room.info, (int(pXPos / 64), int(pYPos / 64)), (int(self.xPos / 64), int(self.yPos / 64)))
            myAlgo.MakeAlgo()

            try:
                nextCoord = myAlgo.path[1]
                nextPos = (nextCoord[0] * 64 + 32, nextCoord[1] * 64 + 32)

                dirToMove = PlayerScript.NormalizeVector((nextPos[0] - self.xPos, nextPos[1] - self.yPos))
            except IndexError:
                pass

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
        if (predictedYHitbox.bottom > mapSize[1]):
            self.yPos = mapSize[1] - self.hitboxSize/2 - skinWidth
            self.yVel = 0
        if (predictedYHitbox.top < 0):
            self.yPos = self.hitboxSize/2 + skinWidth
            self.yVel = 0
            

        if (not self.isAttacking and self.cooldownTimer == 0 and self.attackChargeTimer == 0):
            self.StartAttack()

        if (self.isAttacking):
            self.UpdateAttack()
        
        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt

        self.hitbox.center = (self.xPos, self.yPos)

        
    def CheckPlayerSight(self):
        myPos = (self.xPos, self.yPos)
        pPos = (self.target.xPos, self.target.yPos)
        tW = self.target.hitboxSize/2
        target = pygame.Rect(self.target.xPos - tW/2, self.target.yPos - tW/2, tW, tW)
        

        raycast = PathfindingScript.Raycast(myPos, pPos, target, self.group.obstacleRects)

        return raycast.hit
    
    def DecideAttack(self):
        pass
    
    def CheckRange(self):
        atk = self.attacks[self.currentAttack]
        distMin = atk["Ideal Range"] - atk["Range Slack"]
        distMax = atk["Ideal Range"] + atk["Range Slack"]

        myPos = (self.xPos, self.yPos)
        pPos = (self.target.xPos, self.target.yPos)

        dist = PlayerScript.Magnitude((myPos[0] - pPos[0], myPos[1] - pPos[1]))

        return (dist < distMax and dist > distMin)
    
    def StartAttack(self):
        self.currentAttack = random.randint(0, 2)

        self.attackChargeTimer = self.attacks[self.currentAttack]["Charge Time"]

        self.animator.SwitchAnimation(self.attacks[self.currentAttack]["animation"])

    def UpdateAttack(self):
        pass

    def ExecuteAttack(self):
        self.attackTimer = self.attacks[self.currentAttack]["Attack Time"]

        match self.attacks[self.currentAttack]["name"]:
            case "swipe":
                pass

            case "rapid":
                pass
        
            case "blast":

                pass
    
    def Shoot(self, currentRoom):
        ProjectileScript.SpawnProjectile(self, self.target, currentRoom)

        self.shootCooldownTimer = self.shootCooldownTime
    
    def EndAttack(self):
        self.isAttacking = False
        self.currentAttack = None
        self.cooldownTimer = self.cooldownTime
        pass
        
    def Animate(self):
        pass

    def TakeDamage(self, damage, knockbackVector, knockback):
        pass

    def Timers(self, dt):
        timers = [self.attackTimer, self.cooldownTimer, self.attackChargeTimer, self.stunTimer, self.hurtTimer]

        if (self.attackTimer > 0): self.attackTimer -= dt
        else: self.attackTimer = 0

        if (self.cooldownTimer > 0): self.cooldownTimer -= dt
        else: self.cooldownTimer = 0

        if (self.attackChargeTimer > 0): self.attackChargeTimer -= dt
        else: self.attackChargeTimer = 0

        if (self.stunTimer > 0): self.stunTimer -= dt
        else: self.stunTimer = 0
        
        if (self.hurtTimer > 0): self.hurtTimer -= dt
        else: self.hurtTimer = 0
        
        print(self.attackChargeTimer)
        





class enemy_animator:
    def __init__(self, enemy, infoFile, imagesFolder):
        self.parent = enemy

        self.animations = {}

        self.animationTimes = 0.3

        self.animationTimer = 0

        self.colorMask = None
        
        with (open(f'{infoFile}.json')) as file:
            self.animatorFile = file
            contents = json.load(file)
            
            for a in contents.keys():
                self.animations[a] = animation(infoFile, a)
            
            self.animationList = list(self.animations.keys())
            
        self.currentAnimation = self.animations[self.animationList[0]]
        
        print(self.animations)

        self.editedFrames = {}
    
    def SwitchAnimation(self, animation):
        if (animation not in self.animationList):
            print(f'error: animation {animation} not in animation list')
        
        self.currentAnimation = self.animations[animation]

        self.animationTimer = 0
        
    
    def Update(self, dt):
        self.Timers(dt)

        currentFrame = self.currentAnimation.GetFrame(self.animationTimer)

        if (self.parent.xPos > self.parent.target.xPos):
            currentFrame = pygame.transform.flip(currentFrame, True, False).convert_alpha()

        frameSize = pygame.Surface.get_size(currentFrame)

        if (self.colorMask):                
            imageSize = currentFrame.get_size()

            color_surface = pygame.Surface(imageSize).convert_alpha()
            color_surface.fill((255, 255, 255))

            masked_image = currentFrame.copy()
            currentFrame.fill((255, 255, 255, 0), special_flags = pygame.BLEND_RGBA_MAX)

        pygame.Surface.blit(pygame.display.get_surface(), currentFrame, (self.parent.xPos - frameSize[0]/2, self.parent.yPos - frameSize[1]/2 - self.parent.hitboxSize/2))

        
    
    def Timers(self, dt):
        self.animationTimer += dt
        if (self.animationTimer >= self.currentAnimation.animTime):
            self.animationTimer -= self.currentAnimation.animTime

class animation:
    def __init__(self, fileName, animName):
        self.fileName = fileName
        self.animName = animName

        self.animTime = 0.5

        self.frames = []

        scale = 2.4

        with open(f'{self.fileName}.json') as file:
            contents = json.load(file)

            if (animName not in contents.keys()):
                print(f'error: animation {animName} not in {fileName}')
                return
            
            images = [pygame.image.load(f'{f}.png').convert_alpha() for f in contents[animName]]

            self.frames = [pygame.transform.scale(i, (pygame.Surface.get_size(i)[0] * scale, pygame.Surface.get_size(i)[1] * scale)).convert_alpha() for i in images]
    
    def GetFrame(self, timer):
        numOfFrames = len(self.frames)

        timePerFrame = self.animTime / numOfFrames

        currentFrameInt = min(int(timer / timePerFrame), numOfFrames - 1)

        if currentFrameInt >= numOfFrames:
            currentFrameInt = numOfFrames - 1

        returnFrame = self.frames[currentFrameInt]

        return returnFrame
    
class EnemyHurtbox:
    def __init__(self, duration, position, size, rotation, animFile):
        self.duration = duration

        self.hitboxLength = size[0]
        self.hitboxHeight = size[1]

        self.xPos = position[0]
        self.yPos = position[1]

        self.sizeScale = 1

        self.screen = pygame.display.get_surface()

        cosA = math.cos(math.radians(rotation))
        sinA = -math.sin(math.radians(rotation))

        w = self.hitboxLength
        h = self.hitboxHeight

        x = self.xPos
        y = self.yPos

        self.hitboxPoints = [
            (x - (sinA * w), y + (cosA * w)),
            (x + (sinA * w), y - (cosA * w)),
            (x + (sinA * w) + (cosA * h), y - (cosA * w) + (sinA * h)),
            (x - (sinA * w) + (cosA * h), y + (cosA * w) + (sinA * h)),
            (x - (sinA * w), y + (cosA * w)),
            (x + (sinA * w) + (cosA * h), y - (cosA * w) + (sinA * h)),
            (x + (sinA * w), y - (cosA * w)),
            (x - (sinA * w) + (cosA * h), y + (cosA * w) + (sinA * h)),
        ]

        with open(animFile, "r") as file:
            self.frames = json.load(file)

        self.editedFrames = []
        for i in range(len(self.frames)):
            newImage = pygame.image.load(self.frames[i]).convert_alpha()
            newFrame = pygame.transform.rotozoom(newImage, rotation, self.sizeScale).convert_alpha()
            self.editedFrames.insert(0, newFrame)
        
        self.timePerFrame = self.duration / len(self.frames)

    def Update(self):
        pass

    def Timers(self):
        pass
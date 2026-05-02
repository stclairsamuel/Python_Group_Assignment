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
import Rendering

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
    
    def SpawnEnemies(self):
        
        enemiesToSpawn = int(np.round(len(self.spawnableTiles) / self.enemiesPerTile))

        for _ in range(enemiesToSpawn):
            newEnemy = enemy(self, self.target)
            self.room.AddGameObject(newEnemy)
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
        

class enemy:
    def __init__(self, group, player):
        self.acceleration = 3000

        self.spriteRenderer = Rendering.sprite_renderer(self)

        animationFile = "Enemy_Animation_Frames"

        self.animator = Rendering.animator(animationFile, self.spriteRenderer)

        self.spriteRenderer.animator = self.animator

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

        self.animator.SwitchAnimation("Rat_Mobster_Idle")

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
    
    def Render(self, dt):
        self.Animate()
        self.spriteRenderer.Render(dt)

    def Move(self, dt):
        #self.parentRoom = self.group.room

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
            myAlgo = PathfindingScript.AStarMap(self.parentRoom.info, (int(pXPos / 64), int(pYPos / 64)), (int(self.xPos / 64), int(self.yPos / 64)))
            myAlgo.MakeAlgo()

            #for p in myAlgo.path:
                #pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (p[0] * 64 + 32, p[1] * 62 + 32), 15)

            try:
                nextCoord = myAlgo.path[1]
                nextPos = (nextCoord[0] * 64 + 32, nextCoord[1] * 64 + 32)

                dirToMove = PlayerScript.NormalizeVector((nextPos[0] - self.xPos, nextPos[1] - self.yPos))
            except IndexError:
                pass

        enemyRects = [e.hitbox for e in self.parentRoom.enemyGroup.activeEnemies if e != self]

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
            self.Shoot()

        self.xPos += self.xVel * dt
        self.yPos += self.yVel * dt

        self.hitbox.center = (self.xPos, self.yPos)
    
    def Animate(self):
        current = self.animator.currentAnimation.animName

        if (self.hitflashTimer > 0):
            self.spriteRenderer.SetColorMask((255, 255, 255))
        else:
            self.spriteRenderer.SetColorMask(None)

        if (self.hurtTimer > 0):
            if (current != "Rat_Mobster_Hurt"):
                self.animator.SwitchAnimation("Rat_Mobster_Hurt")
            return

        if (self.animator.currentAnimation.animName != "Rat_Mobster_Walk" and (math.pow(self.xVel, 2) + math.pow(self.yVel, 2) > 1)):
            self.animator.SwitchAnimation("Rat_Mobster_Walk")

        if (self.animator.currentAnimation.animName != "Rat_Mobster_Idle" and (math.pow(self.xVel, 2) + math.pow(self.yVel, 2) < 1)):
            self.animator.SwitchAnimation("Rat_Mobster_Idle")
    
    def Shoot(self):
        newProj = ProjectileScript.enemy_projectile(self, self.target)

        self.parentRoom.AddGameObject(newProj)

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
        
        if (self.currentHealth <= 0):
            self.Die()
    
    def Die(self):
        if (self in self.group.activeEnemies):
            self.group.activeEnemies.remove(self)
        if (self in self.group.room.gameObjects):
            self.group.room.gameObjects.remove(self)
    
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

        self.animator = Rendering.animator(self, animationFile)

        RED = (255, 0, 0)
        WHITE = (255, 255, 255)

        self.color = RED

        self.idealRange = 100
        self.rangeSlack = 100

        self.hasSeenPlayer = False

        self.maxSpeed = 350
        self.speed = 20

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
                 "animation" : "Rat_Boss_Melee", "Ideal Range" : 30, "Range Slack" : 30, "Charge Time" : 1, "Attack Time" : 0},
            1 : {"name" : "rapid", 
                 "animation" : "Rat_Boss_Aim", "Ideal Range" : 200, "Range Slack" : 100, "Charge Time" : 0.33, "Attack Time" : 2},
            2 : {"name" : "blast",
                 "animation" : "Rat_Boss_Throw", "Ideal Range" : 100, "Range Slack" : 50, "Charge Time" : 0.86, "Attack Time" : 0, "Explosion Delay" : 1, "Explosion Duration" : 0.5}
        }

        self.animator.animations["Rat_Boss_Shoot"].animTime = 0.2
        self.animator.animations["Rat_Boss_Melee"].animTime = self.attacks[0]["Charge Time"]
        self.animator.animations["Rat_Boss_Aim"].animTime = self.attacks[1]["Charge Time"]
        self.animator.animations["Rat_Boss_Throw"].animTime = self.attacks[2]["Charge Time"]

        self.cooldownTime = 1
        self.cooldownTimer = 0

        self.currentAttack = 1
        self.lastAttack = None

        self.playerLastSeen = None

        self.isAttacking = False

        self.attackState = 0
        # 0 : not attacking
        # 1 : charging
        # 2 : executing

        self.attackChargeTimer = 0
        self.attackTimer = 0
    
    def Update(self, dt):
        self.UpdateAttack(dt)
        self.Move(dt)
        self.Timers(dt)
        #self.animator.Update(dt)

        
    
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

        if (self.currentAttack == None):
            self.DecideAttack()
    
        inRange = self.InRange()
        tooClose = self.TooClose()

        if (self.canSeePlayer):
            targetPos = (pXPos, pYPos)

            if (self.hasSeenPlayer == False): self.hasSeenPlayer = True

            if (not inRange):
                dirToMove = PlayerScript.NormalizeVector((targetPos[0] - self.xPos, targetPos[1] - self.yPos))

            if (tooClose):
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
        
        if (self.attackState != 0):
            dirToMove = (0, 0)

        isStunned = self.stunTimer > 0
        
        if (not isStunned):
            self.xVel += dirToMove[0] * self.acceleration * dt
            self.yVel += dirToMove[1] * self.acceleration * dt
            self.color = (255, 0, 0)
        else:
            self.xVel *= (self.drag ** (dt * 1000))
            self.yVel *= (self.drag ** (dt * 1000))
            self.color = (255, 255, 255)

        # drag

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

        if ((self.attackState == 0 or self.cooldownTimer > 0) and speed < 1):
            self.animator.SwitchAnimation("Rat_Boss_Walk")

        if (self.attackState == 0 and self.cooldownTimer == 0 and inRange and not tooClose):
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
        nextAtk = random.randint(0, 2)
        self.currentAttack = nextAtk
    
    def InRange(self):
        atk = self.attacks[self.currentAttack]
        distMax = atk["Ideal Range"] + atk["Range Slack"]

        myPos = (self.xPos, self.yPos)
        pPos = (self.target.xPos, self.target.yPos)

        dist = PlayerScript.Magnitude((myPos[0] - pPos[0], myPos[1] - pPos[1]))

        return (dist < distMax)

    def TooClose(self):
        atk = self.attacks[self.currentAttack]
        distMin = atk["Ideal Range"] - atk["Range Slack"]

        myPos = (self.xPos, self.yPos)
        pPos = (self.target.xPos, self.target.yPos)

        dist = PlayerScript.Magnitude((myPos[0] - pPos[0], myPos[1] - pPos[1]))

        return (dist < distMin)
    
    def StartAttack(self):
        self.attackState = 1

        self.attackChargeTimer = self.attacks[self.currentAttack]["Charge Time"]

        self.animator.SwitchAnimation(self.attacks[self.currentAttack]["animation"])

    def UpdateAttack(self, dt):
        if (self.attackState == 1 and self.attackChargeTimer == 0):
            self.ExecuteAttack()

        if (self.attackState == 2):
            if (self.attackTimer > 0):
                pass
            else:
                self.EndAttack()
            


    def ExecuteAttack(self):
        self.attackState = 2
        

        (self.attacks[self.currentAttack]["name"])

        match self.attacks[self.currentAttack]["name"]:
            case "swipe":
                pass

            case "rapid":
                self.animator.SwitchAnimation("Rat_Boss_Shoot")
        
            case "blast":
                pass
        
        if (self.attacks[self.currentAttack]["Attack Time"]):
            self.attackTimer = self.attacks[self.currentAttack]["Attack Time"]
        else:
            self.EndAttack()
        
    
    def Shoot(self):
        ProjectileScript.SpawnProjectile(self, self.target, self.parentRoom)

        self.shootCooldownTimer = self.shootCooldownTime
    
    def EndAttack(self):
        self.attackState = 0
        self.currentAttack = None
        self.cooldownTimer = self.cooldownTime

        self.animator.SwitchAnimation("Rat_Boss_Walk")
        
    def Animate(self):
        pass

    def TakeDamage(self, damage, knockbackVector, knockback):
        pass

    def Timers(self, dt):
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
    
class EnemyHurtbox:
    def __init__(self, duration, position, size, rotation):
        self.duration = duration

        self.parent = None

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

        self.renderer.SetRotation(rotation)

    def Update(self, dt):
        if (self.attackTimer > 0.1):
            self.attackTimer -= dt
        else:
            self.parent.activeAttacks.remove(self)
            del self
        
        try:
            myPoly = PlayerScript.PointsToLines(self.hitboxPoints)

            #for l in myPoly:
                #pygame.draw.line(pygame.display.get_surface(), (255, 255, 255), *l)
        except:
            pass

        myPoly = PlayerScript.PointsToLines(self.hitboxPoints)

        hitbox = pygame.Rect(self.parent.target.xPos, self.parent.target.yPos, self.parent.target.hitboxSize, self.parent.target.hitboxSize)
        hitbox.center = (self.parent.target.xPos, self.parent.target.yPos)

        self.hasHitPlayer = False
        
        if (PlayerScript.CheckPolygonCollisions(myPoly, [hitbox])):
            hitPlayer = next(iter(e for e in self.map.self.parentRoom.enemyGroup.activeEnemies if pygame.Rect(e.xPos - e.hitboxSize/2, e.yPos - e.hitboxSize/2, e.hitboxSize, e.hitboxSize) == PlayerScript.CheckPolygonCollisions(myPoly, hitboxes)), None)

            if (hitPlayer and not self.hasHitPlayer):
                knockbackVector = (math.cos(math.radians(self.rotation)), -math.sin(math.radians(self.rotation)))

                PlayerScript.StopTime(0.05)

                ##
                damage = self.GetDamage()
                hitPlayer.TakeDamage(damage, knockbackVector, self.knockback)

                self.hasHitPlayer = True

    def Timers(self):
        pass
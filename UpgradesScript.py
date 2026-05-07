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

class item_glow:
    def __init__(self, item):
        self.xPos = item.xPos
        self.yPos = item.yPos

        self.sortingLayer = -1

        filePath = "Glow_Animation_Frames"
            
        self.spriteRenderer = Rendering.sprite_renderer(self)

        self.animator = Rendering.animator(filePath, self.spriteRenderer)

    def Render(self, dt):
        self.spriteRenderer.Render(dt)


class fallen_upgrade:
    def __init__(self, tracker, room):
        chooseableUpgrades = [u for u in range(len(tracker.upgradeIDs)) if u not in [tracker.upgradeIDs[u] for _ in tracker.upgradeIDs]]
        self.upgradeID = random.randint(0, len(tracker.upgradeIDs) - 1)

        self.hitboxSize = 10

        self.room = room

        self.tracker = tracker

        self.xPos = 0
        self.yPos = 0

        if (len(room.enemyGroup.spawnableTiles) > 0):
            spawnCoords = random.choice(room.enemyGroup.spawnableTiles)

            print(spawnCoords)

            self.xPos = spawnCoords[0] * 64 + 32
            self.yPos = spawnCoords[1] * 64 + 32
        
        self.myHitbox = pygame.Rect(self.xPos, self.yPos, self.hitboxSize, self.hitboxSize)
        self.myHitbox.center = (self.xPos, self.yPos)

        with open("UpgradeSprites.json", "r") as file:
            contents = json.load(file)
            myImage = pygame.image.load(f'{contents[str(self.upgradeID)]}.png').convert_alpha()


        self.spriteRenderer = Rendering.sprite_renderer(self, myImage)

        self.spriteRenderer.ChangeSize(0.5)

    def CheckPickup(self):
        player = self.tracker.player

        playerHitbox = pygame.Rect(player.xPos - player.hitboxSize / 2, player.yPos - player.hitboxSize / 2, player.hitboxSize, player.hitboxSize)

        if (pygame.Rect.colliderect(playerHitbox, self.myHitbox)):
            self.tracker.Pickup(self)
            if (hasattr(self, "glow")):
                self.room.DelGameObject(self.glow)
            self.room.DelGameObject(self)

    def Render(self, dt):
        self.spriteRenderer.Render(dt)

    def Update(self, dt):
        self.CheckPickup()






class upgrade_tracker:
    def __init__(self, player):
        self.upgradeIDs = {
            0 : "roller_skates", # + movement speed
            1 : "long_claws", # + attack range
            2 : "cool_cape", # + dash length
            3 : "sharp_scarf", # + attack after dash deals additional damage
            4 : "floating_shield", # 1 hit blocked per room
            5 : "life_elixir", # +2 hp and max hp
            6 : "vampire_fangs", # heal 1 every 12 hits
            7 : "enchanted_blade", # attacks fire ranged projectile
            8 : "flaming_boots", # moving leaves damaging fire
            9 : "quick_claws", # + attack speed
            10 : "strong_claws", # + attack damage
            11 : "dashing_dress", # - dash cooldown
            12 : "knockout_glove", # + damage on every 3rd attack
            13 : "pointy_tunic", # dashing through enemies deals damage
            14 : "hardened_shell", # additional i frames
            15 : "volatile_shell", # damage nearby enemies on taking damage
        }

        self.player = player

        self.heldUpgrades = []

        self.scarfPrimed = False
        self.shield = 0

        self.sharpScarfTime = 1
        self.sharpScarfTimer = 0

        self.lifestealTracker = 0

        self.enchantedStrikeTimer = 0
        self.enchantedStrikeTime = 2

        self.bootFireTimer = 0
        self.bootFireTime = 1

        self.knockoutCounter = 0

        self.tunicEnemies = []

        self.shellExplosionSize = 128

    def SpawnUpgrade(self, room):
        newUpgrade = fallen_upgrade(self, room)
        glow = item_glow(newUpgrade)
        room.AddGameObject(glow)
        room.AddGameObject(newUpgrade)
        newUpgrade.glow = glow

    def Update(self, room, dt):
        self.Timers(dt)

        if (self.player.isDashing and "pointy_tunic" in self.heldUpgrades):
            for e in self.player.parentRoom.enemyGroup.activeEnemies:
                if pygame.Rect.colliderect(self.player.hitbox, e.hitbox) or self.player.hitbox.contains(e.hitbox) and e not in self.tunicEnemies:
                    e.TakeDamage(1, (0, 0))
                    self.tunicEnemies.append(e)
        
        if (not self.player.isDashing and len(self.tunicEnemies) > 0):
            self.tunicEnemies = []
    
    def Timers(self, dt):

        if ("sharp_scarf" in self.heldUpgrades and self.scarfPrimed):
            if (self.sharpScarfTimer > 0):
                self.sharpScarfTimer -= dt
            else:
                self.sharpScarfTimer = 0
                self.scarfPrimed = False
        
        if ("enchanted_blade" in self.heldUpgrades):
            if (self.enchantedStrikeTimer > 0):
                self.enchantedStrikeTimer -= dt
            else:
                self.enchantedStrikeTimer = 0
    
        if ("flaming_boots" in self.heldUpgrades):
            if (len(self.player.parentRoom.enemyGroup.activeEnemies)):
                self.bootFireTimer += dt
                if (self.bootFireTimer >= self.bootFireTime):
                    self.bootFireTimer -= self.bootFireTime
                    self.SpawnFire()
                    print("hit")
            else:
                self.bootFireTimer = 0

    def SpawnFire(self):
        newFire = burning_ground(self.player)
        self.player.parentRoom.AddGameObject(newFire)
    
    def Pickup(self, pickedUpgrade):
        upgradeID = pickedUpgrade.upgradeID

        print(self.upgradeIDs[upgradeID])

        match self.upgradeIDs[upgradeID]:
            case "roller_skates":
                self.player.maxSpeed = 500
                self.player.acceleration = 4000
            
            case "long_claws":
                self.player.attackWidth = 30
                self.player.attackHeight = 60
                self.player.attackSize = 1.6

            case "cool_cape":
                self.player.dashSpeed = 1200

            case "floating_shield":
                self.shield = 1

            case "life_elixir":
                self.player.maxHealth += 2
                self.player.currentHealth += 2
            
            case "quick_claws":
                self.player.attackCdTime = 0.1

            case "strong_claws":
                self.player.attackDamage = 2

            case "dashing_dress":
                self.player.dashCdTime = 0.5
            
            case "hardened_shell":
                self.player.invincibilityTime = 1.5

        self.heldUpgrades.append(self.upgradeIDs[pickedUpgrade.upgradeID])
        print(self.heldUpgrades)
    
    def CalculateDamage(self, damage):
        if (self.scarfPrimed):
            damage *= 1.5
            self.player.upgradesTracker.scarfPrimed = False
    
        if ("vampire_fangs" in (self.heldUpgrades)):
            self.lifestealTracker += 1
            if (self.lifestealTracker >= 12):
                self.lifestealTracker = 0
                self.player.Heal(1)

        if ("knockout_glove" in (self.heldUpgrades)):
            self.knockoutCounter += 1
            if (self.knockoutCounter >= 3):
                self.knockoutCounter = 0
                damage *= 2
        

        return damage

class burning_ground:
    def __init__(self, player):
        self.xPos = player.xPos
        self.yPos = player.yPos
        self.sortingLayer = -1

        self.spriteSize = 32

        self.sizeScale = 1.6

        filePath = "Player_Burning_Ground_Frames"
            
        self.spriteRenderer = Rendering.sprite_renderer(self)

        self.animator = Rendering.animator(filePath, self.spriteRenderer)

        self.spriteRenderer.ChangeSize(self.sizeScale)

        self.tickTimer = self.tickTime = 0.5

        self.durationTimer = self.durationTime = 2.5

        self.fadingIn = True
        self.fadingOut = False

        self.hitbox = pygame.Rect(self.xPos, self.yPos, 2 * self.sizeScale * self.spriteSize, 2 * self.sizeScale * self.spriteSize)
        self.hitbox.center = (self.xPos, self.yPos)
    
    def Update(self, dt):
        self.Timers(dt)
    
    def Render(self, dt):
        self.spriteRenderer.Render(dt)
    
    def Timers(self, dt):
        self.tickTimer += dt
        if (self.tickTimer > self.tickTime):
            self.tickTimer -= self.tickTime
            self.DamageTick()
        
        if (self.durationTimer > 0):
            self.durationTimer -= dt
        else:
            self.durationTimer = 0
            self.Delete()

    def Delete(self):
        self.parentRoom.DelGameObject(self)

    def DamageTick(self):
        for e in self.parentRoom.enemyGroup.activeEnemies:
            if pygame.Rect.colliderect(self.hitbox, e.hitbox) or self.hitbox.contains(e.hitbox):
                e.TakeDamage(1, (0, 0))






    
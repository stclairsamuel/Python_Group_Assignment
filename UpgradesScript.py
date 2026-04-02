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

class fallen_upgrade:
    def __init__(self, tracker, room):
        chooseableUpgrades = [u for u in range(len(tracker.upgradeIDs)) if u not in [tracker.upgradeIDs[u] for _ in tracker.upgradeIDs]]
        self.upgradeID = random.randint(0, len(tracker.upgradeIDs) - 1)

        self.hitboxSize = 10

        self.room = room

        self.tracker = tracker

        if (len(room.enemyGroup.spawnableTiles) > 0):
            spawnCoords = random.choice(room.enemyGroup.spawnableTiles)

            print(spawnCoords)

            self.xPos = spawnCoords[0] * 64 + 32
            self.yPos = spawnCoords[1] * 64 + 32
        else:
            self.xPos = 0
            self.yPos = 0
        
        self.myHitbox = pygame.Rect(self.xPos, self.yPos, self.hitboxSize, self.hitboxSize)
        self.myHitbox.center = (self.xPos, self.yPos)

    def CheckPickup(self, player):
        playerHitbox = pygame.Rect(player.xPos - player.hitboxSize / 2, player.yPos - player.hitboxSize / 2, player.hitboxSize, player.hitboxSize)

        if (pygame.Rect.colliderect(playerHitbox, self.myHitbox)):
            self.tracker.Pickup(self)
            self.room.spawnedUpgrades.remove(self)






class upgrade_tracker:
    def __init__(self, player):
        self.upgradeIDs = {
            0 : "roller_skates",
            1 : "long_claws",
            2 : "cool_cape",
            3 : "sharp_scarf",
            4 : "floating_shield",
            5 : "life_elixir"
        }

        self.player = player

        self.heldUpgrades = []
        self.spawnedUpgrades = []

        self.scarfPrimed = False
        self.shield = 0

        self.sharpScarfTime = 1
        self.sharpScarfTimer = 0

    def SpawnUpgrade(self, room):
        newUpgrade = fallen_upgrade(self, room)
        room.spawnedUpgrades.append(newUpgrade)

    def Update(self, room, dt):
        self.DrawUpgrades(room)
        self.Timers(dt)
    
    def DrawUpgrades(self, room):
        for u in room.spawnedUpgrades:
            pygame.draw.circle(pygame.display.get_surface(), (255, 255, 255), (u.xPos, u.yPos), 10)
    
    def Timers(self, dt):

        if ("sharp_scarf" in self.heldUpgrades and self.scarfPrimed):
            if (self.sharpScarfTimer > 0):
                self.sharpScarfTimer -= dt
            else:
                self.sharpScarfTimer = 0
                self.scarfPrimed = False
    
    def Pickup(self, pickepUpgrade):
        upgradeID = pickepUpgrade.upgradeID

        print(self.upgradeIDs[upgradeID])

        match self.upgradeIDs[upgradeID]:
            case "roller_skates":
                self.player.maxSpeed = 500
                self.player.acceleration = 4000
            
            case "long_claws":
                self.player.attackWidth = 30
                self.player.attackHeight = 60

            case "cool_cape":
                self.player.dashSpeed = 1200

            case "floating_shield":
                self.shield = 1

            case "life_elixir":
                self.player.maxHealth += 2
                self.player.currentHealth += 2

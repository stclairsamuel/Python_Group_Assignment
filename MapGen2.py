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
import EnemyScripts
import UpgradesScript

class Map:
    def __init__(self, maxLength, maxHeight, numOfRooms):
        self.maxLength = maxLength
        self.maxHeight = maxHeight

        self.enemyGroup = []

        self.numOfRooms = numOfRooms

        self.info = []

        self.fileName = "CurrentMap"

        self.startRoomPos = (0, int(np.round(maxHeight/2)))

        self.rooms = []

        self.currentRoom = None

        self.upgradesTracker = None
    
    def MakeNewMap(self):
        for y in range(self.maxHeight):
            for x in range(self.maxLength):
                self.info.append("o")
        self.info = [["o" for i in range(self.maxLength)] for j in range(self.maxHeight)]

        currentPos = self.startRoomPos

        lastRoom = None

        for r in range(self.numOfRooms):
            newRoom = Room(self, currentPos, lastRoom)
            self.rooms.append(newRoom)

            self.info[currentPos[1]][currentPos[0]] = f'x{r}'

            nextPos = self.NextRoomPos(currentPos)

            currentPos = nextPos

            lastRoom = newRoom
        
        for i in range(3):
            self.AddSideRooms()
        
        self.currentRoom = self.rooms[0]

        # Map Layout Locked In

        for r in range(len(self.rooms)):
            current = self.rooms[r]
            if (current.parentRoom):
                print(f'{current.parentRoom.mapPos} <----> {current.mapPos}')
                newDoor = Door(current.parentRoom, current)
                print(current.exitDoor)
        
        # Doors Locked In

        for r in (self.rooms):
            r.MakeObstacles()
    
    def AddSideRooms(self):
        roomchance = 3

        for r in self.rooms:
            if random.randint(0, roomchance) == 1:
                nextPos = self.NextRoomPos(r.mapPos)
                newRoom = Room(self, nextPos, r)
                self.rooms.append(newRoom)
                # ERROR HERE
                self.info[nextPos[1]][nextPos[0]] = f's{r}'

    
    def NextRoomPos(self, currentPos):
        positionsToCheck = [(currentPos[0], currentPos[1] - 1),
                     (currentPos[0] + 1, currentPos[1]),
                     (currentPos[0], currentPos[1] + 1)]
    
        for p in positionsToCheck:
            if (p[0] < 0 or p[1] < 0 or p[0] > self.maxLength - 1 or p[1] > self.maxHeight - 1):
                positionsToCheck.remove(p)
                continue
            for r in self.rooms:
                if (p == r.mapPos):
                    # ERROR HERE
                    try:
                        positionsToCheck.remove(p)
                    except:
                        print(f'error at {p}')
        if (len(positionsToCheck) == 0):
            print("Yikes!!!")
        
        return(random.choice(positionsToCheck))


class Room:
    def __init__(self, map, mapPos, parentRoom):
        self.xLen = 14
        self.yLen = 10

        self.map = map
        self.mapPos = mapPos

        self.parentRoom = parentRoom

        self.info = []

        self.fileName = f'RandomMap{self.mapPos}'

        self.MakeEmptyRoom()

        self.doors = []
        self.exitDoor = None

        self.termChance = 8
        self.maxWallSize = 6
        self.wallsPerRoom = 9

        self.tileList = []
        
        self.activeEnemyProjectiles = []
        self.enemyGroup = None

        self.spawnedUpgrades = []

        with open("TileSetStuffs/TileHandling.json", "r") as tileSheetFile:
            self.tiles = json.load(tileSheetFile)
        
        self.roomCleared = False
    
    def MakeEmptyRoom(self):
        self.info = [["o" for _ in range(self.xLen)] for _ in range(self.yLen)]
        for y in range(len(self.info)):
            for x in range(len(self.info[y])):
                if (x in (0, self.xLen - 1) or y in (0, self.yLen - 1)):
                    self.info[y][x] = "z"
        with open(f'MapFiles/{self.fileName}.json', 'w') as file:
            json.dump(self.info, file, indent=4)
    
    def MakeObstacles(self):
        self.entranceDoors = self.doors
        #self.exitDoor = None

        # For all except first room

        if (self.parentRoom):

            # self.info is empty room right now

            '''for d in self.doors:
                if (d.childRoom == self):
                    self.exitDoor = d
                    self.entranceDoors.remove(d)'''
            
            # Entrance and Exit doors established
        
            passing = False
            emptyRoom = self.info
            while not passing:
                emptyRoom = copy.deepcopy(self.info)
                walledRoom = emptyRoom
                passing = True
                for w in range(self.wallsPerRoom):
                    walledRoom = self.MakeWall(walledRoom)

                if (not self.exitDoor):
                    break

                for d in self.doors:
                    myAlgo = PathfindingScript.AStarMap(walledRoom, self.exitDoor.entrancePos, d.exitPos)
                    myAlgo.MakeAlgo()
                    if (len(myAlgo.path) == 0):
                        passing = False
                        break
            self.info = walledRoom
        #else:
            #self.info = self.MakeWall(self.info)
        with open(f'MapFiles/{self.fileName}.json', 'w') as file:
            json.dump(self.info, file, indent=4)

        ##

    def MakeWall(self, input):
        info = input
        xLength = len(info[0])
        yLength= len(info)

        myPos = [random.randint(2, xLength-1), random.randint(2, yLength-1)]
        while (info[myPos[1]][myPos[0]] != "o"):
            myPos = [random.randint(2, xLength-1), random.randint(2, yLength-1)]

        for i in range(self.maxWallSize):
            # WORKING ON THIS

            if (info[myPos[1]][myPos[0]] != "z" and myPos[0] != 0 and myPos[0] != len(info[0]) - 1 and myPos[1] != 0 and myPos[1] != len(info) - 1):
                info[myPos[1]][myPos[0]] = "x"
            directions = random.choice([[[-1, 1],[0]], [[0],[-1, 1]]])
            if (myPos[0] < 2 and -1 in directions[0]): directions[0].remove(-1)
            if (myPos[0] > len(info[0]) - 2 and 1 in directions[0]): directions[0].remove(1)

            if (myPos[1] < 2 and -1 in directions[1]): directions[1].remove(-1)
            if (myPos[1] > len(info) - 2 and 1 in directions[1]): directions[1].remove(1)

            myPos[0] = myPos[0] + random.choice(directions[0])
            myPos[1] = myPos[1] + random.choice(directions[1])

            if (random.randint(1, self.termChance) == self.termChance - 1):
                return info
        
        return info

    def MakeConditions(self, tile, x, y):
        conditions = []
        for i in range(3):
            yToCheck = y + i - 1
            for j in range(3):
               
                xToCheck = x + j - 1
                try:
                    if (xToCheck == x and yToCheck == y):
                        pass
                    elif (xToCheck == -1 or yToCheck == -1):
                        conditions.append(1)
                    elif (self.info[yToCheck][xToCheck] == tile):
                        conditions.append(1)
                    else:
                        conditions.append(-1)
                except IndexError:
                    conditions.append(1)

        return conditions
    
    def GenerateMap(self, player):
        mapFile = self.fileName
        map = self.map
        self.tileList = []
        contents = open("MapFiles/" + str(mapFile) + ".json", "r")
        #self.info = json.load(contents)
        self.obstacles = []

        yCoord = 0
        xCoord = 0



        for y in self.info:
            xCoord = 0
            for t in self.info[yCoord]:
                if (t == "x"):
                    conditions = self.MakeConditions("x", xCoord, yCoord)
                elif (t == "z"):
                    conditions = self.MakeConditions("z", xCoord, yCoord)
                else:
                    conditions = [0, 0, 0,
                                  0, 0,
                                  0, 0, 0]

                newTile = Tile(t, xCoord, yCoord, conditions, self.tiles)
                self.tileList.append(newTile)
                xCoord += 1
            yCoord += 1

        for t in self.tileList:
            if (t.tileLetter == "x" or t.tileLetter == "z"):
                self.obstacles.append(ObstaclesScript.Obstacle(t.hitbox[0], t.hitbox[1], t.hitbox[2], t.hitbox[3]))
            
        
        self.enemyGroup = EnemyScripts.enemy_group(self, player)
        self.activeEnemydProjectiles = []
    
    def CheckDoorCollisions(self, playerHitbox, player):

        self.entranceDoors = self.doors
        
        # For all except first room

        for d in self.doors:

            count = 0
                        
            for i in range(len(d.entranceFacing)):
                if d.exitFacing[i] == player.facingDir[i] and d.exitFacing[i] != 0:
                    count += 1
            
            if (count == 0):
                continue
            
            if (pygame.Rect.colliderect(d.exitHitbox, playerHitbox)):
                d.TransitionRooms(d.childRoom, player)
                player.xPos = d.entrancePos[0] * 64 + 32
                player.yPos = d.entrancePos[1] * 64 + 32
        
        if (self.exitDoor):
            #pygame.draw.rect(pygame.display.get_surface(), (255, 255, 255), self.exitDoor.entranceHitbox)
            if (pygame.Rect.colliderect(self.exitDoor.entranceHitbox, playerHitbox)):
                count = 0
                for i in range(len(self.exitDoor.entranceFacing)):
                    if self.exitDoor.entranceFacing[i] == player.facingDir[i] and self.exitDoor.entranceFacing[i] != 0: count += 1
                if count == 0:
                    return
                self.exitDoor.TransitionRooms(self.exitDoor.parentRoom, player)
                player.xPos = self.exitDoor.exitPos[0] * 64 + 32
                player.yPos = self.exitDoor.exitPos[1] * 64 + 32
    
    def ClearRoom(self):
        self.roomCleared = True

        if (self.map.upgradesTracker):
            self.map.upgradesTracker.SpawnUpgrade(self)


        
    
    
            


class Door:
    def __init__(self, parentRoom, childRoom):
        # Entrance : goes to child
        # Exit : goes to parent

        self.parentRoom = parentRoom
        self.childRoom = childRoom

        self.map = parentRoom.map

        self.exitPos = self.GetExitPos()
        self.entrancePos = self.GetEntrancePos(self.exitPos)

        self.exitHitbox = pygame.Rect(self.exitPos[0] * 64, self.exitPos[1] * 64, 64, 64)
        self.entranceHitbox = pygame.Rect(self.entrancePos[0] * 64, self.entrancePos[1] * 64, 64, 64)

        parentRoom.doors.append(self)
        childRoom.exitDoor = self

        self.parentRoom.info[self.exitPos[1]][self.exitPos[0]] = "o"
        self.childRoom.info[self.entrancePos[1]][self.entrancePos[0]] = "o"

    def GetExitPos(self):
        offset = (self.childRoom.mapPos[0] - self.parentRoom.mapPos[0], self.childRoom.mapPos[1] - self.parentRoom.mapPos[1])
        self.exitFacing = [offset[0], -offset[1]]
        self.entranceFacing = [-offset[0], offset[1]]

        r = None

        match offset:
            case (0, 1):
                while not r or self.parentRoom.info[0][r + 1] == "o" or self.parentRoom.info[0][r - 1] == "o":
                    r = random.randint(2, self.parentRoom.xLen - 2)
                return (r, 0)
            case (-1, 0):
                while not r or self.parentRoom.info[r + 1][0] == "o" or self.parentRoom.info[r - 1][0] == "o":
                    r = random.randint(2, self.parentRoom.xLen - 2)
                return (0, r)
            case (1, 0):
                while not r or self.parentRoom.info[r + 1][self.parentRoom.xLen - 1] == "o" or self.parentRoom.info[r - 1][self.parentRoom.xLen - 1] == "o":
                    r = random.randint(2, self.parentRoom.yLen - 2)
                return (self.parentRoom.xLen - 1, r)
            case (0, -1):
                while not r or self.parentRoom.info[self.parentRoom.yLen - 1][r + 1] == "o" or self.parentRoom.info[self.parentRoom.yLen - 1][r - 1] == "o":
                    r = random.randint(2, self.parentRoom.xLen - 2)
                return (r, self.parentRoom.yLen - 1)
    
    def GetEntrancePos(self, exitDoorPos):
        returnValue = list(exitDoorPos)

        if (exitDoorPos[0] == 0):
            returnValue[0] = self.childRoom.xLen - 1
        if (exitDoorPos[0] == self.childRoom.xLen - 1):
            returnValue[0] = 0
        if (exitDoorPos[1] == 0):
            returnValue[1] = self.childRoom.yLen - 1
        if (exitDoorPos[1] == self.childRoom.yLen - 1):
            returnValue[1] = 0

        return returnValue

    def TransitionRooms(self, nextRoom, player):
        self.map.currentRoom = nextRoom
        self.map.currentRoom.GenerateMap(player)

        if (self.map.upgradesTracker):
            if ("floating_shield" in self.map.upgradesTracker.heldUpgrades):
                self.map.upgradesTracker.shield = 1
        

    
        






class Tile:
    def __init__(self, tileType, xCoord, yCoord, conditions, info, tileSize = 64):
        self.map = map

        self.xCoord = xCoord
        self.yCoord = yCoord

        self.tileLetter = tileType

        self.info = info

        self.hitbox = (xCoord * tileSize, yCoord * tileSize, tileSize, tileSize)

        myTile = "wallTile1"

        if (tileType == "o"):
            tileType = "groundTiles"
            listOfTiles = list(self.info["groundTiles"].keys())
            myTile = random.choice(listOfTiles)

        elif (tileType == "x"):
            tileType = "wallTiles"
            listOfTiles = list(self.info["wallTiles"].keys())

            myTile = self.FindTileMatch("wallTiles", conditions)
        
        elif (tileType == "z"):
            
            tileType = "borderTiles"

            myTile = self.FindTileMatch("borderTiles", conditions)

        # ERROR HERE

        tileFile = self.info[tileType][myTile]["fileName"]

        self.displayTile = "Images/Tileset/" + tileFile + ".png"

        self.tileImage = pygame.image.load(self.displayTile).convert_alpha()
        imageSize = self.tileImage.get_size()
        scaleModifier = tileSize / imageSize[0]
        self.tileImage = pygame.transform.scale(self.tileImage, (imageSize[0] * scaleModifier, imageSize[1] * scaleModifier)).convert_alpha()

        self.position = [xCoord * tileSize, yCoord * tileSize]
    
    def FindTileMatch(self, tileType, conditions):
        defaultTile = "wallTile1"
        myTile = defaultTile
        if (tileType == "wallTiles"):
            possibleMatch = True

            for t in (self.info["wallTiles"].keys()):
                possibleMatch = True
                restrictions = self.info["wallTiles"][t]["restrictions"]
                matchCount = 0
                greatestMatch = 0

                for r in range(8):
                    if restrictions[r] == -conditions[r]:
                        possibleMatch = False
                    if restrictions[r] == conditions[r]:
                        matchCount += 1

                if (possibleMatch == True):
                    if (matchCount > greatestMatch):
                        greatestMatch = matchCount
                        myTile = t
        
        elif (tileType == "borderTiles"):
            possibleMatch = True

            for t in (self.info["borderTiles"].keys()):
                possibleMatch = True
                restrictions = self.info["borderTiles"][t]["restrictions"]
                matchCount = 0
                greatestMatch = 0

                if (conditions == restrictions):
                    myTile = t
                    return myTile

                for r in range(8):
                    if restrictions[r] == -conditions[r]:
                        possibleMatch = False
                    if restrictions[r] == conditions[r]:
                        matchCount += 1

                if (possibleMatch == True):
                    if (matchCount > greatestMatch):
                        greatestMatch = matchCount
                        myTile = t

            #myTile = self.info["borderTiles"]["borderTile1"]

        return myTile
    
    def DrawTile(self, screen):
        screen.blit(self.tileImage, self.position)

map = Map(8, 6, 8)

map.MakeNewMap()
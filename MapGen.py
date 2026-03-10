import pygame
import sys
import math
import numpy as np
import random
import os
import json
import PathfindingScript
import ObstaclesScript

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

class Room:
    def __init__(self, mapPos, parentRoom = None):
        self.doors = []

        self.parentRoom = parentRoom

        self.tileList = []

        self.mapPos = mapPos

        self.info = []

        self.termChance = 6
        self.maxWallSize = 4
        self.wallsPerRoom = 9
        
        with open("TileSetStuffs/TileHandling.json", "r") as tileSheetFile:
            self.tiles = json.load(tileSheetFile)

        self.imageLibrary = {}
    
    def MakeNewRandomMap(self, fileName):
        y = 10
        x = 14

        info = []

        self.fileName = fileName

        
        for i in range(y):
            xList = []
            for t in range(x):
                if (i == 0 or i == y - 1 or t == 0 or t == x - 1):
                    xList.append("z")
                    continue
                xList.append("o")
            info.append(xList)
        
        #HERE FOR DOORS
            
        for i in range(self.wallsPerRoom):
            info = self.MakeWall(info)

        self.info = info

        with open(f'MapFiles/{self.fileName}.json', "w") as map:
            json.dump(info, map, indent=4)

        #self.GenerateMap(fileName)
    
    def MakeWall(self, info):
        xLength = len(info[0])
        yLength= len(info)

        myPos = [random.randint(2, xLength-1), random.randint(2, yLength-1)]
        while (info[myPos[1]][myPos[0]] != "o"):
            myPos = [random.randint(2, xLength-1), random.randint(2, yLength-1)]

        for i in range(self.maxWallSize):
            if (info[myPos[1]-1][myPos[0]-1] != "z"):
                info[myPos[1]-1][myPos[0]-1] = "x"
            directions = random.choice([[[-1, 1],[0]], [[0],[-1, 1]]])
            if (myPos[0] == 0 and -1 in directions[0]): directions[0].remove(-1)
            if (myPos[0] == len(info[0]) and 1 in directions[0]): directions[0].remove(1)

            if (myPos[1] == 0 and -1 in directions[1]): directions[1].remove(-1)
            if (myPos[1] == len(info) and 1 in directions[1]): directions[1].remove(1)

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
    
    def GenerateMap(self, mapFile, map):
        contents = open("MapFiles/" + str(mapFile) + ".json", "r")
        self.info = json.load(contents)
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

                newTile = Tile(t, xCoord, yCoord, conditions, self.info)
                self.tileList.append(newTile)
                xCoord += 1
            yCoord += 1

        for t in self.tileList:
            if (t.tileLetter == "x" or t.tileLetter == "z"):
                self.obstacles.append(ObstaclesScript.Obstacle(t.hitbox[0], t.hitbox[1], t.hitbox[2], t.hitbox[3]))
        
        map.currentRoom = self
        
        
    
    #def CheckDoors():
        
    
    def DrawMap(self, screen):
        for t in self.tileList:
            t.DrawTile(screen)

class Map:
    def __init__(self, x, y, startRoom):
        self.layout = []

        self.startRoom = startRoom

        self.xLen = x
        self.yLen = y

        for i in range(y):
            xList = []
            for j in range(x):
                xList.append("x")
            self.layout.append(xList)
    
    def RandomizeMapLayout(self, numOfRooms):
        info = self.layout
        startPos = self.startRoom
        self.roomList = []

        startRoom = self.MakeRoom((startPos[0], startPos[1]))
        self.currentRoom = startRoom

        current = startRoom

        for r in range(numOfRooms):
            self.roomList.append(current)
            currentPos = (current.mapPos)

            info[currentPos[1] - 1][currentPos[0]] = "o"

            nextPos = self.GetRandomAdjacent((currentPos[0], currentPos[1]))

            nextRoom = self.MakeRoom(nextPos, current)

            current = nextRoom

        for r in range(len(self.roomList)):
            current = self.roomList[r]
            print(current.mapPos)
            try:
                next = self.roomList[r+1]
            except:
                next = None

            #if (current.parentRoom):
            #    pass

            if (next):
                doorPos = self.GetNewDoorPos(current, next)
                exitDoor = Door(current, next, doorPos, "parent", self)
                
                current.doors.append(exitDoor)

            with open(f'MapFiles/{current.fileName}.json', "w") as map:
                json.dump(current.info, map, indent=4)

        with open("CurrentMap.json", "w") as map:
            json.dump(info, map, indent=4)
    
        startRoom.GenerateMap(startRoom.fileName, self)
    
    def GetNewDoorPos(self, fromRoom, toRoom):
        xLen = len(fromRoom.info[0]) - 1
        yLen = len(fromRoom.info) - 1
        

        offset = (toRoom.mapPos[0] - fromRoom.mapPos[0], toRoom.mapPos[1] - fromRoom.mapPos[1])

        if (offset == (1, 0)):
            r = random.randint(-1, yLen - 1)
            return(xLen, r)
        if (offset == (-1, 0)):
            r = random.randint(1, yLen - 1)
            return (0, r)
        if (offset == (0, 1)):
            r = random.randint(1, xLen - 1)
            return(r, 0)
        if (offset == (0, -1)):
            r = random.randint(1, xLen - 1)
            return(r, yLen)

    
    def MakeRoom(self, mapPos, parentRoom = None):

        mapName = f'RandomMap{mapPos}'
        
        newRoom = Room(mapPos, parentRoom)
        newRoom.MakeNewRandomMap(mapName)
    
        '''

        if (parentRoom):
            while True:
                newRoom = Room(mapPos)
                newRoom.MakeNewRandomMap(mapName)
                
                myAlgo = PathfindingScript.AStarMap(mapName, newRoom.doors[0], newRoom.doors[1])
                myAlgo.MakeAlgo(mapName)

                if (len(myAlgo.path) > 0):
                    break
        '''
        
        return(newRoom)
        


    
    #def TransitionRooms(self, currentRoom, nextRoom):
    
    def GetRandomAdjacent(self, checkPos):
        positionsToCheck = [(checkPos[0], checkPos[1] - 1),
                            (checkPos[0] - 1, checkPos[1]),
                            (checkPos[0] + 1, checkPos[1]),
                            (checkPos[0], checkPos[1] + 1)]
    
        for p in positionsToCheck:
            if (p[0] < 0 or p[0] > self.xLen - 1
                or p[1] < 0 or p[1] > self.yLen - 1):
                positionsToCheck.remove(p)

        chosenPos = random.choice(positionsToCheck)
        
        return(chosenPos)

class Door:
    def __init__(self, fromRoom, toRoom, position, type, myMap):
        tileSize = 64

        self.fromRoom = fromRoom
        self.toRoom = toRoom

        self.myPos = position

        self.map = myMap
        
        fromRoom.info[self.myPos[1]][self.myPos[0]] = "o"

        xPos = position[0] * 64
        yPos = position[1] * 64

        self.hitbox = pygame.Rect(xPos, yPos, 32, 32)
    
    def CheckContact(self, playerCollider):
        if (pygame.Rect.colliderect(self.hitbox, playerCollider)):
            self.TransitionRooms()
    
    def TransitionRooms(self):
        self.toRoom.GenerateMap(self.toRoom.fileName, self.map)

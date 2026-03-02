import pygame
import sys
import math
import numpy as np
import random
import os
import json

class Tile:
    def __init__(self, tileType, xCoord, yCoord, conditions, tileSize = 64):
        self.map = map

        self.xCoord = xCoord
        self.yCoord = yCoord

        self.tileLetter = tileType

        self.tileSheetFile = open("TileSetStuffs/TileHandling.json", "r")
        self.info = json.load(self.tileSheetFile)

        self.displayTile = None

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
    
    def DrawTile(self, tileSize = 64):

        position = [(self.xCoord) * tileSize, (self.yCoord) * tileSize]

        tileImage = pygame.image.load(self.displayTile).convert_alpha()
        imageSize = tileImage.get_size()
        scaleModifier = tileSize / imageSize[0]
        tileImage = pygame.transform.scale(tileImage, (imageSize[0] * scaleModifier, imageSize[1] * scaleModifier)).convert_alpha()

        return(tileImage, position)

class Map:
    def __init__(self):
        self.tileList = []

        self.info = {}

        self.termChance = 6
        self.maxWallSize = 4
        self.wallsPerRoom = 9
    
    def MakeNewRandomMap(self):
        y = 10
        x = 14

        info = []

        for i in range(y):
            xList = []
            for t in range(x):
                if (i == 0 or i == y - 1 or t == 0 or t == x - 1):
                    xList.append("z")
                    continue
                xList.append("o")
            info.append(xList)
            

        for i in range(self.wallsPerRoom):
            info = self.MakeWall(info)

        with open("MapFiles/RandomMap.json", "w") as map:
            json.dump(info, map, indent=4)

        self.GenerateMap("RandomMap")
    
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


    
    def GenerateMap(self, mapFile):
        contents = open("MapFiles/" + str(mapFile) + ".json", "r")
        self.info = json.load(contents)

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

                newTile = Tile(t, xCoord, yCoord, conditions)
                self.tileList.append(newTile)
                xCoord += 1
            yCoord += 1
    
    def DrawMap(self):
        for t in self.tileList:
            t.DrawTile()



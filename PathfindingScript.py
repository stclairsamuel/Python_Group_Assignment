import json
import pygame
import numpy as np

class AStarMap:
    def __init__(self, info, startPos, endPos):
        
        self.open = [AStarTile(startPos, startPos, endPos)]
        self.closed = []
        
        self.positionDict = {}
        
        self.startPos = startPos
        self.endPos = endPos
    
        self.info = []

        self.running = True

        self.path = []

        self.info = info
    
    def MakeAlgo(self):
        while self.open:
            current = min(self.open, key=lambda tile: tile.fValue)
            
            self.open.remove(current)
            self.closed.append(current)

            if (current.position == self.endPos):
                self.FindPath(current)
                self.running = False
                return
            
            self.CheckAdjacent(current.position, current)

    def CheckAdjacent(self, checkPos, parentTile):
        positionsToCheck = ((checkPos[0], checkPos[1] - 1),
                            (checkPos[0] - 1, checkPos[1]),
                            (checkPos[0] + 1, checkPos[1]),
                            (checkPos[0], checkPos[1] + 1))
    
        for i in positionsToCheck:
            try:
                myList = []
                for x in self.closed:
                    myList.append(x.position)
                if (not self.info[i[1]][i[0]] == "o" or (i in myList)):
                    continue
                myList = []
                for x in self.open:
                    myList.append(x.position)
                if (i not in myList):
                    self.open.append(AStarTile(i, self.startPos, self.endPos, parentTile))
            except IndexError:
                continue

    
    def FindPath(self, endTile):
        current = endTile
        while (current):
            self.path.append(current.position)
            current = current.parent
        self.running = False


class AStarTile:
    def __init__(self, position, start, end, myParent = None):
        self.position = position
        self.hValue = np.abs(end[0] - position[0]) + np.abs(end[1] - position[1])
        self.gValue = np.abs(start[0] - position[0]) + np.abs(start[1] - position[1])
        self.fValue = self.gValue + self.hValue

        self.parent = myParent
            


myAlgo = AStarMap("RandomMap", [2, 2], [10, 8])
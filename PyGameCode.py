import pygame
import sys
import math
import numpy as np
import random
import os
import json

pygame.init()

keycodes = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
}

obstacles = []

pWidth = 15
pHeight = 15

acceleration = 4000
maxSpeed = 400
speed = maxSpeed
dashSpeed = 800
xVel = 0
yVel = 0
drag = 0.995

maxHealth = currentHealth = 5

dt = 0

tileSize = 64

mapPath = "MapFiles/TestMap.json"
mapFile = open(mapPath, "r")
mapContents = json.load(mapFile)

SCREEN_WIDTH = len(mapContents[0]) * tileSize
SCREEN_HEIGHT = len(mapContents) * tileSize

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (200, 230, 83)
RED = (255, 0, 0)

playerColor = GREEN



# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Text Display")


imagePath = os.path.join("Images", "Background_Image_Test-export.png")

backgroundImage = pygame.image.load(imagePath).convert_alpha()

width = backgroundImage.get_width()
height = backgroundImage.get_height()
scale = 1

bigBgImage = pygame.transform.smoothscale(backgroundImage, (width * scale, height * scale)).convert_alpha()





imageRect = backgroundImage.get_rect()

xPos = SCREEN_WIDTH / 2
yPos = SCREEN_HEIGHT / 2

playerHitbox = pygame.Rect(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, pWidth, pHeight)

running = True

clock = pygame.time.Clock()

yInput = 0
xInput = 0

getInput = True

isDashing = False
dashTime = 0.2
dashTimer = 0

dashCdTime = 0.2
dashCdTimer = 0

iFrameTime = 0.2
iFrameTimer = 0

dashDir = [0, 0]

magnitude = 0

inpList = []

projectiles = []

spawnProjTime = 1
spawnProjTimer = 0

projSize = 10

def ReflectVector(vectorToReflect, normal):
    # R = V - 2(V DOT N)N

    reflectedVector = [0, 0]

    dotProduct = vectorToReflect[0] * normal[0] + vectorToReflect[1] * normal[1]


    reflectedVector[0] - (2 * dotProduct * normal[0])
    reflectedVector[1] - (2 * dotProduct * normal[0])

    return reflectedVector

def Magnitude(vector):
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

def NormalizeVector(vector):
    magnitude = Magnitude(vector)

    try: 
        return [vector[0] / magnitude, vector[1] / magnitude]
    except:
        return [0, 0]


class Projectile:
    def __init__(self):

        if (random.choice([True, False])):
            self.xPos = random.randint(0, SCREEN_WIDTH)
            self.yPos = random.choice([0, SCREEN_HEIGHT])
        else:
            self.xPos = random.choice([0, SCREEN_WIDTH])
            self.yPos = random.randint(0, SCREEN_HEIGHT)

        self.xVel = 0
        self.yVel = 0

        self.size = 10

        self.acceleration = 300

        self.drag = 0.9

        self.lifeTime = self.lifeTimer = 10
    
    def Move(self):
        pPos = [xPos, yPos]
        myPos = [self.xPos, self.yPos]

        xDist = (pPos[0] - myPos[0])
        yDist = (pPos[1] - myPos[1])
        totalDist = NormalizeVector([xDist, yDist])

        #dirToPlayer = [xDist / totalDist, yDist / totalDist]

        #self.xVel += dirToPlayer[0] * self.acceleration * dt
        #self.yVel += dirToPlayer[1] * self.acceleration * dt

        #self.xPos += self.xVel * dt
        #self.yPos += self.yVel * dt
    
    def CheckCollision(self):
        global playerHitbox

        myPos = [self.xPos, self.yPos]

        myHitbox = pygame.Rect(myPos[0], myPos[1], self.size, self.size)

        return (pygame.Rect.colliderect(myHitbox, playerHitbox))

class Player:
    def __init__(self):
        self.xPos = SCREEN_WIDTH/2
        self.yPos = SCREEN_HEIGHT/2

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


    
    def GetInput(self):
        global running

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
            
        if (inpList[pygame.K_LSHIFT] and not dashCdTimer > 0):
            self.StartDash()
    
    def Move(self):
        global dt

        lastXVel = self.xVel
        lastYVel = self.yVel
        
        if ((self.xInput != 0 or self.yInput != 0)):
            inputVector = NormalizeVector([self.xInput, self.yInput])

            self.xVel += inputVector[0] * self.acceleration * dt
            self.yVel += inputVector[1] * self.acceleration * dt

            if (Magnitude([lastXVel, lastYVel]) > maxSpeed):
                self.xVel = self.xVel * (self.drag ** (dt * 1000))
                self.yVel = self.yVel * (self.drag ** (dt * 1000))

        else:
            self.xVel = self.xVel * (self.drag ** (dt * 1000))
            self.yVel = self.yVel * (self.drag ** (dt * 1000))

        speed = Magnitude([self.xVel, self.yVel])

        if (speed > maxSpeed and Magnitude([lastXVel, lastYVel]) <= maxSpeed):
            self.xVel = (self.xVel / speed) * self.maxSpeed
            self.yVel = (self.yVel / speed) * self.maxSpeed

        nextPos = [self.xPos + (self.xVel * dt), self.yPos + (self.yVel * dt)]

        self.CheckObstacles(nextPos)

        wallCheckDist = 2
        left = self.xPos - self.hitboxSize/2
        top = self.yPos - self.hitboxSize/2
        xFacingBox = pygame.Rect(left + self.facingDir[0] * wallCheckDist, top, self.hitboxSize, self.hitboxSize)
        yFacingBox = pygame.Rect(left, top - self.facingDir[1] * wallCheckDist, self.hitboxSize, self.hitboxSize)

        pygame.draw.rect(screen, WHITE, xFacingBox)
        pygame.draw.rect(screen, WHITE, yFacingBox)
        
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

    def CheckObstacles(self, nextPos):
        for o in obstacles:
            o.CheckPlayerCollision(self, [nextPos[0], nextPos[1]])
            
                

    #def StartDash(self):


    
    #def TakeDamage(self):

    
    #def Die(self):

player = Player()


class Obstacle:
    def __init__(self, x, y, w, h, friction = 0.98):
        self.xPos = x
        self.yPos = y
        self.width = w
        self.height = h

        self.friction = friction

        self.hitbox = pygame.Rect(x, y, w, h)

    def CheckPlayerCollision(self, player, predictedPos):
        global dt

        width = height = player.hitboxSize
        
        skinWidth = 0.02

        predictedX = predictedPos[0]
        predictedY = predictedPos[1]
        
        xHitbox = pygame.Rect(predictedX - width/2, player.yPos - height/2, width, height)
        yHitbox = pygame.Rect(player.xPos - width/2, predictedY - height/2, width, height)


    
        if (pygame.Rect.colliderect(self.hitbox, xHitbox)):
            if (player.xVel > 0):
                player.xPos = self.hitbox.left - width/2 - skinWidth
            if (player.xVel < 0):
                player.xPos = self.hitbox.right + width/2 + skinWidth
            player.xVel = 0

        if (pygame.Rect.colliderect(self.hitbox, yHitbox)):
            if (player.yVel > 0):
                player.yPos = self.hitbox.top - height/2 - skinWidth
            if (player.yVel < 0):
                player.yPos = self.hitbox.bottom + height/2 + skinWidth
            player.yVel = 0
        
        

    
    def DrawObstacle(self):
        #file = "Images/Tileset/PygameTileset-Sheet2.png"
        #image = pygame.image.load(file)
        #image = pygame.transform.scale(image, [128, 128]).convert_alpha()
        #screen.blit(image, [self.xPos, self.yPos])

        pygame.draw.rect(screen, WHITE, self.hitbox)
    
class Tile:
    def __init__(self, tileType, xCoord, yCoord, conditions):
        global obstacles

        self.map = map

        self.xCoord = xCoord
        self.yCoord = yCoord

        self.tileSheetFile = open("TileSetStuffs/TileHandling.json", "r")
        self.info = json.load(self.tileSheetFile)

        self.displayTile = None

        myTile = "wallTile1"

        if (tileType == "o"):
            tileType = "groundTiles"
            listOfTiles = list(self.info["groundTiles"].keys())
            myTile = random.choice(listOfTiles)

        elif (tileType == "x"):
            tileType = "wallTiles"
            listOfTiles = list(self.info["wallTiles"].keys())

            myTile = self.FindTileMatch("wallTiles", conditions)

            myObstacle = Obstacle(xCoord * tileSize, yCoord * tileSize, tileSize, tileSize)
            obstacles.append(myObstacle)

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

            
        return myTile
    
    def DrawTile(self):
        global tileSize

        position = [self.xCoord * tileSize, self.yCoord * tileSize]

        tileImage = pygame.image.load(self.displayTile).convert_alpha()
        imageSize = tileImage.get_size()
        scaleModifier = tileSize / imageSize[0]
        tileImage = pygame.transform.scale(tileImage, (imageSize[0] * scaleModifier, imageSize[1] * scaleModifier)).convert_alpha()

        screen.blit(tileImage, position)



        



class Map:
    def __init__(self, xSize, ySize):
        self.xSize = xSize
        self.ySize = ySize

        self.tileList = []

        self.info = {}
    
    def MakeNewRandomMap(self):
        y = 10
        x = 14

        yList = []
        xList = []

        for i in range(y):
            for t in range(x):
                xList.append(random.choice(["x", "o"]))
            yList.append(xList)
            xList = []

        with open("MapFiles/RandomMap.json", "w") as map:
            json.dump(yList, map, indent=4)

        self.GenerateMap("RandomMap")
    
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
                        conditions.append(-1)
                    elif (self.info[yToCheck][xToCheck] == "x"):
                        conditions.append(1)
                    else:
                        conditions.append(-1)
                except IndexError:
                    conditions.append(-1)

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
                    conditions = self.MakeConditions(t, xCoord, yCoord)
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



map = Map(4, 3)


mapFile = "TestMap"
map.GenerateMap(mapFile)

#map.MakeNewRandomMap()

def StartDash():
    global isDashing, dashTimer, dashDir

    isDashing = True
    dashTimer = dashTime
    normedXVel = xVel/magnitude
    normedYVel = yVel/magnitude
    dashDir = [normedXVel, normedYVel]


def Die():
    pygame.quit()

def TakeDamage():
    global iFrameTimer, currentHealth

    currentHealth -= 1

    iFrameTimer = iFrameTime

    if (currentHealth <= 0):
        Die()

def SpawnProjectile():
    newProjectile = Projectile()

    projectiles.append(newProjectile)

def CreateHealthBar():
    global currentHealth

    imagePath = os.path.join("Images", "PygameHeart.png")

    heartImage = pygame.image.load(imagePath).convert_alpha()

    scale = 2
    width = heartImage.get_width()
    height = heartImage.get_height()

    pygame.draw.rect(screen, WHITE, (30, 35, 210, 40))

    biggerHeart = pygame.transform.scale(heartImage, (width * scale, height * scale)).convert_alpha()

    horizontalDistance = 40

    position1 = [40, 40]

    for i in range(currentHealth):
        screen.blit(biggerHeart, (position1[0] + (i * horizontalDistance), position1[1]))


def Timers():
    global dashTimer, dashCdTimer, spawnProjTimer, iFrameTimer

    if (dashTimer > 0):
        player.dashTimer -= dt
    else:
        player.dashTimer = 0
    
    if (dashCdTimer > 0):
        player.dashCdTimer -= dt
    else:
        player.dashCdTimer = 0

    if (spawnProjTimer > 0):
        spawnProjTimer -= dt
    else:
        spawnProjTimer = spawnProjTime
        SpawnProjectile()
    
    if (iFrameTimer > 0):
        player.iFrameTimer -= dt
    else:
        player.iFrameTimer = 0

# Game Running

while running:
    dt = clock.tick() / 1000.0

    if (getInput):
        player.GetInput()
    
    player.Move()




    
    

    # Drawing
    screen.fill(WHITE) # Fill screen with white background

    screen.blit(bigBgImage, imageRect)


    map.DrawMap()

    if (iFrameTimer > 0):
        playerColor = RED
    else:
        playerColor = GREEN

    pygame.draw.circle(screen, playerColor, [player.xPos, player.yPos], 20)

    for p in projectiles:
        pygame.draw.circle(screen, RED, [p.xPos, p.yPos], p.size)
        p.Move()
    
    for p in projectiles:
        p.lifeTimer -= dt
        outOfBounds = (not (0 < xPos and xPos < SCREEN_WIDTH) or not (0 < yPos and yPos < SCREEN_HEIGHT))
        if (p.lifeTimer <= 0 or outOfBounds):
            projectiles.remove(p)
    
        if (p.CheckCollision() and iFrameTimer == 0):
            TakeDamage()
    
    # Timers
    Timers()

    CreateHealthBar()

    #for o in obstacles:
        #o.DrawObstacle()
    
    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()

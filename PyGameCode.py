import pygame
import sys
import math
import numpy as np
import random
import os

pygame.init()

keycodes = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
}

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

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
                self.yVel *= (self.drag ** (dt * 1000))
            if (self.movingInto[1] and self.yInput):
                self.xVel *= (self.drag ** (dt * 1000))
        
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
    def __init__(self, x, y, w, h):
        self.xPos = x
        self.yPos = y
        self.width = w
        self.height = h

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
        pygame.draw.rect(screen, WHITE, self.hitbox)
    
obstacles = [
    Obstacle(150, 250, 100, 100),
    Obstacle(300, 400, 50, 50),
    Obstacle(500, 100, 100, 200)
]

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

    for o in obstacles:
        o.DrawObstacle()
    
    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()

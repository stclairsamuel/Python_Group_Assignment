import pygame
import PlayerScript

class Obstacle:
    def __init__(self, x, y, w, h, friction = 0.98):
        self.xPos = x
        self.yPos = y
        self.width = w
        self.height = h

        self.friction = friction

        self.hitbox = pygame.Rect(x, y, w, h)

    def CheckPlayerCollision(self, player, predictedPos, dt):
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
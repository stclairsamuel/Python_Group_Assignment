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

class sprite_renderer:
    # a sprite renderer prints an image onto the 
    #   current screen surface based on its x position
    #   and y position

    def __init__(self, parent, startImage = None):
        self.parent = parent

        self.animator = None
        self.startImage = startImage
        self.currentImage = startImage

        self.screen = pygame.display.get_surface()

        self.colorMask = None

        self.reflected = False

        self.scale = 1
    
    def Render(self, dt):
        if (self.animator):
            self.animator.Update(dt)

        if (self.animator):
            self.currentImage = self.animator.currentFrame

        # get the game object's x position and y position
        # if the game object does not have x and y positions, return

        try:
            xPos = self.parent.xPos
            yPos = self.parent.yPos
        except:
            print(f'{self.parent} does not have a readable position')
            return

        if (self.animator):
            pass

        if (self.currentImage):
            imageCenter = (xPos, yPos)
            imageSize = self.currentImage.get_size()

            drawPos = (imageCenter[0] - imageSize[0]/2, imageCenter[1] - imageSize[1]/2)

            maskSurf = self.currentImage.copy()

            if (self.colorMask):
                if self.colorMask == (255, 255, 255):
                    maskSurf.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    maskSurf.fill((*self.colorMask, 255), special_flags=pygame.BLEND_RGBA_MULT)

                self.screen.blit(maskSurf, drawPos)
            
            else:
                self.screen.blit(self.currentImage, drawPos)
    
    def SetImage(self, image):
        self.currentImage = image
    
    def ReflectSprite(self):
        if (self.animator):
            for i in self.animator.animationList:
                for j in range(len(self.animator.animations[i].frames)):
                    frameList = self.animator.animations[i].frames
                    normalImage = frameList[j]
                    currentSize = normalImage.get_size()
                    newImage = pygame.transform.flip(normalImage, True, False)
                    frameList[j] = newImage


    
    def ChangeSize(self, newScale):
        if (self.animator):
            for i in self.animator.animationList:
                for j in range(len(self.animator.animations[i].frames)):
                    frameList = self.animator.animations[i].frames
                    normalImage = frameList[j]
                    currentSize = normalImage.get_size()
                    widthRatio = currentSize[1]/currentSize[0]
                    newImage = pygame.transform.scale(normalImage, (64 * newScale, 64 * newScale * widthRatio)).convert_alpha()
                    frameList[j] = newImage
                    self.scale = newScale

        else:
            normalImage = self.currentImage
            currentSize = normalImage.get_size()
            widthRatio = currentSize[1]/currentSize[0]
            newImage = pygame.transform.scale(normalImage, (64 * newScale, 64 * newScale * widthRatio)).convert_alpha()
            self.currentImage = newImage
    
        self.scale = newScale
    
    
    def SetRotation(self, rotation):
        if (self.animator):
            for i in self.animator.animationList:
                for j in range(len(self.animator.animations[i].frames)):
                    frameList = self.animator.animations[i].frames
                    normalImage = frameList[j]
                    newImage = pygame.transform.rotate(normalImage, rotation)
                    frameList[j] = newImage
    
    def SetColorMask(self, color):
        self.colorMask = color

    '''def ChangeImage(self, image):
        imageSize = image.get_size()
        newImage = pygame.transform.scale(image, imageSize[0] * self.scale, imageSize[1] * self.scale)
        self.currentImage = newImage'''


class animator:
    def __init__(self, infoFilePath, renderer):
        self.animations = {}

        renderer.animator = self

        #self.animationTimes = 0.3

        self.animationTimer = 0
        
        with (open(f'{infoFilePath}.json')) as file:
            self.animatorFile = file
            contents = json.load(file)
            
            for a in contents.keys():
                self.animations[a] = animation(infoFilePath, a)
            
            self.animationList = list(self.animations.keys())
            
        self.currentAnimation = self.animations[self.animationList[0]]

        self.currentFrame = self.currentAnimation.frames[0]

        self.isAnimating = True
    
    def Update(self, dt):
        self.Timers(dt)

        if not (self.isAnimating):
            self.isAnimating = True
            return

        currentFrame = self.currentAnimation.GetFrame(self.animationTimer)

        #if (self.parent.xPos > self.parent.target.xPos):
        #    currentFrame = pygame.transform.flip(currentFrame, True, False).convert_alpha()

        frameSize = pygame.Surface.get_size(currentFrame)
        
        self.currentFrame = currentFrame

    def SwitchAnimation(self, animationName):
        if (animationName not in self.animationList):
            print(f'animation {animationName} does not exist')
            return
        
        self.currentAnimation = self.animations[animationName]

        self.animationTimer = 0
        

    def Timers(self, dt):
        if (self.animationTimer >= self.currentAnimation.animTime):
            self.animationTimer -= self.currentAnimation.animTime
            self.isAnimating = False
        self.animationTimer += dt

class animation:
    def __init__(self, fileName, animationName):
        self.fileName = fileName
        self.animName = animationName

        self.animTime = 0.6

        self.frames = []

        scale = 2.4

        with open(f'{self.fileName}.json') as file:
            contents = json.load(file)

            if (animationName not in contents.keys()):
                print(f'error: animation {animationName} not in {fileName}')
                return
            
            images = [pygame.image.load(f'{f}.png').convert_alpha() for f in contents[animationName]]

            self.frames = [pygame.transform.scale(i, (pygame.Surface.get_size(i)[0] * scale, pygame.Surface.get_size(i)[1] * scale)).convert_alpha() for i in images]
    
    def GetFrame(self, timer):
        numOfFrames = len(self.frames)

        timePerFrame = self.animTime / numOfFrames

        currentFrameInt = min(int(timer / timePerFrame), numOfFrames - 1)

        if currentFrameInt >= numOfFrames:
            currentFrameInt = numOfFrames - 1

        returnFrame = self.frames[currentFrameInt]

        return returnFrame
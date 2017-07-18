import pygame
import os
import copy
import random
from mainGame import GameObject
from mapBoard import map
from mapBoard import rowOfMap, colOfMap
from mapBoard import entranceRowOne, entranceRowTwo, entranceColOne
from mapBoard import entranceColTwo


########################################################
# Base class for characters in the game such as player,
# monster, animals......
########################################################

# Use to load the image in certain file into the required list
def initImgFromPath(path, l):
    temp = []
    absPath = os.path.join(os.path.dirname(__file__), path)
    for image in os.listdir(absPath):
        temp.append(absPath + "/" + image)
    for path in temp:
        # Make sure the file is a png image
        if("png" in path):
            l.append(pygame.image.load(path))

class Character(pygame.sprite.Sprite):

    def __init__(self, health=100, attack=100, speed=4, PosX=32, PosY=32):
        super(Character, self).__init__()
        self.health = health
        self.fullHealth = health
        self.healthPercent = 1
        self.attack = attack
        # Position of player
        self.positionX = PosX
        self.positionY = PosY
        self.row = 2
        self.col = 2
        # The direction of player
        self.IsWalkUp = False
        self.IsWalkDown = False
        self.IsWalkLeft = False
        self.IsWalkRight = False
        self.attack = False
        self.attackRange = 10
        self.died = False
        self.isSelected = False
        self.cellWidth = 16
        self.cellHeight = 16
        self.rect = ()
        self.frameCount = 0 # Calculate which frame images show be display
        self.speed = speed
        self.rect



    def updateRec(self):
        w, h = self.frameImg.get_size()
        left, top = self.positionX, self.positionY
        self.rect = pygame.Rect((left, top), (w, h))

    # Loading image from specific path
    def initializeImage(self, subPath):
        initImgFromPath(subPath + "/walkRight", self.WalkRightAni)
        initImgFromPath(subPath + "/walkLeft", self.WalkLeftAni)
        initImgFromPath(subPath + "/walkUp", self.WalkDownAni)
        initImgFromPath(subPath + "/walkDown", self.WalkUpAni)

    # Get the row and col that are relative to the whole map
    def getRowandCol(self, smallScreen, x, y):
        dx = 2 * abs(smallScreen.currentX) + x
        dy = 2 * abs(smallScreen.currentY) + y
        (row, col) = (dy // self.cellHeight, dx // self.cellWidth)
        return (row, col)

    def keyPressed(self):
        pass

    def mousePressed(self, smallScreen):
        pass

    def redrawAll(self, screen, parameter):
        (width, height) = parameter
        color = (255, 0, 0)
        left = self.positionX
        top = self.positionY
        w, h = self.frameImg.get_size()
        test = (left, top, w, h)
        pygame.draw.rect(screen, color, self.rect)
        screen.blit(self.frameImg, ((self.positionX / width) * width,
                                    (self.positionY / height) * height))

    def update(self):
        self.updateRec()

###########################################
# Monster Class
###########################################

class Monster(Character):
    def __init__(self, posX, posY):
        self.positionX = posX
        self.positionY = posY
        self.speed = 2
        self.attackRange = 16
        self.cellWidth = 16
        self.cellHeight = 16
        self.WalkUpAni = []
        self.WalkDownAni = []
        self.WalkLeftAni = []
        self.WalkRightAni = []
        self.attackAni = []
        self.dieAni = []
        self.subPath = "monster"
        self.initializeImage(self.subPath)
        self.frameLength = len(self.WalkUpAni)
        self.frameImg = self.WalkLeftAni[0]  # frame image needed to be show
        super().__init__(100, 100, 1, posX, posY)
        self.attack = 1
        self.offsetX = 0
        self.offsetY = 0
        self.hasTarget = False
        self.target = Building()
        self.reach = 0
        self.targetX = 0
        self.targetY = 0
        self.path = []
        self.attackBullet = [] # List that used to store the bullet info

    def tryOtherDirection(self, direction, smallScreen):
        self.frameCount = (self.frameCount + 1) % self.frameLength
        up = (-1, 0)
        down = (+1, 0)
        left = (0, -1)
        right = (0, +1)
        dirs = [up, down, right, left]
        row, col = self.getRowandCol(smallScreen, self.positionX,
                                     self.positionY)
        for dir in dirs:
            if dir != direction:
                newPosY = self.positionY + dir[0] * self.speed
                newPosX = self.positionX + dir[1] * self.speed
                row, col = self.getRowandCol(smallScreen, newPosX, newPosY)
                path = (newPosX, newPosY)

                if map[row][col] != 1 and dir not in path:
                    self.path.append((self.positionX, self.positionY))
                    self.positionX = newPosX
                    self.positionY = newPosY
                    if dir == up:
                        self.frameImg = self.WalkUpAni[self.frameCount]
                    elif dir == down:
                        self.frameImg = self.WalkDownAni[self.frameCount]
                    elif dir == left:
                        self.frameImg = self.WalkLeftAni[self.frameCount]
                    elif dir == right:
                        self.frameImg = self.WalkRightAni[self.frameCount]
                    break

    # Search for the location of player and chase player
    def searchPlayer(self, smallScreen, targetX, targetY):
        self.frameCount = (self.frameCount + 1) % self.frameLength

        if (self.positionY > targetY + self.attackRange):
            newPosY = self.positionY - self.speed
            row, col = self.getRowandCol(smallScreen, self.positionX,
                                         newPosY)
            if(row >= 0 and row <= 44 and col >= 0 and col <= 44 and map[row][\
                    col] == 1):
                self.tryOtherDirection((+1, 0), smallScreen)
                return
            self.path.append((self.positionX, self.positionY))
            self.positionY = newPosY
            self.IsWalkDown = True
            (self.IsWalkUp, self.IsWalkLeft, self.IsWalkRight) = (False,
                                                                  False,
                                                                  False)
            self.frameImg = self.WalkDownAni[self.frameCount]
        elif (self.positionY < targetY - self.attackRange):
            newPosY = self.positionY + self.speed
            row, col = self.getRowandCol(smallScreen, self.positionX,
                                         newPosY)
            if (row >= 0 and row <= 44 and col >= 0 and col <= 44 and
                map[row][col] == 1):
                self.tryOtherDirection((-1, 0), smallScreen)
                return
            self.path.append((self.positionX, self.positionY))
            self.positionY = newPosY
            self.IsWalkUp = True
            (self.IsWalkDown, self.IsWalkLeft, self.IsWalkRight) = (False,
                                                                    False,
                                                                    False)
            self.frameImg = self.WalkUpAni[self.frameCount]
        elif (self.positionX < targetX - self.attackRange):
            newPosX = self.positionX + self.speed
            row, col = self.getRowandCol(smallScreen, newPosX, self.positionY)
            if(row >= 0 and row <= 44 and col >= 0 and col <= 44 and map[row][\
               col] == 1):
                self.tryOtherDirection((0, +1), smallScreen)
                return
            self.path.append((self.positionX, self.positionY))
            self.positionX = newPosX
            self.IsWalkRight = True
            (self.IsWalkUp, self.IsWalkDown, self.IsWalkLeft) = (False,
                                                                 False,
                                                                 False)
            self.frameImg = self.WalkRightAni[self.frameCount]
        elif (self.positionX > targetX + self.attackRange):
            newPosX = self.positionX - self.speed
            row, col = self.getRowandCol(smallScreen, newPosX, self.positionY)
            if(row >= 0 and row <= 44 and col >= 0 and col <= 44 and map[row][\
                    col] == 1):
                self.tryOtherDirection((0, -1), smallScreen)
                return
            self.path.append((self.positionX, self.positionY))
            self.positionX -= self.speed
            (self.IsWalkDown, self.IsWalkUp, self.IsWalkRight) = (False,
                                                                  False,
                                                                  False)
            self.frameImg = self.WalkLeftAni[self.frameCount]

    # test if player is in the range of attack
    def isInAttackRange(self, player):
        (player_width, player_height) = player.frameImg.get_size()
        return ((self.positionX >= player.positionX and
                 self.positionX <= player.positionX + player_width) or
                (self.positionY >= player.positionY and
                 self.positionY <= player.positionY + player_height))

    def update(self, smallScreen):
        super().update()
        if(self.hasTarget):
            if(isinstance(self.target, Building)):
                self.targetX = self.target.imageX + self.offsetX
                self.targetY = self.target.imageY + self.offsetY
            elif(isinstance(self.target, Player)):
                self.targetX = self.target.positionX
                self.targetY = self.target.positionY

            self.searchPlayer(smallScreen, self.targetX, self.targetY)
        w, h = self.frameImg.get_size()

    def drawHealthBar(self, screen, smallScreen):
        width = 30
        height = 2
        offsetY = 10
        if (self.healthPercent <= 0.5):
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)
        heal = int(self.healthPercent * width)
        healLength = heal * width

        #PosX = self.positionX - smallScreen.currentX
        #PosY = self.positionY - smallScreen.currentY
        PosX = self.positionX
        PosY = self.positionY

        start_p = (PosX, PosY - offsetY)
        end_p_one = (PosX + width, PosY - offsetY)
        end_p_two = (PosX + width, PosY - offsetY + height)
        end_p_thr = (PosX, PosY - offsetY + height)
        pygame.draw.line(screen, color, start_p, end_p_one)
        pygame.draw.line(screen, color, end_p_one, end_p_two)
        pygame.draw.line(screen, color, end_p_two, end_p_thr)
        pygame.draw.line(screen, color, end_p_thr, start_p)
        pygame.draw.rect(screen, color, ((start_p, (heal, height))))

    def drawSelectedArea(self, screen, smallScreen):
        color = (0, 255, 0)
        #PosX = self.positionX - smallScreen.currentX
        #PosY = self.positionY - smallScreen.currentY
        PosX = self.positionX
        PosY = self.positionY
        start_p = (PosX, PosY)
        end_p_one = (PosX + self.cellWidth * 2, PosY)
        end_p_two = (PosX + self.cellWidth * 2, PosY + 2 * self.cellHeight)
        end_p_thr = (PosX, PosY + 2 * self.cellHeight)
        pygame.draw.line(screen, color, start_p, end_p_one)
        pygame.draw.line(screen, color, end_p_one, end_p_two)
        pygame.draw.line(screen, color, end_p_two, end_p_thr)
        pygame.draw.line(screen, color, end_p_thr, start_p)

    def redrawAll(self, screen, smallScreen):
        screen.blit(self.frameImg, (self.positionX, self.positionY))
        self.drawSelectedArea(screen, smallScreen)
        self.drawHealthBar(screen, smallScreen)


#############################################################
# Player character
# Player can go four direction. The health will
# drop when attacked by enemy such as monster.
# can regain the health by eating food or use certain items
#############################################################

class Player(Character):
    def __init__(self, PosX=32, PosY=32):
        self.speed = 2
        self.positionX = PosX
        self.positionY = PosY
        self.WalkUpAni = []
        self.WalkDownAni = []
        self.WalkLeftAni = []
        self.WalkRightAni = []
        self.attackAni = []
        self.dieAni = []
        self.subPath = "player"
        self.initializeImage(self.subPath)
        self.frameLength = len(self.WalkUpAni)
        self.frameImg = self.WalkLeftAni[0]  # frame image needed to be show
        super().__init__(100, 100, 2, PosX, PosY)
        self.attackRange = 16
        self.hasTarget = False
        self.target = []
        self.targetX = 0
        self.targetY = 0
        self.isBeingAttack = False
        self.searchArea = 300
        self.starve = 0
        self.path = []
        self.isSelected = False


    def searchEnemy(self, smallScreen, targetX, targetY):
        playerxUp = self.positionX + self.searchArea
        playerxDown = self.positionX - self.searchArea
        playeryUp = self.positionY + self.searchArea
        playeryDown = self.positionY - self.searchArea

        if(self.hasTarget and ((targetX <= playerxUp and targetX >= playerxDown)
           and (targetY <= playeryUp and targetY >= playeryDown))):
            self.frameCount = (self.frameCount + 1) % self.frameLength

            if (self.positionY > targetY + self.attackRange):
                newPosY = self.positionY - self.speed
                row, col = self.getRowandCol(smallScreen, self.positionX,
                                             newPosY)
                if (map[row][col] == 1):
                    self.tryOtherDirection((+1, 0), smallScreen)
                    return
                self.path.append((self.positionX, self.positionY))
                self.positionY = newPosY
                self.IsWalkDown = True
                (self.IsWalkUp, self.IsWalkLeft, self.IsWalkRight) = (False,
                                                                      False,
                                                                      False)
                self.frameImg = self.WalkDownAni[self.frameCount]
            elif (self.positionY < targetY - self.attackRange):
                newPosY = self.positionY + self.speed
                row, col = self.getRowandCol(smallScreen, self.positionX,
                                             newPosY)
                if (map[row][col] == 1):
                    self.tryOtherDirection((-1, 0), smallScreen)
                    return
                self.path.append((self.positionX, self.positionY))
                self.positionY = newPosY
                self.IsWalkUp = True
                (self.IsWalkDown, self.IsWalkLeft, self.IsWalkRight) = (False,
                                                                        False,
                                                                        False)
                self.frameImg = self.WalkUpAni[self.frameCount]
            elif (self.positionX < targetX - self.attackRange):
                newPosX = self.positionX + self.speed
                row, col = self.getRowandCol(smallScreen, newPosX,
                                             self.positionY)
                if (map[row][col] == 1):
                    self.tryOtherDirection((0, +1), smallScreen)
                    return
                self.path.append((self.positionX, self.positionY))
                self.positionX = newPosX
                self.IsWalkRight = True
                (self.IsWalkUp, self.IsWalkDown, self.IsWalkLeft) = (False,
                                                                     False,
                                                                     False)
                self.frameImg = self.WalkRightAni[self.frameCount]
            elif (self.positionX > targetX + self.attackRange):
                newPosX = self.positionX - self.speed
                row, col = self.getRowandCol(smallScreen, newPosX,
                                             self.positionY)
                if (map[row][col] == 1):
                    self.tryOtherDirection((0, -1), smallScreen)
                    return
                self.path.append((self.positionX, self.positionY))
                self.positionX -= self.speed
                (self.IsWalkDown, self.IsWalkUp, self.IsWalkRight) = (False,
                                                                      False,
                                                                      False)
                self.frameImg = self.WalkLeftAni[self.frameCount]


    def tryOtherDirection(self, direction, smallScreen):
        self.frameCount = (self.frameCount + 1) % self.frameLength
        up = (-1, 0)
        down = (+1, 0)
        left = (0, -1)
        right = (0, +1)
        dirs = [up, down, right, left]
        row, col = self.getRowandCol(smallScreen, self.positionX,
                                     self.positionY)
        for dir in dirs:
            if dir != direction:
                newPosY = self.positionY + dir[0] * self.speed
                newPosX = self.positionX + dir[1] * self.speed
                row, col = self.getRowandCol(smallScreen, newPosX, newPosY)
                path = (newPosX, newPosY)

                if map[row][col] != 1 and dir not in path:
                    self.path.append((self.positionX, self.positionY))
                    self.positionX = newPosX
                    self.positionY = newPosY
                    if dir == up:
                        self.frameImg = self.WalkUpAni[self.frameCount]
                    elif dir == down:
                        self.frameImg = self.WalkDownAni[self.frameCount]
                    elif dir == left:
                        self.frameImg = self.WalkLeftAni[self.frameCount]
                    elif dir == right:
                        self.frameImg = self.WalkRightAni[self.frameCount]
                    break

    def updateTarget(self, screen):
        if (self.hasTarget):
            self.targetX = self.target[0].positionX
            self.targetY = self.target[0].positionY

    def update(self, screen, parameter):
        super().update()
        # Update the info of target if player has target
        self.updateTarget(screen)
        # Update the frame picture of animation
        self.frameCount = (self.frameCount + 1) % self.frameLength
        margin = 32 # Screen start to move when player hit the margin

        # Player's walking animation, move the screen when player goes to the
        # the edge of the screen
        self.row, self.col = self.getRowandCol(screen, self.positionX,
                                               self.positionY)
        if not self.isSelected:
            self.searchEnemy(screen, self.targetX, self.targetY)
        else:
            if(self.IsWalkUp):
                newPos = self.positionY + self.speed
                (row, col) = self.getRowandCol(screen, self.positionX, newPos)
                if(self.isLegalMove(row, col)):
                    if (newPos > screen.currentY +
                        screen.screenHeight - margin):
                        if (screen.currentY - screen.screenHeight
                            > -parameter[1]):
                            screen.currentY -= screen.screenMoveSpeed
                            self.positionY -= screen.screenMoveSpeed
                    else:
                        self.positionY = newPos
                self.frameImg = self.WalkUpAni[self.frameCount]
            elif(self.IsWalkDown):
                newPos = self.positionY - self.speed
                (row, col) = self.getRowandCol(screen, self.positionX, newPos)
                if(self.isLegalMove(row, col)):
                    if(newPos < screen.currentY + margin):
                        if(screen.currentY < 0):
                            screen.currentY += screen.screenMoveSpeed
                            self.positionY += screen.screenMoveSpeed
                    else:
                        self.positionY = newPos
                self.frameImg = self.WalkDownAni[self.frameCount]
            elif(self.IsWalkRight):
                newPos = self.positionX + self.speed
                (row, col) = self.getRowandCol(screen, newPos, self.positionY)
                if(self.isLegalMove(row, col)):
                    if(newPos > screen.currentX + screen.screenWidth -
                       margin):
                        if (screen.currentX - screen.screenWidth >
                            -parameter[0]):
                            screen.currentX -= screen.screenMoveSpeed
                            self.positionX -= screen.screenMoveSpeed
                    else:
                        self.positionX += self.speed
                self.frameImg = self.WalkRightAni[self.frameCount]
            elif(self.IsWalkLeft):
                newPos = self.positionX - self.speed
                (row, col) = self.getRowandCol(screen, newPos, self.positionY)
                if(self.isLegalMove(row, col)):
                    if(newPos < screen.currentX + margin):
                        if(screen.currentX < 0):
                            screen.currentX += screen.screenMoveSpeed
                            self.positionX += screen.screenMoveSpeed
                    else:
                        self.positionX -= self.speed
                self.frameImg = self.WalkLeftAni[self.frameCount]


    def isLegalMove(self, row, col):
        return ((map[row][col] == 0) and (row >= 0 and row < 42 ) and
                (col >= 0 and col < 42))

    def keyPressed(self, type, key):
        if(type == pygame.KEYDOWN):
            if(key == pygame.K_DOWN):
                self.IsWalkUp = True
            elif(key == pygame.K_UP):
                self.IsWalkDown = True
            elif(key == pygame.K_RIGHT):
                self.IsWalkRight = True
            elif(key == pygame.K_LEFT):
                self.IsWalkLeft = True
            elif(key == pygame.K_e):
                self.attack = True
        elif(type == pygame.KEYUP):
            self.resetAni()
            self.IsWalkUp, self.IsWalkDown, self.IsWalkRight, self.IsWalkLeft\
                = False, False, False, False

    def mousePressed(self, smallScreen, x, y, parameter):
        row, col = self.getRowandCol(smallScreen, self.positionX,
                                     self.positionY)
        if ((x <= self.positionX + self.cellWidth and x >= self.positionX) or
            (y <= self.positionY + 2 * self.cellHeight and x <=
                self.positionY)):
            if self.isSelected:
                self.isSelected = False
            else:
                self.isSelected = True

        else:
            pass



    # Character return to still pose
    def resetAni(self):
        if(self.IsWalkDown):
            self.frameImg = self.WalkDownAni[0]
        elif(self.IsWalkUp):
            self.frameImg = self.WalkUpAni[0]
        elif(self.IsWalkRight):
            self.frameImg = self.WalkRightAni[0]
        elif(self.IsWalkLeft):
            self.frameImg = self.WalkLeftAni[0]

    def redrawAll(self, screen, smallScreen):
        screen.blit(self.frameImg, (self.positionX, self.positionY))
        self.drawSelectedArea(screen, smallScreen)
        self.drawHealthBar(screen, smallScreen)

    def drawHealthBar(self, screen, smallScreen):
        width = 30
        height = 2
        offsetY = 10
        if (self.healthPercent <= 0.5):
            color = (255, 0, 0)
        else:
            color = (0, 255, 0)
        heal = int(self.healthPercent * width)
        healLength = heal * width

        PosX = self.positionX
        PosY = self.positionY

        start_p = (PosX, PosY - offsetY)
        end_p_one = (PosX + width, PosY - offsetY)
        end_p_two = (PosX + width, PosY - offsetY + height)
        end_p_thr = (PosX, PosY - offsetY + height)
        pygame.draw.line(screen, color, start_p, end_p_one)
        pygame.draw.line(screen, color, end_p_one, end_p_two)
        pygame.draw.line(screen, color, end_p_two, end_p_thr)
        pygame.draw.line(screen, color, end_p_thr, start_p)
        pygame.draw.rect(screen, color, ((start_p, (heal, height))))

    def drawSelectedArea(self, screen, smallScreen):
        color = (0, 255, 0)
        PosX = self.positionX
        PosY = self.positionY
        start_p = (PosX, PosY)
        end_p_one = (PosX + self.cellWidth, PosY)
        end_p_two = (PosX + self.cellWidth, PosY + 2 * self.cellHeight)
        end_p_thr = (PosX, PosY + 2 * self.cellHeight)
        pygame.draw.line(screen, color, start_p, end_p_one)
        pygame.draw.line(screen, color, end_p_one, end_p_two)
        pygame.draw.line(screen, color, end_p_two, end_p_thr)
        pygame.draw.line(screen, color, end_p_thr, start_p)

######################################################
# Building that can be built in the game
######################################################

class Building(object):
    def __init__(self, path="", row=1, col=1, health=10**10, cost=100,
                 offsetX=0, offsetY=0):
        self.imageRow = row
        self.imageCol = col
        self.cellWidth = 16
        self.cellHeight = 16
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.imageX = 0
        self.imageY = 0
        self.subPath = path
        self.health = health
        self.fullHealth = health
        self.isOccupy = False
        self.isSelected = False
        self.isBeingAttack = False
        self.cost = cost
        self.image = []
        self.initImg()

    def initImg(self):
        initImgFromPath(self.subPath, self.image)

class House(Building):
    def __init__(self):
        super().__init__("building/house", 5, 5, 1000, 50)
        self.residents = 5
        offset = 32

class Tower(Building):
    def __init__(self):
        super().__init__("building/tower", 3, 3, 2000, 100, 0, 5)

class Farm(Building):
    def __init__(self):
        super().__init__("building/farm", 4, 8, 1000)
        self.foodOffer = 4

class Market(Building):
    def __init__(self):
        self.moneyOffer = 50
        super().__init__("building/market", 6, 5, 1000)

##################################################
# Screen
##################################################

class Screen(object):
    def __init__(self):
        self.currentX =0
        self.currentY = 0
        self.screenWidth = 16 * 32
        self.screenHeight = 16 * 32
        self.screenMoveSpeed = 1

###################################################
# Terrain
# The map of game
###################################################

class Terrain(GameObject):
    def __init__(self):
        super().__init__()
        self.mapImg = []
        self.subPath = "map"
        self.initMap()
        self.rows = 60
        self.cols = 60
        self.cellWidth = 16
        self.cellHeight = 16
        self.select = False
        self.selectedRow = -1
        self.selectedCol = -1
        self.selectedAbsRow = -1
        self.selectedAbsCol = - 1
        self.isLegalToBuild = True
        self.isLegalColor = (0, 255, 0)
        self.notLegalColor = (255, 0, 0)
        self.currentColor = self.isLegalColor
        self.buildingOnMap = []
        self.currentBuilding = Building()
    def initMap(self):
        initImgFromPath(self.subPath, self.mapImg)

    # Get the row and col that are relative to the whole map
    def getAbsRowandCol(self, smallScreen, x, y):
        dx = abs(smallScreen.currentX) + x
        dy = abs(smallScreen.currentY) + y
        (row, col) = (dy // self.cellHeight, dx // self.cellWidth)
        return (row, col)

    # Get the row and col that are relative to the main screen
    def getRowandCol(self, x, y):
        return (y // self.cellHeight, x // self.cellWidth)

    # Test if the area is legal to walk through or for construction
    def isLegalArea(self, rows, cols, width, height):
        for row in range(rows, rows + width + 1):
            for col in range(cols, cols + height + 1):
                if(row >= rowOfMap or col >= colOfMap or map[row][col] != 0):
                    return False
        return True

    # Block the corresponding area on map so that character cannot pass
    # the building
    def updateMap(self, smallScreen, building, isRemove):
        x = building.imageX
        y = building.imageY
        rows, cols = self.getAbsRowandCol(smallScreen, x, y)
        rows += building.offsetY
        cols += building.offsetX
        for row in range(rows, rows + building.imageRow):
            for col in range(cols, cols + building.imageCol):
                if(isRemove):
                    map[row][col] = 0
                else:
                    map[row][col] = 1

    def keyPressed(self, type, key, smallScreen):
        if(type == pygame.KEYDOWN):
            if(key == pygame.K_c):
                if self.select == True:
                    self.select = False
                else:
                    self.select = True
            if(key == pygame.K_h):
                self.currentBuilding = House()

            elif(key == pygame.K_c):
                self.currentBuilding = Tower()

            elif(key == pygame.K_m):
                self.currentBuilding = Market()

            elif(key == pygame.K_f):
                self.currentBuilding = Farm()

            elif(key == pygame.K_d):
                self.removeBuilding(smallScreen)

    def removeBuilding(self, smallScreen):
        for building in self.buildingOnMap:
            if building.isSelected:
                self.updateMap(smallScreen, building, True)
                if(isinstance(building, House)):
                    self.population -= building.residents
                elif(isinstance(building, Farm)):
                    self.food -= building.foodOffer
                self.buildingOnMap.remove(building)

    def build(self, building, x, y, smallScreen):
        building.imageX = x
        building.imageY = y
        if (isinstance(building, House)):
            self.population += self.currentBuilding.residents
        elif(isinstance(building, Farm)):
            self.food += self.currentBuilding.foodOffer
        self.buildingOnMap.append(building)
        # Update the map so that building cannot be passed
        self.updateMap(smallScreen, building, False)

    def mousePressed(self, x, y, smallScreen):
        if self.select:
            # If it's the area is leagal
            if self.isLegalToBuild:
                self.build(self.currentBuilding, x, y, smallScreen)
                # Set default current building
                self.money -= self.currentBuilding.cost
                self.currentBuilding = House()
                self.select = False
        else:
            # Select building
            for building in self.buildingOnMap:
                if(x >= building.imageX and
                   x <= building.imageX + building.imageCol * self.cellWidth
                   and y >= building.imageY and
                   y <= building.imageY + building.imageRow * self.cellWidth):

                    if building.isSelected == True:
                        building.isSelected = False
                    else:
                        # If it's been selected, cancel the selection
                        building.isSelected = True

                    # Cancel other building's selection
                    for others in self.buildingOnMap:
                        if others.isSelected and others != building:
                            others.isSelected = False

    def mouseMotion(self, smallScreen, x, y):
        if self.select == True:
            self.selectedRow, self.selectedCol = self.getRowandCol(x, y)
            self.selectedAbsRow, self.selectedAbsCol = self.getAbsRowandCol(
                                                            smallScreen, x, y)
        # Update the color of selection area and parameter
        if (self.isLegalArea(self.selectedAbsRow, self.selectedAbsCol,
                             self.currentBuilding.imageRow,
                             self.currentBuilding.imageCol)):
            self.isLegalToBuild = True
            self.currentColor = self.isLegalColor

        else:
            self.isLegalToBuild = False
            self.currentColor = self.notLegalColor

    def redrawAll(self, screen):

        self.drawBuilding(screen)

        self.drawSelectedArea(screen)
        self.drawInfoBar(screen)

        if self.select:
            self.drawBuildingArea(screen)


    def drawBuilding(self, screen):
        if (len(self.buildingOnMap) != 0):
            for building in self.buildingOnMap:
                screen.blit(building.image[0],
                            (building.imageX, building.imageY))

    def drawBuildingArea(self, screen):
        selectedWidth = self.cellWidth * self.currentBuilding.imageCol
        selectedHeight = self.cellHeight * self.currentBuilding.imageRow

        x = (self.selectedCol + self.currentBuilding.offsetX )* self.cellWidth
        y = (self.selectedRow + self.currentBuilding.offsetY) * self.cellHeight
        pygame.draw.rect(screen, self.currentColor, ((x, y), (selectedWidth,
                                                              selectedHeight)))

    # Draw the selection area of building
    def drawSelectedArea(self, screen):
        for building in self.buildingOnMap:
            if building.isSelected:
                color = self.isLegalColor
                w = building.imageCol * self.cellWidth
                h = building.imageRow * self.cellHeight
                offsetX = self.cellWidth * building.offsetX
                offsetY = self.cellHeight * building.offsetY
                start_p = (building.imageX + offsetX,
                           building.imageY + offsetY)
                end_p_one = (building.imageX + offsetX + w,
                             building.imageY + offsetY)
                end_p_two = (building.imageX + offsetX + w,
                             building.imageY + offsetY + h)
                end_p_thr = (building.imageX + offsetX,
                             building.imageY + offsetY + h)
                pygame.draw.line(screen, color, start_p, end_p_one, 2)
                pygame.draw.line(screen, color, end_p_one, end_p_two, 2)
                pygame.draw.line(screen, color, end_p_two, end_p_thr, 2)
                pygame.draw.line(screen, color, end_p_thr, start_p, 2)

    # Draw the health bar of building on top of the building
    def drawInfoBar(self, screen):
        for building in self.buildingOnMap:
            if building.isSelected:
                color = (0, 255, 0)
                width = 50
                height = 2
                offsetY = 15
                percent = building.health / building.fullHealth
                if(percent <= 0.5):
                    color = (255, 0, 0)
                else:
                    color = (0, 255, 0)
                heal = int(percent * width)
                healLength = heal * width

                start_p = (building.imageX, building.imageY - offsetY)
                end_p_one = (building.imageX + width, building.imageY - offsetY)
                end_p_two = (building.imageX + width, building.imageY -
                             offsetY + height)
                end_p_thr = (building.imageX, building.imageY - offsetY +
                             height)
                pygame.draw.line(screen, color, start_p, end_p_one)
                pygame.draw.line(screen, color, end_p_one, end_p_two)
                pygame.draw.line(screen, color, end_p_two, end_p_thr)
                pygame.draw.line(screen, color, end_p_thr, start_p)
                pygame.draw.rect(screen, color, ((start_p, (heal, height))))

    def update(self, dx, dy):
        for building in self.buildingOnMap:
            building.imageX += dx
            building.imageY += dy

################################################
# Information bar shown on top of the game
################################################

class infoBar(object):
    def __init__(self, title, data, x, y):
        self.barLength = 16 * 8
        self.barWidth = 16 * 4
        self.title = title
        self.data = data
        self.subPath = "menu/top"
        self.backImg = []
        self.initImage()
        self.barX = x
        self.barY = y
        self.textOffSetX = 10
        self.textOffSetY = 10

    def initImage(self):
        initImgFromPath(self.subPath, self.backImg)

    def drawBar(self, screen):
        screen.blit(self.backImg[0], ((self.barX, self.barY), (self.barLength,
                                                             self.barWidth)))
        info = pygame.font.SysFont("monospace", 15)
        label = info.render(self.title  + ":" + str(self.data), 1, (0, 0, 0))
        screen.blit(label, (self.barX + self.textOffSetX, self.barY +
                            self.textOffSetY))

    def update(self, newData):
        self.data = newData

##################################################
# Information bar shown on the bottom of the game
##################################################

class bottomBar(object):
    def __init__(self):
        self.barLength = 16 * 32
        self.barWidth = 16 * 4
        self.data = 0
        self.subPath = "menu/bottom"
        self.backImg = []
        self.initImage()
        self.barX = 0
        self.barY = 16 * 32 - self.barWidth
        self.houseButtonAreaX = 20
        self.marketButtonAreaX = 90
        self.farmButtonAreaX = 170
        self.castleButtonAreaX = 230
        self.buildingTypeOffset = 10
        self.costOffset = 20

    def initImage(self):
        initImgFromPath(self.subPath, self.backImg)

    def mousePressed(self, x, y):
        if(y >= self.barY and y <= self.barY + self.barWidth):
            if(x >= self.houseButtonAreaX and x <= self.marketButtonAreaX):
                return "House"
            elif(x >= self.marketButtonAreaX and x <= self.farmButtonAreaX):
                return "Market"
            elif(x >= self.farmButtonAreaX and x <= self.castleButtonAreaX):
                return "Farm"

    def drawBottomBar(self, screen):
        # Draw the scroll
        screen.blit(self.backImg[0], ((self.barX, self.barY),
                                      (self.barLength, self.barWidth)))
        # Draw the button of different building
        self.drawFont(screen, "House", self.houseButtonAreaX, self.barY +
                      self.buildingTypeOffset,15)
        self.drawFont(screen, "100$", self.houseButtonAreaX, self.barY +
                      self.buildingTypeOffset + self.costOffset, 12)
        self.drawFont(screen, "Market", self.marketButtonAreaX, self.barY +
                      self.buildingTypeOffset, 15)
        self.drawFont(screen, "100$", self.marketButtonAreaX, self.barY +
                      self.buildingTypeOffset + self.costOffset, 12)
        self.drawFont(screen, "Farm", self.farmButtonAreaX, self.barY +
                      self.buildingTypeOffset, 15)
        self.drawFont(screen, "100$", self.farmButtonAreaX, self.barY +
                      self.buildingTypeOffset + self.costOffset, 12)

    def drawFont(self, screen, title, x, y, size):
        info = pygame.font.SysFont("monospace", size)
        label = info.render((title), 1, (0, 0, 0))
        screen.blit(label, (x, y))
















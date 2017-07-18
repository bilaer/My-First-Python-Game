import pygame
import random
import os
import math
from gameclass import Character
from gameclass import House
from gameclass import Farm
from gameclass import Market
from gameclass import Tower
from gameclass import Player
from gameclass import Monster
from gameclass import Terrain
from gameclass import Screen
from gameclass import infoBar
from gameclass import bottomBar
from gameclass import Building
from gameclass import Market
from gameclass import Farm
from mainGame import GameObject
from mapBoard import map




##############################
# Game play class
##############################
class Game(GameObject):

    def __init__(self, width=720, height=720, fps=30):
        super().__init__()
        self.player = [Player()]
        self.smallScreen = Screen()
        self.foodInfo = infoBar("food", self.food, 0, 0)
        self.populationInfo = infoBar("population", self.population, 16*12, 0)
        self.moneyInfo = infoBar("money", self.money, 16*24, 0)
        self.bottomBar = bottomBar()
        self.oldScreenX = self.smallScreen.currentX
        self.oldScreenY = self.smallScreen.currentY
        self.width = width
        self.height = height
        self.moveUp = False
        self.moveDown = False
        self.moveLeft = False
        self.moveRight = False
        self.row = 45
        self.col = 45
        self.title = "test"
        self.monsterAttackNum = 5
        self.initMoney = 1000
        self.monsterAttackIncrease = 3
        self.timeCount = 0
        self.foodStartTime = 0
        self.moneyStartTime = 0
        self.monsterAttackTime = 20
        self.monsterAttackCount = 50
        self.foodIncreaseTime = 10
        self.foodIncreaseCount = 10
        self.foodIncreaseNum = 0
        self.moneyEarn = 0
        self.moneyIncreaseTime = 5
        self.moneyIncreaseCount = 5
        self.moneyIncreaseNum = 0
        self.peopleConTime = 1
        self.peopleConCount = 1
        self.popCon = 0
        self.menu = True
        self.instruction = False
        self.gameStart = True
        self.isShowFoodWarning = False
        self.monster = []
        self.numOfFarm = 0
        self.numOfMarket = 0
        self.playerAttack = 0.5
        self.monsterAttack = 0.5
        self.die = False
        # effect
        self.map = Terrain()
        self.oldPop = self.map.population
        self.fps = fps
        self.fillColor = (255, 255, 255)
        self.playing = False
        self.wave = 0
        self.timeTemp = self.timeCount

    def initMonster(self, num):
        monsterNum = num
        count = 0
        while count < monsterNum:
            if(self.smallScreen.currentX <= -self.cellWidth):
                posX = random.randint(self.smallScreen.currentX, 0)
            elif(self.width + self.smallScreen.currentX -
                self.smallScreen.screenWidth >= 16):
                    posX = random.randint((self.smallScreen.currentX +
                                          self.smallScreen.screenWidth),
                                          (self.width +
                                           self.smallScreen.currentX))
            else:
                posX = random.randint(self.smallScreen.currentX, 0)
            if(self.smallScreen.currentY <= -self.cellHeight):
                posY = random.randint(self.smallScreen.currentY, 0)
            elif(self.height + self.smallScreen.currentY -
                    self.smallScreen.screenWidth >= 16):
                posY = random.randint((self.smallScreen.currentY +
                                          self.smallScreen.screenHeight),
                                          (self.width +
                                          self.smallScreen.currentY))
            else:
                posY = random.randint(self.smallScreen.currentY, 0)
            row, col = self.getRowandCol(self.smallScreen, posX, posY)
            if(row >= self.row or row < 0 or col >= self.col or col <
                map[row][col] == 1):
                break
            else:
                # Generate even monster location so that image
                # will not shaking
                if(posX % 4 == 0 and posY % 4 == 0):
                    self.monster.append(Monster(posX, posY))
                    count += 1

    def timerFired(self):
        if self.menu:
            return
        elif self.instruction:
            return
        elif self.die:
            return
        elif len(self.player) == 0 or len(self.map.buildingOnMap) == 0 and \
                not self.gameStart:
            self.die = True
        elif len(self.map.buildingOnMap) != 0:
            self.gameStart = False
        # Here need to change
        # Update time resource
        self.updateTime()
        self.updateBuildingNum()
        self.updateScreen()
        for player in self.player:
            player.update(self.smallScreen, (self.width, self.height))
            # Update the percentage of health to player
            player.healthPercent = player.health / player.fullHealth
        dx = (self.smallScreen.currentX - self.oldScreenX)
        dy = (self.smallScreen.currentY - self.oldScreenY)

        if(dx != 0 or dy != 0):
            # Update the location of monster:
            for mon in self.monster:
                mon.positionX += dx
                mon.positionY += dy
            # Store the screen info into the data
            self.oldScreenX = self.smallScreen.currentX
            self.oldScreenY = self.smallScreen.currentY

        # Assign the target for the player when player generated
        delta = self.map.population - self.oldPop
        if delta != 0:
            index = 0
            for i in range(0, delta):
                for j in range(index, len(self.map.buildingOnMap)):
                    if isinstance(self.map.buildingOnMap[j], House):
                        index = j
                        # Calculate the place for the birth spot
                        buildingX = self.map.buildingOnMap[j].imageX
                        buildingY = self.map.buildingOnMap[j].imageY
                        width = self.map.buildingOnMap[j].cellWidth
                        height = self.map.buildingOnMap[j].cellHeight
                        row = self.map.buildingOnMap[j].imageRow
                        col = self.map.buildingOnMap[j].imageCol
                        x = buildingX + (col * width) // 2
                        y = buildingY + row * height
                        add = Player(x, y)
                        if len(self.monster) != 0:
                            ran = random.randint(0, len(self.monster) - 1)
                            add.hasTarget = False
                            add.target.append(self.monster[ran])
                        self.player.append(add)
            self.oldPop = self.map.population


        # Assign the target to the monsters
        if len(self.map.buildingOnMap) == 0:
            for mon in self.monster:
                #mon.hasTarget = True
                #mon.target = self.player
                if mon.hasTarget == False:
                    if len(self.map.buildingOnMap) != 0:
                        ran = random.randint(0, len(self.map.buildingOnMap) - 1)
                        mon.hasTarget = True
                        mon.target = self.map.buildingOnMap[ran]
                    else:
                        if len(self.player) == 0:
                            ran = random.randint(0, len(self.player))
                            mon.hasTaregt = True
                            mon.target = self.player[ran]
        else:
            for mon in self.monster:

                if mon.hasTarget == False:
                    ran = random.randint(0, len(self.map.buildingOnMap) - 1)
                    x = self.map.buildingOnMap[ran].imageX
                    y = self.map.buildingOnMap[ran].imageY
                    width = self.map.buildingOnMap[ran].cellWidth
                    height = self.map.buildingOnMap[ran].cellHeight
                    row = self.map.buildingOnMap[ran].imageRow
                    col = self.map.buildingOnMap[ran].imageCol
                    offSet = [(0, 0), (0, height*row),
                              (width*col, 0), (width*col, height*row)]

                    ranPoint = random.randint(0, len(offSet) - 1)
                    mon.hasTarget = True
                    mon.target = self.map.buildingOnMap[ran]
                    mon.offsetX, mon.offsetY = offSet[ranPoint]

        is_break = False
        for player in self.player:
            for monster in self.monster:
                x = player.positionX
                y = player.positionY
                if ((x <= monster.positionX + monster.attackRange and
                     x >= monster.positionX - monster.attackRange) and
                    (y <= monster.positionY + monster.attackRange and
                     y >= monster.positionY - monster.attackRange)):
                    player.health -= self.monsterAttack
                    if player.health <= 0:
                        self.player.remove(player)
                        self.population -= 1
                        break
                        is_break = True
            if is_break:
                break


        # Being Starved
        if self.food == 0:
            for player in self.player:
                player.health -= 0.05
                if player.health <= 0:
                    self.player.remove(player)

        # Update the info of resource players have
        self.updateResource()
        # Update the display of information
        self.foodInfo.update(self.food)
        self.populationInfo.update(self.population)
        self.moneyInfo.update(self.money)

        # Player being attacked by monster

        # Update the monter position
        if len(self.monster) != 0:
            for monster in self.monster:
                #print("monster location: %d %d", monster.positionX,
                #       monster.positionY)
                monster.update(self.smallScreen)


        # Test if building is under attack
        is_break = False
        for mon in self.monster:
            if isinstance(mon.target, Building):
                for building in self.map.buildingOnMap:
                    x = mon.positionX - mon.offsetX
                    y = mon.positionY - mon.offsetY
                    if((x <= building.imageX + mon.attackRange and
                        x >= building.imageX - mon.attackRange) and
                        (y <= building.imageY + mon.attackRange and
                        y >= building.imageY - mon.attackRange)):
                        building.health -= self.monsterAttack
                        if building.health == 0:
                            self.map.buildingOnMap.remove(building)
                            self.map.updateMap(self.smallScreen, building, True)
                            # Here add test if there are building in map
                            self.assignTarget(mon, building)
                            # If other monsters are attacking the same house,
                            # change the target
                            for others in self.monster:
                                if(isinstance(others.target, Building) and(x <=
                                   building.imageX + mon.attackRange and
                                   x >= building.imageX - mon.attackRange) and
                                   (y <= building.imageY + mon.attackRange and
                                   y >= building.imageY - mon.attackRange)):
                                    self.assignTarget(others, building)
                if is_break:
                    break

        # Assign the target for the player'army
        if len(self.monster) != 0:
            for player in self.player:
                if not player.hasTarget:
                    if len(self.monster) != 0:
                        ran = random.randint(0, len(self.monster) - 1)
                        player.hasTarget = True
                        player.target.append(self.monster[ran])
                else:
                    for mon in self.monster:
                        x = player.positionX
                        y = player.positionY
                        if ((mon == player.target[0]) and
                            (x >= mon.positionX - player.attackRange and
                             x <= mon.positionX + player.attackRange) and
                            ((y >= mon.positionY - player.attackRange and
                             y <= mon.positionY + player.attackRange))):
                            mon.health -= self.playerAttack # Under
                            mon.healthPercent = mon.health / mon.fullHealth
                            if mon.health == 0:
                                self.monster.remove(mon)
                                temp = player.target.pop()
                                player.hasTarget = False
                                if len(self.monster) != 0:
                                    self.assignTargetForPlayer(player)
                                for others in self.player:
                                    if others.hasTarget and others.target[0] \
                                            == temp:
                                        others.target.pop()
                                        others.hasTarget = False
                                        if len(self.monster) != 0:
                                            self.assignTargetForPlayer(others)
                                if len(self.monster) == 0:
                                    break

    def updateBuildingNum(self):
        market = 0
        farm = 0
        foodIncreaseNum = 0
        moneyIncreaseNum = 0
        popCon = 0
        for building in self.map.buildingOnMap:
            if isinstance(building, Market):
                market += 1
                moneyIncreaseNum += building.moneyOffer
            elif isinstance(building, Farm):
                farm += 1
                foodIncreaseNum += building.foodOffer

            elif isinstance(building, House):
                popCon += 1
        self.numOfFarm = farm
        self.numOfMarket = market
        self.foodIncreaseNum = foodIncreaseNum
        self.moneyIncreaseNum = moneyIncreaseNum
        self.popCon = popCon

    def updateTime(self):
        time = round(pygame.time.get_ticks() / 1000)
        if time != self.timeCount:
            temp = self.monsterAttackCount - 1
            if temp < 0:
                self.monsterAttackCount = self.monsterAttackTime
                self.initMonster(self.monsterAttackNum)
                self.monsterAttackNum += self.monsterAttackIncrease
                self.wave += 1
            else:
                self.monsterAttackCount = temp

            if self.numOfFarm != 0:
                farmTemp = self.foodIncreaseTime - 1
                if farmTemp < 0:
                    printemp = self.food + self.foodIncreaseNum
                    self.food = printemp
                    self.foodIncreaseTime = self.foodIncreaseCount
                else:
                    self.foodIncreaseTime = farmTemp
            if self.numOfMarket != 0:
                marketTemp = self.moneyIncreaseTime - 1
                print(marketTemp)
                if marketTemp < 0:
                    self.moneyEarn += self.moneyIncreaseNum
                    self.moneyIncreaseTime = self.moneyIncreaseCount
                else:
                    self.moneyIncreaseTime = marketTemp
            popTime = self.peopleConCount - 1
            if popTime < 0:
                if self.food != 0:
                    printemp = self.food - self.popCon
                    if printemp >= 0:
                        self.food = printemp
                self.peopleConCount = self.peopleConTime
            else:
                self.peopleConCount = popTime
            self.timeCount = time


    def assignTargetForPlayer(self, player):
        ran = random.randint(0, len(self.monster) - 1)
        player.target.append(self.monster[ran])
        player.hasTarget = True

    def assignTarget(self, monster, building):
        if len(self.map.buildingOnMap) != 0:
            is_True = True
            while is_True:
                ran = random.randint(0, len(self.map.buildingOnMap) - 1)
                if self.map.buildingOnMap[ran] != building:
                    monster.hasTarget = True
                    monster.target = self.map.buildingOnMap[ran]
                    is_True = False


    def getRowandCol(self, smallScreen, x, y):
        dx = 2 * abs(smallScreen.currentX) + x
        dy = 2 * abs(smallScreen.currentY) + y
        (row, col) = (dy // self.cellHeight, dx // self.cellWidth)
        return (row, col)

    # Update the current resource
    def updateResource(self):
        total = self.initMoney
        for building in self.map.buildingOnMap:
            total -= building.cost
        self.money = total + self.moneyEarn
        self.population = self.map.population


    def keyPressed(self, type, key=-1):
        if self.menu:
            return
        elif self.instruction:
            return
        elif self.die:
            return
        for player in self.player:
            player.keyPressed(type, key)
        self.map.keyPressed(type, key, self.smallScreen)
        if type == pygame.KEYDOWN:
            if key == pygame.K_w:
                self.moveUp = True
                self.moveDown, self.moveRight, self.moveLeft = False, False, \
                                                               False
            elif key == pygame.K_a:
                self.moveLeft = True
                self.moveDown, self.moveRight, self.moveUp = False, False, False
            elif key == pygame.K_d:
                self.moveRight = True
                self.moveDown, self.moveUp, self.moveLeft = False, False, False
            elif key == pygame.K_s:
                self.moveDown = True
                self.moveRight, self.moveLeft, self.moveUp = False, False, False
        elif type == pygame.KEYUP:
            self.moveUp, self.moveDown, self.moveLeft, self.moveRight = \
                False, False, False, False

    def updateScreen(self):
        boundaryX = 16 * 30
        boundaryy = 16 * 30
        if self.moveDown:
            test = self.smallScreen.currentY - self.smallScreen.screenMoveSpeed
            if test >= - boundaryy:
                self.smallScreen.currentY = test
                for player in self.player:
                    player.positionY -= self.smallScreen.screenMoveSpeed
                for building in self.map.buildingOnMap:
                    building.imageY -= self.smallScreen.screenMoveSpeed
                for monster in self.monster:
                    monster.positionY -= self.smallScreen.screenMoveSpeed
        elif self.moveUp:
            test = self.smallScreen.currentY + self.smallScreen.screenMoveSpeed
            if test <= 0:
                self.smallScreen.currentY = test
                for player in self.player:
                    player.positionY += self.smallScreen.screenMoveSpeed
                for building in self.map.buildingOnMap:
                    building.imageY += self.smallScreen.screenMoveSpeed
                for monster in self.monster:
                    monster.positionY += self.smallScreen.screenMoveSpeed
        elif self.moveRight:
            test = self.smallScreen.currentX - self.smallScreen.screenMoveSpeed
            if test >= - boundaryX:
                self.smallScreen.currentX = test
                for player in self.player:
                    player.positionX -= self.smallScreen.screenMoveSpeed
                for building in self.map.buildingOnMap:
                    building.imageX -= self.smallScreen.screenMoveSpeed
                for monster in self.monster:
                    monster.positionX -= self.smallScreen.screenMoveSpeed
        elif self.moveLeft:
            test = self.smallScreen.currentX + self.smallScreen.screenMoveSpeed
            if test <= 0:
                for player in self.player:
                    player.positionX += self.smallScreen.screenMoveSpeed
                for building in self.map.buildingOnMap:
                    building.imageX += self.smallScreen.screenMoveSpeed
                for monster in self.monster:
                    monster.positionX += self.smallScreen.screenMoveSpeed
                self.smallScreen.currentX = test

    def mouseReleased(self, x, y):
        pass

    def mousePressed(self, x, y):
        if self.menu:
            startX = 198
            startY = 310
            startWidth = 120
            startHeight = 40
            infoX = 198
            infoY = 380
            InfoWidth = 120
            InfoHeight = 40
            quitX = 198
            quitY = 450
            QuitWidth = 120
            QuitHeight = 40
            if ((x >= startX and x <= startX + startWidth) and
                (y >= startY and y <= startY + startHeight)):
                self.menu = False
            elif ((x >= infoX and x <= infoX + InfoWidth) and
                  (y >= infoY and y <= infoY + InfoHeight)):
                self.menu = False
                self.instruction = True
            elif ((x >= quitX and x <= quitX + QuitWidth) and
                  (y >= quitY and y <= quitY + QuitHeight)):
                pygame.quit()

            return
        elif self.instruction:
            backX = 20
            backY = 450
            backWidth = 120
            backHeight = 40
            if ((x >= backX and x <= backX + backWidth) and
                (y >= backY and y <= backY + backHeight)):
                self.instruction = False
                self.menu = True
        elif self.die:
            if ((x >= 0 and x <= 16 * 32) and
               (y >= 0 and y <= 16 * 32)):
                self.die = False
                self.menu = True
                self.__init__()

        self.map.mousePressed(x, y, self.smallScreen)
        for player in self.player:
            player.mousePressed(self.smallScreen, x, y, (self.width,
                                                         self.height))
            for others in self.player:
                if others != player:
                    player.isSelected = False
        result = self.bottomBar.mousePressed(x, y)
        if(result != None):
            self.map.select = True
            if(result == "House"):
                self.map.currentBuilding = House()
            elif(result == "Farm"):
                self.map.currentBuilding = Farm()
            elif(result == "Castle"):
                self.map.currentBuilding = Tower()
            elif(result == "Market"):
                self.map.currentBuilding = Market()


    def mouseMotion(self, x, y):
        self.map.mouseMotion(self.smallScreen, x, y)

    def mouseDrag(self, x, y):
        pass

    def warning(self, screen):
        if self.isShowFoodWarning:
            title = "You don't have enough food!"
            info = pygame.font.SysFont("helvetica", 50, True)
            label = info.render(title, 8, (0, 0, 250))
            screen.blit(label, (0, 0))

    def Info(self, screen):
        path = "menu/main"
        img = []
        back = []
        absPath = os.path.join(os.path.dirname(__file__), path)
        for image in os.listdir(absPath):
            img.append(absPath + "/" + image)
        for path in img:
            if ("jpg" in path):
                back.append(pygame.image.load(path))
        screen.blit(back[0], (0, 0))
        quitX = 20
        quitY = 450
        titleInfo = pygame.font.SysFont("helvetica", 30, True)
        titleOne = "W, A, S, D move the screen"
        titleTwo = "Select the building at bottom"
        titleThree = "Build house to get army"
        titleFour = "Build farm to get food"
        titleFive = "Build market to earn money"
        labelOne = titleInfo.render(("go back to menu"), 8, (0, 0, 250))
        labelTwo = titleInfo.render((titleTwo), 8, (0, 0, 250))
        labelThree = titleInfo.render((titleThree), 8, (0, 0, 250))
        labelFour = titleInfo.render((titleFour), 8, (0, 0, 250))
        labelFive = titleInfo.render((titleFive), 8, (0, 0, 250))

        screen.blit(labelOne, (quitX, quitY))
        screen.blit(labelTwo, (20, 20))
        screen.blit(labelTwo, (20, 50))
        screen.blit(labelThree, (20, 100))
        screen.blit(labelFour, (20, 150))
        screen.blit(labelFive, (20, 200))



    def mainMenu(self, screen):
        path = "menu/main"
        img = []
        back = []
        absPath = os.path.join(os.path.dirname(__file__), path)
        for image in os.listdir(absPath):
            img.append(absPath + "/" + image)
        for path in img:
            if ("jpg" in path):
                back.append(pygame.image.load(path))
        screen.blit(back[0], (0, 0))
        startX = 220
        startY = 305
        infoX = 205
        infoY = 378
        quitX = 225
        quitY = 442
        titleX = 110
        titleY = 180
        title = "A Cool Game"
        titleInfo = pygame.font.SysFont("helvetica", 60, True)
        info = pygame.font.SysFont("helvetica",40, True)
        labelOne = info.render(("start"), 8, (0, 0, 0))
        infoTwo = pygame.font.SysFont("helvetica", 40, True)
        labelTwo = infoTwo.render(("tutorial"), 8, (0, 0, 0))
        labelThree = infoTwo.render(("quit"), 8, (0, 0, 0))
        titles = titleInfo.render((title), 8, (150, 0, 150))
        screen.blit(titles, (titleX, titleY))
        pygame.draw.rect(screen, (255, 0, 0), ((198, 310), (120, 40)))
        screen.blit(labelOne, (startX, startY))
        pygame.draw.rect(screen, (255, 0, 0), ((198, 380), (120, 40)))
        screen.blit(labelTwo, (infoX, infoY))
        pygame.draw.rect(screen, (255, 0, 0), ((198, 450), (120, 40)))
        screen.blit(labelThree, (quitX, quitY))

    def Die(self, screen):
        titleOneX = 160
        titleOneY = 20
        titleTwoX = 60
        titleTwoY = 150
        titleThrX = 140
        titleThrY = 350
        waveX = 240
        waveY = 250
        info = pygame.font.SysFont("helvetica", 50, True)
        infoTwo = pygame.font.SysFont("helvetica", 40, True)
        infoThree = pygame.font.SysFont("helvetica", 60, True)
        labelOne = info.render(("You lose"), 8, (255, 0, 0))
        labelTwo = infoTwo.render(("You have survived from"), 8, (255, 0, 0))
        labelThree = infoThree.render((str(self.wave)), 8, (255, 0, 0))
        labelFour = infoTwo.render(("waves of attack"), 8, (255, 0, 0))
        screen.fill((0, 0, 0))
        screen.blit(labelOne, (titleOneX, titleOneY))
        screen.blit(labelTwo, (titleTwoX, titleTwoY))
        screen.blit(labelThree, (waveX, waveY))
        screen.blit(labelFour, (titleThrX, titleThrY))


    def drawCountingDown(self, screen):
        x = 320
        y = 460
        fontX = 290
        fontY = 480
        x2 = 435
        y2 = 460
        fontX2 = 390
        fontY2 = 480

        info = pygame.font.SysFont("helvetica", 20)
        word = pygame.font.SysFont("helvetica", 14, True)
        labelone = word.render(("Enemy attack left"), 8, (255, 0, 0))
        labeltwo = info.render((str(self.monsterAttackCount)), 10, (255, 0, 0))
        labelthree = word.render(("Numbers would be.."), 8, (255, 0, 0))
        labelfour = info.render((str(self.monsterAttackNum)), 8, (255, 0, 0))
        screen.blit(labelone, (fontX, fontY))
        screen.blit(labeltwo, (x, y))
        screen.blit(labelthree, (fontX2, fontY2))
        screen.blit(labelfour, (x2, y2))

    def redrawAll(self, screen, parameter):
        self.warning(screen)
        if self.menu:
            self.mainMenu(screen)
            return
        elif self.instruction:
            self.Info(screen)
            return
        elif self.die:
            self.Die(screen)
            return

        for player in self.player:
            player.redrawAll(screen, self.smallScreen)
        for monster in self.monster:
            monster.redrawAll(screen, self.smallScreen)

        # Draw map
        self.map.redrawAll(screen)

        # Draw the information bar on top
        self.foodInfo.drawBar(screen)
        self.populationInfo.drawBar(screen)
        self.moneyInfo.drawBar(screen)
        self.bottomBar.drawBottomBar(screen)
        self.drawCountingDown(screen)

    def run(self):
        pygame.init()
        self.playing = True
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.smallScreen.screenWidth,
                                          self.smallScreen.screenHeight))
        pygame.display.set_caption(self.title)
        while self.playing:
            time = clock.tick(self.fps)
            self.timerFired()
            for event in pygame.event.get():
                if(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    self.mousePressed(*(event.pos))
                elif(event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    self.mouseReleased(*(event.pos))
                elif(event.type == pygame.MOUSEMOTION and event.buttons[0] ==
                    1):
                    self.mouseDrag(*(event.pos))
                elif(event.type == pygame.MOUSEMOTION and event.buttons == (
                        0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                if(event.type == pygame.QUIT):
                    self.playing = False
                elif(event.type == pygame.KEYDOWN):
                    self.keyPressed(event.type, event.key)
                elif(event.type == pygame.KEYUP):
                    self.keyPressed(event.type)


            screen.blit(self.map.mapImg[0], (self.smallScreen.currentX,
                        self.smallScreen.currentY))
            self.redrawAll(screen, (self.width, self.height))
            pygame.display.flip()


def main():
    newGame = Game()
    newGame.run()

if __name__ == '__main__':
    main()





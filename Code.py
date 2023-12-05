from cmu_graphics import *
from PIL import Image
import random

#board
def drawBoard(app):
    cellWidth, cellHeight = getCellSize(app)
    imageWidth, imageHeight = getImageSize(app.gameViewBackground)
    drawImage(app.gameViewBackground, app.width/2 + 120 ,app.height/2-45,
                  align = 'center', width=imageWidth//2.7, height=imageHeight//2.6)
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, 
             fill = 'wheat', border = None, borderWidth = app.cellBorderWidth*2)
    for r in range(app.boardRow):
        for c in range(app.boardCol):
            #top left corner of cell
            x = app.boardLeft + c * cellWidth
            y = app.boardTop + r * cellHeight
            drawRect(x, y, cellWidth, cellHeight, border = 'tan', fill = None,
                     borderWidth = app.cellBorderWidth)
    #drawBorder
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, 
             fill = None, border = 'tan', borderWidth = app.cellBorderWidth*2 )
    pass
 
def getCellSize(app):
    return (app.boardWidth/app.boardCol, app.boardHeight/app.boardRow)

def getCellCenter(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    x = app.boardLeft + cellWidth/2 + col * cellWidth
    y = app.boardTop + cellHeight/2 + row * cellHeight
    return (x, y)

#get row col of a location
def getRowCol(app, x, y):
    cellWidth, cellHeight = getCellSize(app)
    row = (y-app.boardTop)//cellHeight
    col = (x-app.boardLeft)//cellWidth
    return (row, col)

class Wallnut:
    def __init__(self, app, row, col):
        self.x, self.y = getCellCenter(app, row, col)
        self.y = 0
        self.row, self.col = row, col
        self.imageIndex = 0
        self.bitesLeft = 240
        self.opacity = 100
        self.falling = True
        #being eaten animation
        self.beingEaten = False
        self.opacityCount = 5
        self.opac = False 

        self.eaten = False

        

class Guacodile:
    def __init__(self,app, x, y, dir):
        self.x = x 
        self.y = y
        self.dir = dir
        self.row, self.col = getRowCol(app, x, y)
        self.aniIndex = (dir, 0)

    def __repr__(self):
        return f'x:{self.x}, y:{self.y}, direction:{self.dir}, animationIndex:{self.aniIndex}'

class Zombie:
    def __init__(self, app, level, x, y, row, col):
        self.level = level
        self.bitesLeft = 1 if level == 1 else 2
        self.x=x
        self.y=y
        self.row = row
        self.col = col
        self.biteList = []#takes (which gua, row, col)
        self.dead = False
        #jump
        self.jumped = False if level == 3 else True #only level 3 zombie can jump
        self.jumpFinished = True
        self.jumpFrom = None
        self.jumpTo= None
        self.reachedTop = False
        #wallnut
        self.blocked = False
        self.moveFrom = None
        self.moveTo = None
        #animation
        self.imageIndex = 0
        self.walking = True
        self.eating = False
        self.dying = False
        #self.hurt1Walking = False #for level2,level3
        #self.hurt2Walking = False #for level3
        self.walkinglist = None
        #if level == 1:
        #temporary
        if level == 1:
            self.walkingList = app.level1WalkList
            self.dyingList = app.level1DieList
        elif level == 2:
            self.walkingList = app.level2WalkList
            self.hurt1WalkingList = app.level1WalkList
            self.dyingList = app.level1DieList
        else:
            self.walkingList = app.level3WalkList
            self.hurt1WalkingList = app.level3Hurt1WalkList
            self.dyingList = app.level3DieList
        
            
            
        
        


    def __repr__(self):
        return f'Level: {self.level}, bitesLeft = {self.bitesLeft}, location = ({self.x}, {self.y}, rowCol = {self.row}, {self.col})'

    def walk(self, app):
        if not self.blocked:
            self.x -= app.zombieSpeed
            self.col = getRowCol(app, self.x, self.y)[1]
    
    def updateRowCol(self, app):
        self.row, self.col = getRowCol(app, self.x, self.y)

    def smartJump(self, app):
        
        if not self.jumped:
            for d in range(len(app.guaList)):
                if abs(app.guaList[d].row - self.row)<= 1 and abs(app.guaList[d].col - self.col)<= 1:
                    #if gua within 3*3
                    choices = [(-1, -1), (0, -1), (1, -1),(-1, 0), (1, 0),(0, 1),(-1, 1),(1, 1)]
                    #loop through the front cells first
                    for dcol, drow in choices:
                        newRow, newCol = self.row + drow, self.col + dcol
                        if 0 <= newRow < app.boardRow and 0 <= newCol < app.boardCol:
                            #if in range of board
                            guaDcol, guaDrow = app.dirList[app.guaList[0].dir]
                            guaNewRow = app.guaList[0].row + guaDrow
                            guaNewCol = app.guaList[0].col + guaDcol
                            if (app.guaList[0].row != newRow or app.guaList[0].col != 
                                newCol) and(guaNewCol!=newCol or guaNewRow != 
                                            newRow) :
                                #guahead not in that cell and is not the next cell gua enters if stay in current Dir 
                                
                                canJump = True
                                #gua body not in cell
                                for l in range(len(app.guaList)):
                                    if app.guaList[l].row == newRow and app.guaList[l].col == newCol:
                                        canJump = False
                                # wallnut not in the cell
                                for k in range(len(app.wallnutList)):
                                    if app.wallnutList[k].row == newRow and app.wallnutList[k].col == newCol and not app.wallnutList[k].falling and not app.wallnutList[k].eaten:
                                        canJump = False
                                        break
                                if canJump:    
                                    self.jumpFrom = (self.x, self.y)
                                        
                                    self.jumped = True
                                    self.jumpFinished = False
                                    self.jumpTo = (newRow, newCol)

                                    return
        return
    
    def avoidWallnut(self, app):
        for j in range(len(app.wallnutList)):
            if self.row == app.wallnutList[j].row and self.col == app.wallnutList[j].col+1 and not (app.wallnutList[j].falling or app.wallnutList[j].eaten):
            #if wallnut ahead
                choices = [-1, 1] #change row
                for c in choices:
                    newRow, newCol = self.row + c, self.col 
                    if 0 <= newRow < app.boardRow and 0 <= newCol < app.boardCol:
                        #if in range of board
                        for k in range(len(app.guaList)):
                            if (app.guaList[k].row != newRow or app.guaList[k].col != newCol) :
                            #gua not in that cell 
                                for q in range(len(app.wallnutList)):
                                    if not (app.wallnutList[q].row == newRow and app.wallnutList[q].col == newCol) and not (app.wallnutList[q].falling or app.wallnutList[q].eaten):
                                    #wallnut not in that cell
                                        self.moveFrom = (self.x, self.y)
                                        self.moveFinished = False
                                        self.moveTo = (newRow, newCol)
                                        return

                        
        return
    

#zombieJump animation with gravity (self is the zombie object), each jump 1s                  
def jumpToCell(app, self, newRow, newCol):
    targetX, targetY = getCellCenter(app, newRow, newCol)
    highY = min(self.jumpFrom[1], targetY)-15
    #on each step
    #x
    if (self.jumpFrom[0] < targetX and self.x < targetX) or (self.jumpFrom[0] > targetX and self.x > targetX) :
        if self.jumpFrom[0] < targetX:
            if self.x < targetX:
                self.x += abs(targetX - self.jumpFrom[0])/app.stepsPerSecond
        elif self.jumpFrom[0] > targetX:
            if self.x > targetX:
                self.x -= abs(targetX - self.jumpFrom[0])/app.stepsPerSecond
        #y
        if not self.reachedTop and self.y > highY:
            if self.y - abs(highY-self.jumpFrom[1])/ (app.stepsPerSecond/2) > highY:
                self.y -= abs(highY-self.jumpFrom[1])/ (app.stepsPerSecond/2)
            else:
                self.y = highY
        else:
            self.reachedTop = True
        if self.reachedTop and self.y < targetY:
            if self.y + abs(highY-targetY)/ (app.stepsPerSecond/2) < targetY:
                self.y +=abs(highY-targetY)/ (app.stepsPerSecond/2)
            else: 
                self.y = targetY
        self.updateRowCol(app)
    else:
        self.y = targetY
        self.jumpFinished = True
        self.updateRowCol(app)


    #...
    #rewrite self.x, self.y, self.row, self.col
    pass

def moveToCell(app, self, newRow, newCol):
    targetX, targetY = getCellCenter(app, newRow, newCol)
    highY = min(self.moveFrom[1], targetY)-15
    #on each step
    #x
    if (self.moveFrom[0] < targetX and self.x < targetX) or (self.moveFrom[0] > targetX and self.x > targetX) :
        if self.moveFrom[0] < targetX:
            if self.x < targetX:
                self.x += abs(targetX - self.moveFrom[0])/(app.stepsPerSecond/3)
        elif self.moveFrom[0] > targetX:
            if self.x > targetX:
                self.x -= abs(targetX - self.moveFrom[0])/(app.stepsPerSecond/3)
    #y
    if (self.moveFrom[1] < targetY and self.y < targetY) or (self.moveFrom[1] > targetY and self.y > targetY) :
        if self.moveFrom[1] < targetY:
            if self.y < targetY:
                self.y += abs(targetY - self.moveFrom[1])/(app.stepsPerSecond/3)
        elif self.moveFrom[1] > targetY:
            if self.y > targetY:
                self.y -= abs(targetY - self.moveFrom[1])/(app.stepsPerSecond/3)
        self.updateRowCol(app)
    else:
    #     print(self.x, targetX)
    #     print(self.y, targetY)
        self.y = targetY
        self.moveFinished = True
        self.updateRowCol(app)


    #...
    #rewrite self.x, self.y, self.row, self.col
    pass

def onStep(app):
    if app.gameView:
        if not app.isGameOver and not app.isPaused:
            #decides wave or not
            app.timer += 1
            app.waveTimeCount -=1 
            if not app.zombieFinished:
                if app.waveTimeCount ==0 and app.numOfWavesLeft > 0:
                    #draw big wave message

                    zombieWaveGenerator(app)
                    app.waveTimeCount = app.waveInterval
                    app.numOfWavesLeft -= 1
                #generate zombies during normal period
                if app.zombieGenIntervalCount > 0:
                    app.zombieGenIntervalCount -=1
                elif app.zombieGenIntervalCount == 0:
                    zombieGenerator(app)
                    app.zombieGenIntervalCount = app.zombieGenInterval
                    app.zombieGenInterval  = random.randint(180, 350)

            
            #move Guacodile
            if not app.guaHitWallnut:
                moveGuacodileLine(app)
                guaHitWallnut(app)
            else:
                app.guaHitWallnutCounter -=1
                if app.guaHitWallnutCounter <= 0:
                    app.guaHitWallnutCounter = app.guaHitWallnutTime
                    app.guaHitWallnut = False
            updateGuaImage(app)
            guaHitSelf(app)
            guaHitWall(app)
            
            guaCollideZomb(app)
            

            #zombies walk
            for i in range(len(app.zombieList)):
                if not app.zombieList[i].dead:

                    app.zombieList[i].walk(app)
                    app.zombieList[i].smartJump(app)
                    if app.zombieList[i].level == 3:
                        app.zombieList[i].avoidWallnut(app)
                    if app.zombieList[i].jumpFrom != None:
                        
                        newRow, newCol = app.zombieList[i].jumpTo
                        if not app.zombieList[i].jumpFinished:
                            jumpToCell(app,app.zombieList[i], newRow, newCol)
                    if app.zombieList[i].moveFrom != None:
                        newRow, newCol = app.zombieList[i].moveTo
                        if not app.zombieList[i].moveFinished:
                            moveToCell(app,app.zombieList[i], newRow, newCol)
                else:#if dead, stop walking, death animation
                    pass
            #detect lose
            userLoseDetect(app)
            #zombie animation
            for i in range(len(app.zombieList)):
                if app.zombieList[i].walking:
                    app.zombieList[i].imageIndex = (app.zombieList[i].imageIndex + 1) % len(app.zombieList[i].walkingList)
                    pass
                elif app.zombieList[i].eating:
                    pass
                elif app.zombieList[i].dying:
                    app.zombieList[i].imageIndex = (app.zombieList[i].imageIndex + 1)
                    if app.zombieList[i].imageIndex == len(app.zombieList[i].dyingList)-1:
                        app.zombieList[i].dying = False
                    pass
                elif app.zombieList[i].hurt1Walking:
                    pass

            #wallnut
            app.wallnutIntervalCount -= 1
            if app.wallnutIntervalCount<= 0:
                generateStone(app)
                app.wallnutIntervalCount = app.wallnutInterval
            for l in range(len(app.wallnutList)):
                if app.wallnutList[l].falling:
                    targetY = getCellCenter(app, app.wallnutList[l].row, app.wallnutList[l].col)[1]
                    app.wallnutList[l].y += targetY / (app.stepsPerSecond*3)
                    if app.wallnutList[l].y >= targetY:
                        app.wallnutList[l].falling = False
                else:
                    #wallnut being Eaten Animation
                    for s in range(len(app.zombieList)):
                        if app.zombieList[s].row == app.wallnutList[l].row and app.zombieList[s].col == app.wallnutList[l].col and not app.zombieList[s].dead and not app.wallnutList[l].eaten:
                            app.wallnutList[l].beingEaten = True
                        else:
                            app.wallnutList[l].beingEaten = False
                    if app.wallnutList[l].beingEaten:
                        app.wallnutList[l].opacityCount -= 1
                        if app.wallnutList[l].opacityCount == 0:
                            app.wallnutList[l].opac = not app.wallnutList[l].opac 
                            app.wallnutList[l].opacityCount = 5
            zombieBiteWallnut(app)
            #wallnut being Eaten Animation
            

            #add one gua when numZombKilled + 2
            if app.numZombKilled //2 > app.guaLength -1 :
                addOneGua(app)
            #check if time ends
            if app.timer >= app.finishTime:
                app.zombieFinished = True #stop generating new zombies
                winOrNot(app)
        


    
def onAppStart(app):
    app.gameView = False
    app.frontPage = True
    app.instructions = False

    app.width = 800
    app.height = 500

    app.diffLevel = 0
    #animations
    app.HDGuacodile = CMUImage(Image.open('HDGuacodile.png'))
    #HDGuacodile Image obtained from https://plantsvszombies.fandom.com/wiki/File:HDGuacodile.png
    app.ZombieHD = CMUImage(Image.open('ZombieHD.png'))
    #ZombieHD Image obtained from https://plantsvszombies.fandom.com/wiki/File:Zombie_HD_Old.png
    app.FootballZombieHD = CMUImage(Image.open('FootballZombieHD.png'))
    #FootballZombieHD obtained from https://plantsvszombies.fandom.com/wiki/File:FootballZombieHD.png
    app.ConeHeadZombie = CMUImage(Image.open('ConeHeadZombie.png'))
    #ConeHeadZombie image obtained from  https://plantsvszombies.fandom.com/wiki/File:Leconeheadwebsite.png
    app.Logo =  CMUImage(Image.open('Logo.png'))
    #Logo png obtained from https://branditechture.agency/brand-logos/download/plants-vs-zombies-2/#google_vignette
    reset(app)
    

def reset(app):
    app.isPaused = False
    app.isGameOver  = False
    app.win = False
    app.lose = False
    app.hitWallLose = False
    app.brainEatenLose = False
    #board
    app.boardRow = 10
    app.boardCol = 18
    app.boardLeft = 100
    app.boardTop = 70
    app.boardWidth = 18*36
    app.boardHeight = 10*36
    app.cellBorderWidth = 1
    
    app.stepsPerSecond = 10
    #time, progress, wave of zombie
    app.timer = 0 #in terms of steps
    minutes = 3 if app.diffLevel == 1 else 5
    app.finishTime = app.stepsPerSecond * 60 * minutes
    app.numOfWaves = 2 if app.diffLevel == 1 else 3
    app.numOfWavesLeft = app.numOfWaves
    app.waveTimeCount = app.stepsPerSecond * 50 #initially, wait 50s for first wave
    app.waveInterval = (app.finishTime-app.waveTimeCount)//(app.numOfWaves-1)-120
    app.zombieFinished = False
    
    #Animation
    #game background, obtained from https://plantsvszombies.fandom.com/wiki/Big_Wave_Beach?file=Beach_nowater.png
    app.gameViewBackground = CMUImage(Image.open('gameViewBackground.png'))

    #guac image
    guaRight1 = CMUImage(Image.open('guaRight1.png'))
    guaLeft1 = CMUImage(Image.open('guaLeft1.png'))
    guaUp1 = CMUImage(Image.open('guaUp1.png'))
    guaDown1 = CMUImage(Image.open('guaDown1.png'))
    #guaRight1, guaLeft1, guaUp1, guaDown1 are original and edited versions of https://plantsvszombies.fandom.com/wiki/File:HDGuacodile.png
    app.guaImageList = [ [guaLeft1],[guaRight1], [guaUp1], [guaDown1]]

    #zombie image
    #level1 Walk
    level1Walk1 = CMUImage(Image.open('level1Walk1.png'))
    level1Walk2 = CMUImage(Image.open('level1Walk2.png'))
    level1Walk3 = CMUImage(Image.open('level1Walk3.png'))
    level1Walk4 = CMUImage(Image.open('level1Walk4.png'))
    level1Walk5 = CMUImage(Image.open('level1Walk5.png'))
    level1Walk6 = CMUImage(Image.open('level1Walk6.png'))
    level1Walk7 = CMUImage(Image.open('level1Walk7.png'))
    level1Walk8 = CMUImage(Image.open('level1Walk8.png'))
    level1Walk9 = CMUImage(Image.open('level1Walk9.png'))
    #all images in app.level1WalkList are obtained from the original Plant vs Zombie game by Electronic Arts Inc.
    app.level1WalkList = [level1Walk1, level1Walk2, level1Walk3, level1Walk4, 
                          level1Walk5, level1Walk6, level1Walk7, level1Walk8, level1Walk9]

    app.image = level1Walk1

    #level1 Die
    level1Die1 = CMUImage(Image.open('level1Die1.png'))
    level1Die2 = CMUImage(Image.open('level1Die2.png'))
    level1Die3 = CMUImage(Image.open('level1Die3.png'))
    level1Die4 = CMUImage(Image.open('level1Die4.png'))
    level1Die5 = CMUImage(Image.open('level1Die5.png'))
    level1Die6 = CMUImage(Image.open('level1Die6.png'))
    level1Die7 = CMUImage(Image.open('level1Die7.png'))
    level1Die8 = CMUImage(Image.open('level1Die8.png'))
    level1Die9 = CMUImage(Image.open('level1Die9.png'))
    level1Die10 = CMUImage(Image.open('level1Die10.png'))
    level1Die11 = CMUImage(Image.open('level1Die11.png'))
    level1Die12 = CMUImage(Image.open('level1Die12.png'))
    level1Die13 = CMUImage(Image.open('level1Die13.png'))
    level1Die14 = CMUImage(Image.open('level1Die14.png'))
    app.level1DieList = [level1Die1,level1Die2,level1Die3,level1Die4,level1Die5, level1Die6, level1Die7, level1Die8, level1Die9, level1Die10,level1Die11, level1Die12, level1Die13, level1Die14 ]
    #all images in app.level1DieList are obtained from the original Plant vs Zombie game by Electronic Arts Inc.
    #temporary
    app.level2WalkList = [app.ConeHeadZombie]
    app.level3WalkList = [app.FootballZombieHD]
    #cited above at app.ConeHeadZombie and app.FootballZombieHD

    level3Eat1 = CMUImage(Image.open('level3Eat1.png'))
    app.level3EatList = [level3Eat1]
    # All images in app.level3EatList are taken from https://cdn.discordapp.com/attachments/757684407288201276/773939942186549268/footballfast.gif

    level3Hurt1Walk1 = CMUImage(Image.open('level3Hurt1Walk1.png'))
    app.level3Hurt1WalkList = [level3Hurt1Walk1]
    # All images in app.level3Hurt1WalkList are taken from https://cdn.discordapp.com/attachments/757684407288201276/773939942186549268/footballfast.gif


    level3Die1 = CMUImage(Image.open('Level3Die1.png'))
    app.level3DieList = [level3Die1, level3Die1, level3Die1, level3Die1]
    # All images in app.level3DieList are taken from https://cdn.discordapp.com/attachments/757684407288201276/773939942186549268/footballfast.gif


    #zombies
    app.zombieSpeed = 0.5 #may vary with difficulty level?
    app.zombieGenInterval = 200 #steps, randomly changes in onStep after each use
    app.zombieGenIntervalCount = 15
    app.zombieList = []
    cellWidth, cellHeight = getCellSize(app)
    #zombie generation(normal period, crowded period)
    app.zNormNumList = [(2, 3), (3, 4), (3, 5)]#number of zombies generated during normal period, 
                            #(lower, upper) for each diffLevel, include upper
    app.zNormNumLower, app.zNormNumUpper = app.zNormNumList[app.diffLevel-1]

    #guacodile 
    app.guaSpeed = 3
    row = random.randint(2, app.boardRow-3)
    col = random.randint(2, app.boardCol-3)
    initX, initY = getCellCenter(app, row, col)
    #locations: 0-left, 1-right, 2-up, 3-down
    app.dirList = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir = random.randint(0, 1)# initial location, can be left or right
    app.guaDir = dir #direction of the whole line?
    head = Guacodile(app, initX, initY, dir) #initialize head
    app.guaList = [head] # list contains all gua
    app.guaLength = 1
    #length of gua
    length, height = getImageSize(app.guaImageList[0][0])
    app.oneGuaLength = length//100
    app.oneGuaHeight = length//100
    app.turn = None
    #period between Huge Waves (level 1: 2 waves, level2/3: 3 waves)

    #gua-zomb interact
    app.numZombKilled = 0 #decides app.guaLength

    #gua-wallnut
    app.guaHitWallnut = False
    app.guaHitWallnutTime = app.stepsPerSecond * 3
    app.guaHitWallnutCounter = app.guaHitWallnutTime
    #generate Wall-nut
    wallnut1 = CMUImage(Image.open('wallnut1.png'))
    #wallnut1 obtained from https://plantsvszombies.fandom.com/wiki/Wall-nut/Gallery?file=HD_Wall-nut.png
    app.wallnutImages = [wallnut1]
    app.wallnutIntervalCount = 200
    app.wallnutInterval = random.randint(200, 400) if app.diffLevel == 3 else random.randint(300, 450)
    #app.wallnutInterval = random.randint(20, 40) if app.diffLevel == 3 else random.randint(300, 450)
    app.wallnutList = []


def drawFrontPage(app):
    drawRect(0,0,app.width, app.height)
    #guac
    imageWidth, imageHeight = getImageSize(app.HDGuacodile)
    drawImage(app.HDGuacodile, app.width/2-200, app.height/2-80,width = imageWidth//11, height = imageHeight//11, align = 'center', rotateAngle = 330)

    #ZombieHD
    imageWidth, imageHeight = getImageSize(app.ZombieHD)
    drawImage(app.ZombieHD, app.width/2+70, app.height/2-120,width = imageWidth//2, height = imageHeight//2, align = 'center')

    #ConeHeadZombie
    imageWidth, imageHeight = getImageSize(app.ConeHeadZombie)
    drawImage(app.ConeHeadZombie, app.width/2+130, app.height/2-110,width = imageWidth//5.3, height = imageHeight//5.3, align = 'center')
    #FootballZombieHD
    imageWidth, imageHeight = getImageSize(app.FootballZombieHD)
    drawImage(app.FootballZombieHD, app.width/2+210, app.height/2-80,width = imageWidth//2.9, height = imageHeight//2.9, align = 'center')
    
    #logo
    imageWidth, imageHeight = getImageSize(app.Logo)
    drawImage(app.Logo, app.width/2, app.height/2+35,width = imageWidth//6, height = imageHeight//7, align = 'center')

    drawLabel("~By Guacodile", app.width/2+270, app.height/2+100, size = 28, font = 'sacramento', fill = 'white')
    drawButtons(app)

def drawButtons(app):
    #levels
    for i in range(3):
        drawRect(app.width/2-170 + i * 170, 420, 100, 50, fill = 'lightGray', border = 'darkGrey', 
                 borderWidth = 3, align = 'center')
        drawLabel(f"Level{i+1}", app.width/2-170 + i * 170, 420)

def onMousePress(app, mouseX, mouseY):
    if app.frontPage:
        for i in range(3):
            if (app.width/2-170 + i * 170 - 50 <= mouseX <= app.width/2-170 + i * 170 + 
                50) and (420-25 <= mouseY <= 420 + 25):
                app.diffLevel = i + 1
                app.numOfWaves = 2 if app.diffLevel == 1 else 3
                app.gameView = True
                app.frontPage = False
                reset(app)
        pass

def redrawAll(app):
    if app.frontPage:
        drawFrontPage(app)
    elif app.gameView:
        drawBoard(app)
        
        drawProgressBar(app)
        
        drawWallnut(app)
        drawGuacodileLine(app)
        drawZombies(app)
        drawWaveMessage(app)
        #win or lose
        if app.isGameOver:
            #print win/lose message 
            drawWinLoseMessage(app)
    pass



#zombies
def drawZombies(app):
    pilImage = app.image.image
    #pil image
    cellWidth, cellHeight = getCellSize(app)
    for i in range(len(app.zombieList)-1, -1, -1):
        if app.zombieList[i].level == 1:
            if not app.zombieList[i].dead:
                if app.zombieList[i].walking:
                    imageWidth, imageHeight = getImageSize(app.zombieList[i].walkingList[app.zombieList[i].imageIndex])
                    drawImage(app.zombieList[i].walkingList[app.zombieList[i].imageIndex], 
                              app.zombieList[i].x, app.zombieList[i].y, width = imageWidth//2.5, height = imageHeight//2.5, align = 'bottom')
            else:
                if app.zombieList[i].dying:
                    #level1 and 2 have same die list

                    imageWidth, imageHeight = getImageSize(app.zombieList[i].dyingList[app.zombieList[i].imageIndex])
                    drawImage(app.zombieList[i].dyingList[app.zombieList[i].imageIndex], 
                              app.zombieList[i].x, app.zombieList[i].y, width = imageWidth//2.5, height = imageHeight//2.5, align = 'bottom')
                pass
                #dead animation
            pass
        elif app.zombieList[i].level == 2:
            if not app.zombieList[i].dead:
               if app.zombieList[i].walking:
                    imageWidth, imageHeight = getImageSize(app.zombieList[i].walkingList[app.zombieList[i].imageIndex])
                    drawImage(app.zombieList[i].walkingList[app.zombieList[i].imageIndex], 
                              app.zombieList[i].x, app.zombieList[i].y, width = pilImage.width//2.5, height = pilImage.height//2.5, align = 'bottom')
            else:
                if app.zombieList[i].dying:
                    #level1 and 2 have same die list

                    imageWidth, imageHeight = getImageSize(app.zombieList[i].dyingList[app.zombieList[i].imageIndex])
                    drawImage(app.zombieList[i].dyingList[app.zombieList[i].imageIndex], 
                              app.zombieList[i].x, app.zombieList[i].y, width = pilImage.width//2.5, height = pilImage.height//2.5, align = 'bottom')
            
        else:
            if not app.zombieList[i].dead:
               if app.zombieList[i].walking:
                    imageWidth, imageHeight = getImageSize(app.zombieList[i].walkingList[app.zombieList[i].imageIndex])
                    drawImage(app.zombieList[i].walkingList[app.zombieList[i].imageIndex], 
                              app.zombieList[i].x, app.zombieList[i].y, width = pilImage.width//2.5, height = pilImage.height//2.5, align = 'bottom')
            else:
                if app.zombieList[i].dying:
                    #level1 and 2 have same die list

                    imageWidth, imageHeight = getImageSize(app.zombieList[i].dyingList[app.zombieList[i].imageIndex])
                    drawImage(app.zombieList[i].dyingList[app.zombieList[i].imageIndex], 
                              app.zombieList[i].x, app.zombieList[i].y, width = pilImage.width//2.5, height = pilImage.height//2.5, align = 'bottom')
                
                pass


#randomly generate Zombies
def zombieGenerator(app):
    #normal period
    zombNum = random.randint(app.zNormNumLower, app.zNormNumUpper)
    for i in range(zombNum):
        generateOneZomb(app)
    pass

def zombieWaveGenerator(app):
    #wave
    zombNum = random.randint(app.zNormNumLower+2, app.zNormNumUpper +2)
    for i in range(zombNum):
        generateOneZomb(app)
    pass

def generateOneZomb(app):
    
    #zombie levels: 1/2 in difflevel 1; 1/2/3 in difflevel 2 or 3
    levelMax = 2 if app.diffLevel==1 else 3
    level = random.randint(1, levelMax)
    # x, y are the bottom center location of the zombie
    #row col are the cell that zombie stands in
    x, y, row, col = randomZombieLocation(app, level)
    app.zombieList.append(Zombie(app, level, x, y, row, col)) #name each zombie with time
    pass

def randomZombieLocation(app, level):
    return randomZombieLocationHelper(app, 0, 0, 0, 0, set(), level)

def randomZombieLocationHelper(app, x, y, row, col, wallnutRowSet, level):
   # check if the location already exists in a close distance
    legal = True
    if x != 0:
        for i in range(len(app.zombieList)):
            #new x y location cannot be within 5 distance of current location
            if abs(app.zombieList[i].x - x)<5 and abs(app.zombieList[i].y - y)<5 and not app.zombieList[i].dead:
                legal = False
                break
            for o in range(len(app.guaList)):
            #cannot generate in cell with gua
                if app.guaList[o].row == row and app.guaList[o].col == col:
                    legal = False
            for k in range(len(app.wallnutList)):
            #does not generate in cell with wallnut
                if app.wallnutList[k].row == row and app.wallnutList[k].col == col and not (app.wallnutList[k].falling or app.wallnutList[k].eaten):
                    legal = False
                if level == 1:
                #level1 zombie does not generate in wallnut row
                    if row == app.wallnutList[k].row and not (app.wallnutList[k].falling or app.wallnutList[k].eaten):
                        legal = False
                #but if wallnut in every row, legal
                wallnutRowSet.add(app.wallnutList[k].row)
            for num in range(app.boardRow):
                if num not in wallnutRowSet:
                    break
                if num == app.boardRow-1:
                    legal = True
    if legal and x != 0 and y != 0:
        return (x, y, row, col)
    else:
        cellWidth, cellHeight = getCellSize(app)
        col= random.randint(app.boardCol//2, app.boardCol-1) #can change later when difflevel changes
        row = random.randint(0, app.boardRow-1) #since zombies are two-cells tall
        centerX, centerY = getCellCenter(app, row, col)
        x = random.randint(app.boardLeft + col * cellWidth, app.boardLeft + (col+1) * cellWidth-cellWidth/2)
        return randomZombieLocationHelper(app, x, centerY, row, col, wallnutRowSet, level)
        
    
#detects if zombie crossed board left and reaches home
def userLoseDetect( app):

    for i in range(len(app.zombieList)):
        if app.zombieList[i].x <= app.boardLeft:
            app.lose = True
            app.brainEatenLose = True
            app.isGameOver = True

#detect win: if not zombie on board and time ends
def winOrNot(app):
    if app.timer >= app.finishTime:
        for i in range(len(app.zombieList)):
            if app.zombieList[i].dead == False:
                return
        app.isGameOver = True
        app.win = True


    

        

def onKeyPress(app, key):
    if key == 'h':
        app.gameView = False
        app.instructions = False
        app.frontPage = True
    if app.gameView:
        app.turn = None
        cellWidth, cellHeight = getCellSize(app)
        #can only turn at the middle of cell
        #print((app.guaList[0].x - app.boardLeft) % cellWidth, (app.guaList[0].y - app.boardTop) % cellHeight, (app.guaList[0].y - app.boardTop))
        if app.turn == None:
            if key == 'up' and app.guaDir != 3:
                app.turn = 'up'
            elif key == 'down' and app.guaDir != 2 :
                app.turn = 'down'
            elif key == 'left' and app.guaDir != 1 :
                app.turn = 'left'
            elif key == 'right' and app.guaDir != 0 :
                app.turn = 'right'
        if key == 'p':
            app.isPaused = not app.isPaused
        elif key == 'r':
            reset(app)
#guacodile
#draw Guacodile Line
def drawGuacodileLine(app):
    #pilImage = app.image.image
    for i in range(len(app.guaList)):
        #decides which animation to draw based on direction
        index1, index2 = app.guaList[i].aniIndex
        imageWidth, imageHeight = getImageSize(app.guaImageList[index1][index2])
        drawImage(app.guaImageList[index1][index2], app.guaList[i].x, app.guaList[i].y,align = 'center', width=imageWidth//100, height=imageHeight//100)
        

def moveGuacodileLine(app): #used in onStep, headDir is index for dirList

    cellWidth, cellHeight = getCellSize(app)
    #turn in the middle of cell
    if app.turn != None:
        if int((app.guaList[0].x - app.boardLeft) % cellWidth) == int(cellWidth/2):
            if app.turn == 'up':
                app.guaDir = 2
                app.turn = None
            elif app.turn == 'down':
                app.guaDir = 3
                app.turn = None
        if int((app.guaList[0].y - app.boardTop) % cellHeight) == int(cellHeight/2):
            if app.turn == 'left':
                app.guaDir = 0
                app.turn = None
            elif app.turn == 'right':
                app.guaDir = 1
                app.turn = None
        
    for i in range(len(app.guaList)):
        if i == 0:
            if app.guaList[0].dir == app.guaDir: #when dir key is pressed to change dir
                #change animation dir
                pass
            app.guaList[i].dir = app.guaDir
            dx, dy = app.dirList[app.guaDir]
            dx, dy = dx*app.guaSpeed, dy*app.guaSpeed
            app.guaList[i].x += dx
            app.guaList[i].y += dy
        elif app.guaList[i].dir == app.guaList[i-1].dir:
            dx, dy = app.dirList[app.guaList[i].dir]
            dx, dy = dx*app.guaSpeed, dy*app.guaSpeed
            app.guaList[i].x += dx
            app.guaList[i].y += dy
        else:#when direction of previous gua is different from current gua
            
            prevDx, prevDy = app.dirList[app.guaList[i-1].dir]
            dx, dy = app.dirList[app.guaList[i].dir]
            if prevDx == 0:#prev gua is going up or down
                prevX = app.guaList[i-1].x
                currX = app.guaList[i].x
                if ((currX + dx*app.guaSpeed)-prevX >=0 and dx <0) or ((currX + dx*app.guaSpeed)-prevX<=0 and dx >0):
                    app.guaList[i].x += dx*app.guaSpeed
                else:#change direction
                    rest= app.guaSpeed-abs(prevX-app.guaList[i].x)
                    app.guaList[i].x = prevX
                    
                    app.guaList[i].y += prevDy * rest
                    app.guaList[i].dir = app.guaList[i-1].dir 
            else:#prevDy == 0, prev gua is going left or right
                prevY = app.guaList[i-1].y
                currY = app.guaList[i].y
                if ((currY + dy*app.guaSpeed)-prevY >=0 and dy <0) or ((currY + dy*app.guaSpeed)-prevY<=0 and dy >0):
                    app.guaList[i].y += dy*app.guaSpeed
                else:#change direction
                    rest= app.guaSpeed-abs(prevY-app.guaList[i].y)
                    app.guaList[i].y = prevY
                    
                    app.guaList[i].x += prevDx * rest
                    app.guaList[i].dir = app.guaList[i-1].dir 
        #update row col
        app.guaList[i].row, app.guaList[i].col = getRowCol(app, app.guaList[i].x, app.guaList[i].y)
            
def updateGuaImage(app):
    for i in range(len(app.guaList)):
        index1, index2 = app.guaList[i].aniIndex
        index1 = app.guaList[i].dir
        index2 = (index2+1)%len(app.guaImageList[0])
        app.guaList[i].aniIndex = (index1, index2)
        
        
def addOneGua(app):
    #change gua width
    cellWidth, cellHeight = getCellSize(app)
    lastX, lastY=app.guaList[-1].x, app.guaList[-1].y
    lastDx, lastDy = app.dirList[app.guaList[-1].dir]
    newX = lastX - lastDx * app.oneGuaLength
    newY = lastY - lastDy * app.oneGuaLength
    app.guaList.append(Guacodile(app, newX, newY, app.guaList[-1].dir))
    app.guaLength += 1 

def guaHitWall(app):
    #change oneGuaLength
    if app.boardLeft + app.oneGuaLength/2 >= app.guaList[0].x or app.guaList[0].x >= (app.boardLeft + app.boardWidth - app.oneGuaLength/2):
        app.lose = True
        app.hitWallLose = True                                                                                                                                                            
        app.isGameOver = True
    if app.boardTop + app.oneGuaLength/2 >= app.guaList[0].y or app.guaList[0].y >= (app.boardTop + app.boardHeight - app.oneGuaLength/2):
        app.lose = True
        app.hitWallLose = True                                                                               
        app.isGameOver = True
    pass

def guaHitSelf(app):
    for i in range(len(app.guaList)):
        
        if i>=2 and app.guaList[0].row == app.guaList[i].row and app.guaList[0].col == app.guaList[i].col:
            app.guaList = app.guaList[:i]
            break


def guaCollideZomb(app):
    for i in range(len(app.zombieList)):
        for k in range(len(app.guaList)):
            if app.guaList[k].row == app.zombieList[i].row and app.guaList[k].col == app.zombieList[i].col and (app.guaList[k],app.guaList[k].row, app.guaList[k].col) not in app.zombieList[i].biteList:
                app.zombieList[i].bitesLeft -= 1
                #animation change
                if app.zombieList[i].level == 2:
                    if app.zombieList[i].bitesLeft == 1:
                        app.zombieList[i].walkingList = app.zombieList[i].hurt1WalkingList
                elif app.zombieList[i].level == 3:
                    if app.zombieList[i].bitesLeft == 1:
                        app.zombieList[i].walkingList = app.zombieList[i].hurt1WalkingList
                #record where collide, only collide onece in each cell
                app.zombieList[i].biteList.append((app.guaList[k],app.guaList[k].row, app.guaList[k].col) )
                #zombie death
                if app.zombieList[i].bitesLeft == 0:
                    app.zombieList[i].dead = True
                    app.numZombKilled += 1
                    #animation
                    app.zombieList[i].dying = True
                    app.zombieList[i].walking = False
                    app.zombieList[i].eating = False
                    app.zombieList[i].hurt1Walking = False
                    app.zombieList[i].hurt2Walking = False
                    app.zombieList[i].imageIndex = 0
                    
    pass

#generate random falling stones
#zombies have to eat stones/wait for the stones to disappear
#gracodile freeze for 2s when hit stone, and then stone vanished
def generateStone(app):
    row, col = generateStoneLocation(app)
    app.wallnutList.append(Wallnut(app, row, col))
    pass

def generateStoneLocation(app, row = -1, col = -1):
    legal = True
    #do not generate on gua or zombie
    for i in range(len(app.guaList)):
        if app.guaList[i].row == row and app.guaList[i].col ==col:
            legal = False
    for j in range(len(app.zombieList)):
        if app.zombieList[j].row == row and app.zombieList[j].col ==col:
            legal = False
    #in board range
    if row < 0 or row >= app.boardRow or col < 0 or col >= app.boardCol:
        legal = False
    if legal:
        return (row, col)
    else:
        row = random.randint(0, app.boardRow-1)
        col = random.randint(0, app.boardCol-1)
        return generateStoneLocation(app, row , col )
    
#zombie bite walnut
def zombieBiteWallnut(app):
    for i in range(len(app.wallnutList)):
        if not app.wallnutList[i].eaten and not app.wallnutList[i].falling:
            for k in range(len(app.zombieList)):
                if app.wallnutList[i].row == app.zombieList[k].row and app.wallnutList[i].col == app.zombieList[k].col:
                    app.wallnutList[i].bitesLeft -= 1
                    app.zombieList[k].blocked = True
                    app.wallnutList[i].beingEaten = True
                    #wallnut being eaten animation?

                    #zombie eating animation?
        for k in range(len(app.zombieList)):
            if app.wallnutList[i].bitesLeft<= 0:
                app.wallnutList[i].beingEaten = False
                app.wallnutList[i].eaten = True
                app.zombieList[k].blocked = False


#if gua hit wallnut, wallnut disappears and gua stays for 3s
def guaHitWallnut(app):
    for i in range(len(app.wallnutList)):
        if app.wallnutList[i].row == app.guaList[0].row and app.wallnutList[i].col == app.guaList[0].col and not app.wallnutList[i].eaten:
            app.wallnutList[i].eaten = True
            app.wallnutList[i].beingEaten = False
            app.guaHitWallnut = True


def drawWallnut(app):
    
    for i in range(len(app.wallnutList)-1, -1, -1):
        #decides which animation to draw based on direction
        if not app.wallnutList[i].eaten:
            opacity = 20 if app.wallnutList[i].falling or app.wallnutList[i].opac else 100
            
            imageIndex = app.wallnutList[i].imageIndex
            imageWidth, imageHeight = getImageSize(app.wallnutImages[imageIndex])
            drawImage(app.wallnutImages[imageIndex], app.wallnutList[i].x, app.wallnutList[i].y,align = 'bottom', width=imageWidth//18, height=imageHeight//18, opacity = opacity)
        
    pass



#draw wave message

def drawWaveMessage(app):
    #font
    if app.waveTimeCount <= 50:
        message = "A Big Wave of Zombie is Approaching~" if app.numOfWavesLeft >1 else "Final Wave of Zombie!"
        drawLabel(message, app.boardLeft + app.boardWidth/2, 
                 app.boardTop + app.boardHeight/2, fill = 'red', size = 16, font= 'cinzel')
        
#draw win/lose messages
def drawWinLoseMessage(app):
    if app.win:
        drawWin(app)
    if app.lose:
        drawLose(app)

#win message
def drawWin(app):
    drawLabel('YOU WIN!', app.width/2, app.height/2, size = 30, font = 'cinzel', bold = True, fill = 'red')
    pass
#losemessage
def drawLose(app):
    #depend on guacodile dies or zombie eats brain
    drawRect(0,0,app.width, app.height, fill = 'black', opacity = 40)
    if app.brainEatenLose:
        drawLabel('ZOMBIE HAS EATEN YOUR BRAIN!!!', app.width/2, app.height/2, size = 40, font = 'cinzel', bold = True, italic = True, fill = 'red')
    elif app.hitWallLose:
        drawLabel('GUACODILE HIT THE WALL!!!',app.width/2, app.height/2, size = 40, font = 'cinzel', bold = True, italic = True, fill = 'red')
    pass

#progressBar
def drawProgressBar(app):
    width = 0
    if app.timer > 0: #draw the moving bar
        if app.timer <= app.finishTime:
            width = 150*(app.timer/app.finishTime)
        else:
            width = 150
        drawRect(300+150, 25, width, 20, border = None, align = 'top-right', fill = 'blue')
    drawRect(300, 25, 150, 20, fill = None, border = 'black', borderWidth = 2) #drawBorder
    for i in range(app.numOfWaves):#drawFlag
        x = ((120 + i * app.waveInterval)/app.finishTime)*150 + 300
        #flag rises if reached
        if 450-width <= x:
            y = 25
        else:
            y = 20+25 
        drawFlag(app, x, y)

#x, y is the bottom location of the stick of the flag
def drawFlag(app, x, y):
    drawLine(x, y, x, y-18, lineWidth = 2)
    drawPolygon(x, y-18, x, y-12, x+8, y-15, fill = 'red', borderWidth = 1, border = 'black')
    pass


def main():
    runApp()
main()
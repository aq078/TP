from cmu_graphics import *
import random

#board
def drawBoard(app):
    cellWidth, cellHeight = getCellSize(app)
    for r in range(app.boardRow):
        for c in range(app.boardCol):
            #top left corner of cell
            x = app.boardLeft + c * cellWidth
            y = app.boardTop + r * cellHeight
            drawRect(x, y, cellWidth, cellHeight, border = 'black', fill = None,
                     borderWidth = app.cellBorderWidth)
    #drawBorder
    drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, 
             fill = None, border = 'black', borderWidth = app.cellBorderWidth*2 )
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

class Guacodile:
    def __init__(self,app, x, y, dir):
        self.x = x 
        self.y = y
        self.dir = dir
        self.row, self.col = getRowCol(app, x, y)
    def __repr__(self):
        return f'x:{self.x}, y:{self.y}, direction:{self.dir}'

class Zombie:
    def __init__(self, level, x, y, row, col):
        self.level = level
        self.bitesLeft = level
        self.x=x
        self.y=y
        self.row = row
        self.col = col
        self.biteList = []#takes (which gua, row, col)
        self.dead = False
        self.jumpsLeft = level-2 #only level 3 zombie can jump

    def __repr__(self):
        return f'Level: {self.level}, bitesLeft = {self.bitesLeft}, location = ({self.x}, {self.y}, rowCol = {self.row}, {self.col})'

    def walk(self, app):
        self.x -= app.zombieSpeed
        self.col = getRowCol(app, self.x, self.y)[1]
    
    def smartJump(app, self):
        if self.jumpsLeft > 0:
            if abs(app.guaList[0].row - self.row)<= 1 and abs(app.guaList[0].col - self.col)<= 1:
                #if guahead within 3*3
                choices = [(-1, -1), (0, -1), (1, -1),(-1, 0), (1, 0),(0, 1),(-1, 1),(1, 1)]
                #loop through the front cells first
                for dcol, drow in choices:
                    newRow, newCol = self.row + drow, self.col + dcol
                    if 0 <= newRow < app.boardRow and 0 <= newCol < app.boardCol:
                        #if in range of board
                        guaDcol, guaDrow = app.dirList[app.guaList[0].dir]
                        guaNewRow = app.guaList[0].row + guaDrow
                        guaNewCol = app.guaList[0].col + guaDcol
                        if (app.guaList[0].row != newRow or app.guaList[0].col != newCol) and(guaNewCol!= newCol or guaNewRow != newRow):
                            #guahead not in that cell and is not the next cell gua enters if stay in currDir
                            jumpToCell(app, self, newRow, newCol)
                    self.jumpsLeft -= 1
                    break

#zombieJump animation with gravity                   
def jumpToCell(app, self, newRow, newCol):
    currX, currY = self.x, self.y
    #...
    #rewrite self.x, self.y, self.row, self.col
    pass



    
def onAppStart(app):
    reset(app)

def reset(app):
    app.isPaused = False
    app.isGameOver  = False
    app.win = False
    app.lose = False
    app.diffLevel = 1
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
    print(app.waveInterval)
    

    #board
    app.width = 800
    app.height = 500
    app.boardRow = 10
    app.boardCol = 18
    app.boardLeft = 100
    app.boardTop = 50
    app.boardWidth = 18*36
    app.boardHeight = 10*36
    app.cellBorderWidth = 1

    #zombies
    app.zombieSpeed = 0.5 #may vary with difficulty level
    app.zombieGenInterval = 200 #steps, randomly changes in onStep after each use
    app.zombieGenIntervalCount = 15
    app.zombieList = []
    cellWidth, cellHeight = getCellSize(app)
    #zombie generation(normal period, crowded period)
    app.zNormNumList = [(2, 3), (2, 4), (3, 4)]#number of zombies generated during normal period, 
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
    app.oneGuaLength = cellWidth/2
    app.oneGuaHeight = cellHeight/2
    app.turn = None
    #period between Huge Waves (level 1: 2 waves, level2/3: 3 waves)

    #gua-zomb interact
    app.numZombKilled = 0 #decides app.guaLength

    #test
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)
    # addOneGua(app)

def redrawAll(app):
    drawProgressBar(app)
    drawBoard(app)
    drawGuacodileLine(app)
    drawZombies(app)
    drawWaveMessage(app)
    #win or lose
    pass



#zombies
def drawZombies(app):
    cellWidth, cellHeight = getCellSize(app)
    for i in range(len(app.zombieList)):
        if app.zombieList[i].level == 1:
            if not app.zombieList[i].dead:
                drawRect(app.zombieList[i].x, app.zombieList[i].y, cellWidth/2, 
                         cellHeight, align = 'bottom', fill = 'grey', opacity = 50)
            else:
                pass
                #dead animation
            pass
        elif app.zombieList[i].level == 2:
            if not app.zombieList[i].dead:
                drawRect(app.zombieList[i].x, app.zombieList[i].y, cellWidth/2
                         , cellHeight, align = 'bottom', fill = 'blue', opacity = 50)
            #animation depends on number of bites left
            pass
        else:
            if not app.zombieList[i].dead:
                drawRect(app.zombieList[i].x, app.zombieList[i].y, cellWidth/2
                         , cellHeight, align = 'bottom', fill = 'red', opacity = 50)
            #animation depends on number of bites left
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
    zombNum = random.randint(app.zNormNumLower+2, app.zNormNumUpper +3)
    for i in range(zombNum):
        generateOneZomb(app)
    pass

def generateOneZomb(app):
    # x, y are the bottom center location of the zombie
    #row col are the cell that zombie stands in
    x, y, row, col = randomZombieLocation(app)
    #zombie levels: 1/2 in difflevel 1; 1/2/3 in difflevel 2 or 3
    levelMax = 2 if app.diffLevel==1 else 3
    level = random.randint(1, levelMax)
    app.zombieList.append(Zombie(level, x, y, row, col)) #name each zombie with time
    pass

def randomZombieLocation(app):
    return randomZombieLocationHelper(app, 0, 0, 0, 0)

def randomZombieLocationHelper(app, x, y, row, col):
   # check if the location already exists in a close distance
    legal = True
    if x != 0:
        for i in range(len(app.zombieList)):
            #new x location cannot be within 5 distance of current location
            if abs(app.zombieList[i].x - x)<5 :
                legal = False
                break
    if legal == True and x != 0 and y != 0:
        return (x, y, row, col)
    else:
        cellWidth, cellHeight = getCellSize(app)
        col= random.randint(6, app.boardCol-1) #can change later when difflevel changes
        row = random.randint(0, app.boardRow-1) #since zombies are two-cells tall
        centerX, centerY = getCellCenter(app, row, col)
        x = random.randint(app.boardLeft + col * cellWidth, app.boardLeft + (col+1) * cellWidth-cellWidth/2)
        return randomZombieLocationHelper(app, x, centerY, row, col)
        
    
#detects if zombie crossed board left and reaches home
def userLoseDetect( app):
    for i in range(len(app.zombieList)):
        if app.zombieList[i].col < 0:
            app.lose = True
            app.isGameOver = True

#detect win: if not zombie on board and time ends
def winOrNot(app):
    for i in range(len(app.zombieList)):
        if app.zombieList[i].dead == False:
            return
    app.win = True


    
def onStep(app):
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
                app.zombieGenInterval  = random.randint(135, 200)
        
        #zombies walk
        for i in range(len(app.zombieList)):
            if not app.zombieList[i].dead:
                app.zombieList[i].walk(app)
            else:#if dead, stop walking, death animation
                pass
        
        #detect lose
        userLoseDetect(app)
        #move Guacodile
        moveGuacodileLine(app)
        guaHitSelf(app)
        guaHitWall(app)
        guaCollideZomb(app)
        if app.numZombKilled //5 > app.guaLength -1 :
            addOneGua(app)
        #check if time ends
        if app.timer >= app.finishTime:
            app.zombieFinished = True #stop generating new zombies
            winOrNot(app)
        #print wave message 
        
        

def onKeyPress(app, key):
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
    for i in range(len(app.guaList)):
        #decides which animation to draw based on direction
        if app.guaList[i].dir == 1:
            pass
        elif app.guaList[i].dir == 2:
            pass
        elif app.guaList[i].dir == 3:
            pass
        else:
            pass
        #temporary
        cellWidth, cellHeight = getCellSize(app)
        drawRect(app.guaList[i].x, app.guaList[i].y, cellWidth/2, cellHeight/2, 
                 fill = 'green', opacity = 40, align = 'center')
    pass

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
    if app.boardLeft + app.oneGuaLength/2 >= app.guaList[0].x or app.guaList[0].x >= (app.boardLeft + 
                                                                                      app.boardWidth - app.oneGuaLength/2):
        app.isGameOver = True
    if app.boardTop + app.oneGuaLength/2 >= app.guaList[0].y or app.guaList[0].y >= (app.boardTop + 
                                                                                      app.boardHeight - app.oneGuaLength/2):
        app.isGameOver = True
    pass

def guaHitSelf(app):
    for i in range(len(app.guaList)):
        
        if i>=8 and app.guaList[0].row == app.guaList[i].row and app.guaList[0].col == app.guaList[i].col:
            app.guaList = app.guaList[:i]
            break


def guaCollideZomb(app):
    for i in range(len(app.zombieList)):
        if app.guaList[0].row == app.zombieList[i].row and app.guaList[0].col == app.zombieList[i].col and (app.guaList[0],app.guaList[0].row, app.guaList[0].col) not in app.zombieList[i].biteList:
            app.zombieList[i].bitesLeft -= 1
            app.zombieList[i].biteList.append((app.guaList[0],app.guaList[0].row, app.guaList[0].col) )
            if app.zombieList[i].bitesLeft == 0:
                app.zombieList[i].dead = True
                app.numZombKilled += 1
    pass

#draw wave message

def drawWaveMessage(app):
    #font
    if app.waveTimeCount <= 50:
        message = "A Big Wave of Zombie is Approaching~" if app.numOfWaveLeft >1 else "Final Wave of Zombie!"
        drawLine(message, app.boardLeft + app.boardWidth/2, 
                 app.boardTop + app.boardHeight/2, fill = 'red')
        
#draw win/lose messages
def drawWinLoseMessage(app):
    if app.win:
        drawWin(app)
    if app.lose:
        drawLose(app)
#win message
def drawWin(app):
    pass
#losemessage
def drawLose(app):
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
        print(i, x, y)
        drawFlag(app, x, y)

#x, y is the bottom location of the stick of the flag
def drawFlag(app, x, y):
    drawLine(x, y, x, y-18, lineWidth = 2)
    drawPolygon(x, y-18, x, y-12, x+8, y-15, fill = 'red', borderWidth = 1, border = 'black')
    pass


def main():
    runApp()
main()
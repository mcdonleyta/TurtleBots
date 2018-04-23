import random
import turtle
import copy

turtle.speed(0)
turtle.delay(0)
turtle.tracer(10000, 0)

def mapVal(val, high, low, toHigh, toLow):
    ratio = (toHigh - toLow)/(high - low)
    return ((val-low)*ratio) + toLow

class Screen:
    width = turtle.window_width()
    height = turtle.window_height()

    mat = [] # a bitmap save of the drawSquare() canvas

    def resetTurtle(self, clear=False):  #Preserves image while reseting turtle stamps
        turtle.reset()      # this greatly decreases turtle's accumulated slow down
        for r in range(0, len(self.mat)):
            for c in range(0, len(self.mat[0])):
                if(self.mat[r][c] != 0):
                    if(clear == False or self.mat[r][c] == (0,0,0)):
                        turtle.color(self.mat[r][c])
                        self.drawSquare(r, c)
                    else:
                        self.mat[r][c] = 0
        turtle.update()
    
    def drawSquare(self, r, c):
        self.mat[r][c] = turtle.pencolor() #save pixel in bitmap
        
        blocksize = blockSize = self.width/cols
        scale = 25*1.4/rows
        x = mapVal(c, 0, cols, -self.width/2, self.width/2) + blockSize/2
        y = mapVal(r, 0, rows, -self.height/2, self.height/2) + blockSize/2

        turtle.resizemode("user")
        turtle.shape("square")
        turtle.shapesize(scale, scale, 1)
        turtle.penup()
        turtle.setpos(x, y)
        turtle.pendown()
        turtle.stamp()

    def draw(self, world):
        rows = world.rows
        cols = world.cols
        self.mat = copy.deepcopy(world.mat)
        
        ## Draw Screen
        for r in range(0, rows):
            for c in range(0, cols):
                if(self.mat[r][c] == 1):
                    turtle.color((0,0,0))
                    self.drawSquare(r, c)


class World:
    mat = []
    rows = -1
    cols = -1

    def emptySpace(self):
        r = random.randint(0, self.rows-1)
        c = random.randint(0, self.cols-1)
        while(self.mat[r][c] != 0):
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)

        return (r,c)
            

    def __init__(self, rows, cols, seed, density, coverage, growth):
        random.seed(seed)
        self.rows = rows
        self.cols = cols
        
        for j in range(0, rows):
            line = []
            for i in range(0, cols):
                #Theres a 5% chance of appending a 1 instead of a zero
                if( random.random() <= density ):
                    line.append(1)
                else:
                    line.append(0)
            self.mat.append(line)

        for i in range(0, coverage):        ## Run one pass of the algorithm
            cpyMat = copy.deepcopy(self.mat)
            rate = growth
            for r in range(0, rows):
                for c in range(0, cols):
                    if(self.mat[r][c] == 1):

                        if(c - 1 >= 0 and self.mat[r][c-1] == 0 and random.random() <= rate):
                            cpyMat[r][c-1] = 1
                        if(c + 1 < cols and self.mat[r][c+1] == 0 and random.random() <= rate):
                            cpyMat[r][c+1] = 1

                        if(r - 1 >= 0):
                            if(self.mat[r-1][c] == 0 and random.random() <= rate):
                                cpyMat[r-1][c] = 1
                            if(c - 1 >= 0 and self.mat[r-1][c-1] == 0 and random.random() <= rate):
                                cpyMat[r-1][c-1] = 1
                            if(c + 1 < cols and self.mat[r-1][c+1] == 0 and random.random() <= rate):
                                cpyMat[r-1][c+1] = 1
                                
                        if(r + 1 < rows):
                            if(self.mat[r+1][c] == 0 and random.random() <= rate):
                                cpyMat[r+1][c] = 1
                            if(c - 1 >= 0 and self.mat[r+1][c-1] == 0 and random.random() <= rate):
                                cpyMat[r+1][c-1] = 1
                            if(c + 1 < cols and self.mat[r+1][c+1] == 0 and random.random() <= rate):
                                cpyMat[r+1][c+1] = 1
                        

            self.mat = copy.deepcopy(cpyMat)


class Robot:
    lastR = 0 #pos
    lastC = 0
    r = 0
    c = 0

    gr = 0 #goal
    gc = 0

    deltaX = 0
    deltaY = 0

    score = 0

    dirRate = 0
    goalRate = 0

    def __init__(self, r, c, dr, gr):
        self.r = r
        self.c = c
        self.score = 0
        self.dirRate = dr
        self.goalRate = gr

    def move(self, world):
        #desire to change directions
        rows = world.rows
        cols = world.cols
        if(random.random() < self.dirRate):
            #desire to move toward goal
            if(random.random() < self.goalRate):
                goalX = self.gc - self.c
                goalY = self.gr - self.r
                if(goalX != 0): goalX = goalX // abs(goalX)
                if(goalY != 0): goalY = goalY // abs(goalY)
                
                self.deltaX = goalX
                self.deltaY = goalY
            else:
                self.deltaX = random.randint(-1, 1)
                self.deltaY = random.randint(-1, 1)

        if( self.r+self.deltaY>=0 and self.r+self.deltaY<rows  and self.c+self.deltaX>=0 and self.c+self.deltaX<cols and world.mat[self.r+self.deltaY][self.c+self.deltaX] == 0):
            self.c = self.c + self.deltaX
            self.r = self.r + self.deltaY
            

        self.lastR = self.r
        self.lastC = self.c
        self.score = self.score + 1

    def setPos(self, r, c):
        self.r = r
        self.c = c

    def setGoal(self, r, c):
        self.gr = r
        self.gc = c


def runTrials(bots, num, steps, world):
    pass

def selectBots(bots, num):
    #pick the best bots
    nextBots = []

    return nextBots

def breedBots(bots, num):
    nextBots = []

    return nextBots

## Initialize World
rows = 128
cols = 128
myMap = World(rows, cols, 1, 0.0025, 18, 0.1)

myView = Screen()
myView.draw(myMap)

pos = myMap.emptySpace()
gc = pos[1]
gr = pos[0]

pos = myMap.emptySpace()
random.seed(None)

turtle.color((1, 1, 0))
myView.drawSquare(gr,gc)
turtle.update()

## Create bots
bots = []
for i in range (0, 1000):
    bots.append(Robot(pos[0], pos[1], random.random(), random.random()))

## Run evolution
for generation in range(0, 20):
    print("=================[ Generation %d ]======================" % generation)
    for i in range (0, len(bots)):
      bots[i].setPos(pos[0],pos[1])
      bots[i].setGoal(gr, gc)
      bots[i].score = 0

    runTrials(bots, 10, 6000, myMap)

    nextBots = selectBots(bots, 50)
    print("Fittest Bots: ")
    for i in range(0, len(nextBots)):
        print("Bot%d[%f, %f] scored %d" % (i, nextBots[i].dirRate, nextBots[i].goalRate, nextBots[i].score))  

    bots = breedBots(nextBots, 20)

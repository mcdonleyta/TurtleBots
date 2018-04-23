import random
import turtle
import copy

def mapVal(val, high, low, toHigh, toLow):
    ratio = (toHigh - toLow)/(high - low)
    return ((val-low)*ratio) + toLow

class Screen:
    width = turtle.window_width()
    height = turtle.window_height()

    mat = [] # a bitmap save of the drawSqaure() canvas

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
        scale = 30*1.4/rows
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
    rot = 0
    

    gr = 0 #goal
    gc = 0

    deltaX = 0
    deltaY = 0

    score = 0

    genes = []

    def __init__(self, r, c, genes):
        self.r = r
        self.c = c
        self.score = 0
        self.wins = 0
        self.genes = genes

    def rotate(self, direction):
        if(direction == 1):
            self.turnRight()
        elif(direction == -1):
            self.turnLeft()

    def rotToward(self, dx, dy):
        if(self.deltaX != dx or self.deltaY != dy):
            saveDX = self.deltaX
            saveDY = self.deltaY
            right=0
            while(self.deltaX != dx or self.deltaY != dy):
                right += 1
                self.turnRight()

            if(right < 4):
                self.rot = 1
            elif(right > 4):
                self.rot = -1

            self.deltaX = saveDX
            self.deltaY = saveDY

    def turnRight(self):
        if(self.deltaX == 0):
            self.deltaX = self.deltaY 
        elif(self.deltaY == 0):
            self.deltaY = -1*self.deltaX
        elif(self.deltaY == self.deltaX):
            self.deltaY = 0
        else:
            self.deltaX = 0

    def turnLeft(self):
        if(self.deltaX == 0):
            self.deltaX = -1*self.deltaY 
        elif(self.deltaY == 0):
            self.deltaY = self.deltaX
        elif(self.deltaY == self.deltaX):
            self.deltaX = 0
        else:
            self.deltaY = 0

    def move(self, world):
        #desire to change directions
        rows = world.rows
        cols = world.cols
        dirRate = self.genes[0]
        goalUpdateRate = self.genes[1]
        rotateUpdateRate = self.genes[2]
        rotateRate = self.genes[3]
        randomRate = self.genes[4]
        
        if(random.random() < dirRate):
            #desire to move toward goal
            if(random.random() < goalUpdateRate):
                goalX = self.gc - self.c
                goalY = self.gr - self.r
                if(goalX != 0): goalX = goalX // abs(goalX)
                if(goalY != 0): goalY = goalY // abs(goalY)

                self.deltaX = goalX
                self.deltaY = goalY
            elif(random.random() < rotateUpdateRate):
                goalX = self.gc - self.c
                goalY = self.gr - self.r
                if(goalX != 0): goalX = goalX // abs(goalX)
                if(goalY != 0): goalY = goalY // abs(goalY)

                self.rotToward(goalX, goalY)
            elif(random.random() < randomRate):
                #self.rot *= -1                
                self.deltaX = random.randint(-1, 1)
                self.deltaY = random.randint(-1, 1)
                if(self.deltaX == 0 and self.deltaY == 0):
                    if(random.random() < 0.5):
                        if(random.random() < 0.5):
                            self.deltaX = 1
                        else:
                            self.deltaX = -1
                    else:
                        if(random.random() < 0.5):
                            self.deltaY = 1
                        else:
                            self.deltaY = -1
                
            if(random.random() < rotateRate):
                self.rotate(self.rot)


        if( self.r+self.deltaY>=0 and self.r+self.deltaY<rows  and self.c+self.deltaX>=0 and self.c+self.deltaX<cols and world.mat[self.r+self.deltaY][self.c+self.deltaX] == 0):
            self.c = self.c + self.deltaX
            self.r = self.r + self.deltaY
        else: 
            self.rotate(-1*self.rot) #Avoid obstacles by rotating the opposite direction
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


def runTrials(bots, num, steps, world, view):
    global turtle
    oldBots = copy.deepcopy(bots)
    for trials in range(0, num):
      print("Trial %d" % trials)
      for s in range(0, steps):
        if(s % (steps/20) == 0):
            print(".", end="")
            turtle.update()
        for i in range(0, len(bots)):
            bot = bots[i]
            if(bot.r != bot.gr or bot.c != bot.gc):
                if(i == 0 or i == 0):
                    turtle.color(bot.genes[0:3])
                    view.drawSquare(bot.r,bot.c)
                bot.move(world)
                if(i == 0 or i == 0):
                    turtle.color((1, 0, 1))
                    view.drawSquare(bot.r,bot.c)
                #turtle.update()

      print("")
      #Reset for next trial
      view.resetTurtle(clear=True)
      for r in range(0, len(bots)):
          if(bots[r].r == bots[r].gr and bots[r].c == bots[r].gc):
              bots[r].wins += 1
          else:
              #Penalty for bots that don't make the goal
              xdist = abs(bots[r].gc - bots[r].c)
              ydist = abs(bots[r].gr - bots[r].r)
              bots[r].score += (xdist+1)*(ydist+1)

          bots[r].setPos(oldBots[r].r, oldBots[r].c)
          bots[r].deltaX = -1
          bots[r].deltaY = 1
          bots[r].rot = 1

##          if(random.random() < .5):
##              bots[r].deltaX = 1
##          else:
##              bots[r].deltaX = -1
##          if(random.random() < .5):
##              bots[r].deltaY = 1
##          else:
##              bots[r].deltaY = -1
##          if(random.random() < .5):
##              bots[r].rot = 1
##          else:
##              bots[r].rot = -1
          

    

def selectBots(bots, num):
    #pick the best bots
    nextBots = []
    minI = 0
    for n in range(0, num):
         minFit = bots[0].score    
         for i in range(0, len(bots)):
            fit = bots[i].score
            if(fit < minFit):
                minFit = bots[i].score
                minI = i
         nextBots.append(copy.deepcopy(bots[minI]))
         bots.remove(bots[minI])
         minI=0

    return nextBots

def breedBots(bots, num):
    lenBots = len(bots)
    for m in range(0, num):
     for i in range(0, lenBots):
        j=i
        while(j == i):
            j = random.randint(0, lenBots-1)

        genesP1 = copy.deepcopy(bots[i].genes)
        genesP2 = copy.deepcopy(bots[j].genes)

        for g in range(0, len(genesP1)):
            if(random.random() < 0.05):    #Mutation
                genesP1[g] = random.random()
            if(random.random() < 0.05):
                genesP2[g] = random.random()

        if(random.random() < 0.5):
            split = random.randint(1, len(genesP1)-1)
            genes = genesP1[0:split]
            genes = genes + genesP2[split:len(genesP2)]
        else:
            split = random.randint(0, len(genesP1)-1)
            genes = genesP1[0:split]
            for g in range(split, len(genesP1)):
                genes.append((genesP1[g] + genesP2[g])/2)

        bots.append(Robot(0,0,genes)) #add child

    return bots

## Initialize World
rows = 128
cols = 128
myMap = World(rows, cols, 1, 0.0025, 18, 0.1)

turtle.speed(0)
turtle.delay(0)
turtle.ht()
turtle.tracer(0, 0)
myView = Screen()
myView.draw(myMap)

pos = myMap.emptySpace()
gc = pos[1]
gr = pos[0]

pos = myMap.emptySpace()
random.seed(None)

turtle.color((1, 1, 0))
myView.drawSquare(gr,gc)
turtle.color((0, 1, 1))
myView.drawSquare(pos[0],pos[1])
turtle.update()

## Create bots
bots = []
for i in range (0, 1000):
    #genes = [0.81, 0.15, 0.99, 0.02] #15000/20 @ 6000 steps
    #bots.append(Robot(pos[0], pos[1], genes))

    #genes = [0.4810, 0.1565, 0.9598, 0.0427] #9900/10 @ 6000 steps self.rot=-1
    #bots.append(Robot(pos[0], pos[1], genes))


    #genes = [0.7305, 0.2553, 0.9998, 0.4055]
    #bots.append(Robot(pos[0], pos[1], genes))
    #genes = [0.8099, 0.3231, 0.9999, 0.4397]
    #bots.append(Robot(pos[0], pos[1], genes))    
    #genes = [0.5684, 0.2010, 0.9999, 0.4110]
    #bots.append(Robot(pos[0], pos[1], genes))    
    #genes = [0.3201, 0.2346, 0.9765, 0.0254]
    #bots.append(Robot(pos[0], pos[1], genes))    
    #genes = [0.3243, 0.1632, 0.6869, 0.0978]
    #bots.append(Robot(pos[0], pos[1], genes))    
    #genes = [0.2912, 0.1718, 0.6445, 0.2391]
    #bots.append(Robot(pos[0], pos[1], genes))    
    #genes = [0.2181, 0.2264, 0.7690, 0.4489]
    #bots.append(Robot(pos[0], pos[1], genes))

    #genes = [.5, 0.65, 0.02, .9, 0.02] #15000/20 @ 6000 steps
    #bots.append(Robot(pos[0], pos[1], genes))

    genes = []
    for g in range(0, 5):
        genes.append(random.random())
    bots.append(Robot(pos[0], pos[1], genes))

## Run evolution
for generation in range(0, 20):
    print("=================[ Generation %d ]======================" % generation)
    for i in range (0, len(bots)):
      bots[i].setPos(pos[0],pos[1])
      bots[i].setGoal(gr, gc)
      bots[i].score = 0
      bots[i].wins = 0
      bots[i].deltaX = -1
      bots[i].deltaY = 1
      bots[i].rot = 1
##      if(random.random() < .5 and False):
##          bots[i].deltaX = 1
##      else:
##          bots[i].deltaX = -1
##      if(random.random() < .5 or True):
##          bots[i].deltaY = 1
##      else:
##          bots[i].deltaY = -1
##      if(random.random() < .5 or True):
##          bots[i].rot = 1
##      else:
##          bots[i].rot = -1


    runTrials(bots, 10, 6000, myMap, myView)
    myView.resetTurtle(clear=True)

    nextBots = selectBots(bots, 50)
    print("Fittest Bots: ")
    for i in range(0, len(nextBots)):
        print("Bot%d[" % i, end="")
        for g in nextBots[i].genes:
            print("%.4f, " % g, end="")
        if(nextBots[i].wins != 0):
            print("] scored %d/%d ~%.2f" % (nextBots[i].score, nextBots[i].wins, nextBots[i].score/nextBots[i].wins))
        else:
            print("] scored %d/%d" % (nextBots[i].score, nextBots[i].wins))
            

    bots = breedBots(nextBots, 20)

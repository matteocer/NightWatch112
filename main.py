"""
Main Aspects:

- Raycasting
    To simulate the 3D-like graphics, the game uses raycasting. It casts a ray 
    in every direction accoring to the players FOV and dAngle (in onAppStart). 
    The distance at that angle is found by fast voxel traversal. 
- Light Generation
    Every in game minute, determined by time.count(), a light has a chance of 
    spawning. If so, a random angle is generated in the player visible area. 
    This angle is then, is translated to the screen based on the players 
    direction vector and FOV.
- Hitbox (enable with h)
    If the player clicks on the light, determined by the hitbox, the light 
    despawns.
- Wave function
    To simulate wave-like motion, every step, the screen is moved up and down.

"""


from cmu_graphics import *
from cmu_cpcs_utils import testFunction, rounded

import math
import random

class Screen:
    def __init__(self, width, height):
        if not isinstance(width, int):
            raise TypeError(f'Invalid screen.width type: {width}')        
        if not isinstance(height, int):
            raise TypeError(f'Invalid screen.height type: {height}')
        self.width = width
        self.height = height
    
    def __repr__(self):
        return f'{self.width} x {self.height}'

class Map:
    def __init__(self):
        self.list = tuple([[1,1,1,1,1,1],
                           [1,0,0,0,0,1],
                           [1,0,0,0,0,1],
                           [1,0,0,0,0,1],
                           [1,0,0,0,0,1],
                           [1,0,0,0,0,1],
                           [1,0,0,0,0,1],
                           [1,0,0,0,0,1]])
        self.rows = len(self.list)
        self.cols = len(self.list[0])
        
class Vec2D:
    def __init__(self, x, y):
        if not (isinstance(x, float) or isinstance(x, int)):
            raise TypeError(f'Invalid Vec2D.x type: {x}')        
        if not (isinstance(y, float) or isinstance(y, int)):
            raise TypeError(f'Invalid Vec2D.y type: {y}')
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if not isinstance(other, Vec2D):
            return
        return Vec2D(other.x + self.x, other.y + self.y)

    def __sub__(self, other):
        if not isinstance(other, Vec2D):
            return
        return Vec2D(self.x - other.x, self.y - other.y)
        
    def __mul__(self, other):
        if not isinstance(other, float):
            return 
        return Vec2D(self.x * other, self.y * other)
        
    def __repr__(self):
        return f'{self.x}, {self.y}'
    
    def getMagnitude(self):
        return (self.x**2 + self.y**2) ** 0.5
    
    def getAngle(self):
        return math.degrees(math.atan2(self.y, self.x))
    
    def dotProduct(self, other):
        if not isinstance(other, Vec2D):
            return
        return (other.x * self.x + other.y * self.y)
    
    # Rotates the vector by angle in degrees counterclockwise 
    def rotate(self, angle):
        radians = math.radians(-angle)
        self.x = self.x * math.cos(radians) - self.y * math.sin(radians)
        self.y = self.x * math.sin(radians) + self.y * math.cos(radians)

class Vec3D(Vec2D):
    def __init__(self, x, y, z):
        if not isinstance(z, float):
            raise TypeError(f'Invalid Vec3D.z type: {z}')
        super.__init__(self, x, y)
        self.z = z
        
    def __eq__(self, other):
        if not isinstance(other, Vec3D):
            return
        return Vec3D(other.x + self.x, other.y + self.y, other.z + self.z)
        
    def getMagnitude(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5
    
    def dotProduct(self, other):
        if not isinstance(other, Vec3D):
            return
        return (other.x * self.x + other.y * self.y + other.z * self.z)
        
    def __repr__(self):
        return f'{self.x}, {self.y}, {self.z}'


    
class Size2D:
    def __init__(self, width, height):
        if not isinstance(width, float):
            raise TypeError(f'Invalid size.width type: {width}')
        if not isinstance(height, float):
            raise TypeError(f'Invalid size.height type: {height}')
        self.width = width
        self.height = height
    
    def __eq__(self, other):
        if not isinstance(other, Size2D):
            return
        return Size2D(other.width + self.width, other.height + self.height)
    
    def __repr__(self):
        return f'{self.width} x {self.height}'
    
class Size3D(Size2D):
    def __init__(self, width, height, depth):
        if not isinstance(depth, float):
            raise TypeError(f'Invalid size.depth type: {depth}')
        super.__init__(self, width, height)
        self.depth = depth
    
    def __eq__(self, other):
        if not isinstance(other, Size3D):
            return
        return Size3D(other.width + self.width, other.height + self.height, 
                      other.depth + self.depth)
        
    def __repr__(self):
        return f'{self.width} x {self.height} x {self.depth}'
        
class Camera:
    def __init__(self, length, position):
        if not isinstance(length, float):
            raise TypeError(f'Invalid Camera.length type: {length}')
        if not isinstance(position, Vec2D):
            raise TypeError(f'Invalid Camera.position type: {position}')
        self.length = length
        self.position = position

# Used to keep track of game time
class Time:
    def __init__(self, start, speed):
        if not isinstance(start, int):
            raise TypeError(f'Invalid Time.start type: {start}')
        if not isinstance(speed, int):
            raise TypeError(f'Invalid Time.speed type: {speed}')
        self.min = start
        self.speed = speed
        self.sec = 0
    
    def __repr__(self):
        min = str(self.min)
        sec = str(self.sec) if self.sec > 9 else f"0{self.sec}"
        return f"{min}.{sec}"
    
    # Returns true every minute
    def count(self):
        self.sec -= 100//self.speed
        if self.sec//100 != 0 and self.min != 0:
            self.min -= 1
            self.sec = 100//self.speed * (self.speed - 1)
            return True
        return False
            
    def isUp(self):
        if self.min == 0 and self.sec == 0:
            return True
        return False
    

def onAppStart(app):
    
    # Variables for map, screen, and projection
    app.screen = Screen(400, 400)
    app.map = Map() 
    app.camera = Vec2D(0.0, 0.66)
    app.playerPos = Vec2D(3.0, 5.0)
    app.playerDir = Vec2D(0.0, -1.0)
    app.playerFOV = math.degrees(2 * math.atan(app.camera.getMagnitude()
                                               /app.playerDir.getMagnitude()))
    app.startingAngle = 0
    app.dAngle = 0.2
    
    app.isHitbox = False
    
    # Colours
    app.skyColour = 'black'
    app.waterLevel = app.screen.height // 7 * 3

    
    # Wave variables
    app.cameraTilt = 30
    app.isTiltingUp = True
    app.waveAmount = 30
    app.dWave = 1

    reset(app)


def reset(app):
    # Game time variables
    app.gameTime = Time(100, 10)
    app.gameOver = False
    app.gameWon = False
    
    
    # Light variables
    resetLight(app)
    app.lightAngle = -90
    app.lightdRadius = 5
    app.lightEndRadius = 40 # Light Radius which ends the game
    app.lightSpawn = 0.1    # Value is from 0.01 to 1
    app.lightPos = 0
    app.lightdPos = 2
    
    # Hitbox Variables
    app.hitBox = None
    app.hitBoxSize = app.lightEndRadius * 2
    
    app.playerDir = Vec2D(0.0, -1.0)
    
def resetLight(app):
    app.lightAngle = None
    app.lightRadius = 8
    app.lightPos = 0
   
def redrawAll(app):
    rayCast(app, app.map.list)
    drawLight(app)
    drawTime(app)
    # print(f"pos: ({app.playerPos}), dir: ({app.playerDir})")
    drawCircle(app.screen.width //2, 340, 50)
    drawRect(app.screen.width //2 - 25, 320, 50, 200)
    
    if app.isHitbox:
        drawHitBox(app) # for debugging
    if app.gameOver:
        if app.gameWon:
            winner(app)
        else:
            gameOver(app)
    
def onKeyPress(app, key):
    moveFactor = 0.1
    degrees = 10
    if (key == 'right' or key == 'd') and inBounds('right', app.playerDir):
        app.playerDir.rotate(-degrees)
    # Hardcoded bounds correction
    elif (key == 'left' or key == 'a') and inBounds('left', app.playerDir):
        app.playerDir.rotate(degrees)
    
    if app.gameOver and key == 'r':
        reset(app)
    
    # Keys for debugging
    if key == 'g':
        app.gameOver = True
        app.gameTime = Time(0,5)
    if key == 'w':
        app.gameOver = True
        app.gameWon = True
        app.gameTime = Time(0,5)
    if key == 'h':
        app.isHitbox = not app.isHitbox
 
# Function to determine if the angle change will go off the map
def inBounds(key, direction):
    if key == 'left':
        # print('left')
        # print(direction.getAngle()) 
        return direction.getAngle() > -113
    if key == 'right':
        # print('right')
        # print(direction.getAngle())
        return direction.getAngle() < -70
    
    
    
def onStep(app):
    
    
    
    if not app.gameTime.isUp():
        
        print(app.gameTime, app.gameTime.sec)
        if app.lightRadius >= app.lightEndRadius:
            app.gameOver = True
            app.gameTime = Time(0, 10)
            return
        
        wave(app)
        if app.gameTime.count():
            changeLight(app)
            fixBoxPosition(app)
            
        # print(app.gameTime)
    elif not app.gameOver or app.gameWon:
        app.gameWon = True
        app.gameOver = True

def fixBoxPosition(app):
    playerAngle = app.playerDir.getAngle()
    leftAngle = playerAngle - app.playerFOV/2
    rightAngle = playerAngle + app.playerFOV/2
    
    if app.lightAngle != None and leftAngle <= app.lightAngle <= rightAngle:
        boxY = app.waterLevel + app.lightPos
        boxX = ((app.lightAngle - leftAngle) / 
                (app.playerFOV) * app.screen.width)
        app.hitBox = Vec2D(boxX, boxY)
    else:
        app.hitBox = None
 



def onMousePress(app, mouseX, mouseY):
    if not app.gameOver:
        # Detects if the hitbox is hit
        if app.hitBox != None:
            checkHitBox(app, mouseX, mouseY)

    
    
# Sees if the mouse position is in the hitbox
def checkHitBox(app, mouseX, mouseY):
    left = app.hitBox.x - app.hitBoxSize//2
    right = app.hitBox.x + app.hitBoxSize//2
    
    top = app.hitBox.y - app.hitBoxSize//2
    bottom = app.hitBox.y + app.hitBoxSize//2
    if left <= mouseX <= right and top <= mouseY <= bottom:
        resetLight(app)
        app.hitBox = None
        

# Increases radius is still there else calls spawn light
def changeLight(app):
    if app.lightAngle != None:
        app.lightRadius += app.lightdRadius
        app.lightPos += app.lightdPos
    else:
        spawnLight(app)
    
# Has the possiblility to spawn a light every second dependent on app.lightSpawn
def spawnLight(app):
    # determines if boat spawns
    lightSpawnInt = random.randint(1, 100)
    if app.lightSpawn * 100 > lightSpawnInt:
        return
    
    # determines the angle
    lightAngle = random.randint(30, 150)
    
    app.lightAngle = lightAngle * -1


# Makes the screen move to simulate a wave according to app.waveAmount
def wave(app):
    magnitude = app.waveAmount
    if not (isinstance(magnitude, int) and magnitude % 5 == 0):
        raise TypeError(f'Invalid magnitude type: {magnitude}')
    if app.cameraTilt > magnitude or app.cameraTilt < 5:
        app.isTiltingUp = not app.isTiltingUp
    if app.isTiltingUp:
        app.cameraTilt += app.dWave
    else:
        app.cameraTilt -= app.dWave
 
def drawLight(app):
    startingAngle = app.playerDir.getAngle() - app.playerFOV/2
    endingAngle = app.playerDir.getAngle() + app.playerFOV/2
    for ray in range(int(app.playerFOV / app.dAngle)):
        angle = startingAngle + ray * app.dAngle
        if int(angle) == app.lightAngle:
            lightX = (abs(startingAngle - angle) / (endingAngle - startingAngle) 
                      * app.screen.width)
            drawCircle(lightX, app.waterLevel + app.lightPos, 
                       app.lightRadius, fill='yellow')
        
# Wrapper function which goes creates and calls a function to cast the ray    
def rayCast(app, grid2D):
    startingAngle = app.playerDir.getAngle() - app.playerFOV/2
    for ray in range(int(app.playerFOV / app.dAngle)):
        angle = startingAngle + ray * app.dAngle
        fastCastRay(app, grid2D, angle)
    
    
# casts a ray and steps through it at a regular interval (stepValue)
def slowCastRay(app, grid2D, angle):
    # real value of positiond
    currX = app.playerPos.x
    currY = app.playerPos.y
    
    # pixel ray is in aka rounded value
    mapX = int(currX)
    mapY = int(currY)
    
    rayDirX = math.cos(math.radians(angle))
    rayDirY = math.sin(math.radians(angle))
    
    stepValue = 0.5
    
    while (0 <= mapX < app.map.cols and 0 <= mapY < app.map.rows and 
           (grid2D[mapY][mapX] == 0 or grid2D[mapY][mapX] == None)):
        currX += rayDirX * stepValue
        currY += rayDirY * stepValue
        
        mapX = int(currX)
        mapY = int(currY)
    
    # print(currX)
    # print(currY)
    dx = currX - app.playerPos.x
    dy = currY - app.playerPos.y
    distance = (dx**2 + dy**2) ** 0.5
    
    # Remove fisheye effect
    # distance *= math.cos(math.radians(angle - app.playerDir.getAngle()))
    if distance < 0:
        distance = None
    # print(f"angle: {angle}, distance:{distance}")
    drawWall(app, distance, angle)



# Draws the walls and 
def drawWall(app, distance, angle):
    startingAngle = app.playerDir.getAngle() - app.playerFOV/2
    dAngle = abs(startingAngle - angle)
    # print(f"dAngle: {dAngle}")
    # print(f"distance: {distance}")
    # this is the height of the wall/windows
    modelWallHeight = 900
    
    wallWidth = math.ceil(app.dAngle/app.playerFOV * app.screen.width)
    viewWallHeight = 0 if distance == None else int(modelWallHeight/distance)
    
    wallTop = int(app.screen.height/2 - viewWallHeight/2) + app.cameraTilt
    wallLeft = dAngle/app.playerFOV * app.screen.width
    
    if wallWidth != 0 and viewWallHeight != 0:
        isLight = False
        if int(angle) == app.lightAngle:
            isLight = True
        drawSector(app, wallLeft, wallTop, wallWidth, viewWallHeight, isLight)

def drawSector(app, left, top, width, height, isLight):
    waterTop = app.waterLevel
    waterWidth = 40
    windowBoarderWidth = 30
    
    skyTop = top + windowBoarderWidth
    skyHeight = waterTop - top - windowBoarderWidth
    
    waterHeight = (top + windowBoarderWidth + height - 2 * windowBoarderWidth 
                   - waterTop)
    
    
    if (top > 0):
        # drawRect(left, 0, width, top, fill='gray')
        # drawRect(left, top, width, windowBoarderWidth, fill='lightgray')
        drawRect(left, 0, width, top + windowBoarderWidth + skyHeight, 
                 fill=app.skyColour)
        drawRect(left, waterTop, width, waterHeight, fill='blue')
        drawRect(left, waterHeight + waterTop, width, windowBoarderWidth, 
                 fill='darkgray')
        drawRect(left, top + height, width, top, fill='brown')
    
# slowCastRay optimized to use DDA instead of stepping courtesy of mostly Chat 
# based on this paper:
# Amanatides, John & Woo, Andrew. (1987). A Fast Voxel Traversal Algorithm for 
# Ray Tracing.
def fastCastRay(app, grid2D, angle):
    posX = app.playerPos.x
    posY = app.playerPos.y
    
    rayDirX = math.cos(math.radians(angle))
    rayDirY = math.sin(math.radians(angle))
    
    mapX = int(posX)
    mapY = int(posY)
    
    deltaDistX = abs(1 / rayDirX) if rayDirX != 0 else 1e30  # A very big number to 
    deltaDistY = abs(1 / rayDirY) if rayDirY != 0 else 1e30
    
    if rayDirX < 0:
        stepX = -1
        sideDistX = (posX - mapX) * deltaDistX
    else:
        stepX = 1
        sideDistX = (mapX + 1 - posX) * deltaDistX
    
    if rayDirY < 0:
        stepY = -1
        sideDistY = (posY - mapY) * deltaDistY
    else:
        stepX = 1
        sideDistY = (mapY + 1 - posY) * deltaDistY
        
    side = 0
    
    while (0 <= mapX < app.map.cols and 0 <= mapY < app.map.rows and 
           (grid2D[mapY][mapX] == 0 or grid2D[mapY][mapX] == None)):
        if sideDistX < sideDistY:
            sideDistX += deltaDistX
            mapX += stepX
            side = 0
        else:
            sideDistY += deltaDistY
            mapY += stepY
            side = 1
    
    if side == 0:
        distance = sideDistX - deltaDistX
    else:
        distance = sideDistY - deltaDistY
        
    drawWall(app, distance, angle)
    
def drawTime(app):
    Left = app.screen.width//6 * 4
    Top = app.screen.height//12
    drawLabel(f"Time Remaining: {app.gameTime}", Left, Top, size=16, fill='red')
    
# Draws the hitBox
def drawHitBox(app):
    if app.hitBox == None:
        return 
    drawRect(app.hitBox.x - app.hitBoxSize//2, app.hitBox.y - app.hitBoxSize//2, 
             app.hitBoxSize, app.hitBoxSize, border='red', fill=None)

def gameOver(app):
    drawLabel('GAME OVER', app.screen.width//2, app.screen.height//2 - 30, 
              bold=True, size=40, fill='red')
    drawLabel('Press \'r\' to restart', app.screen.width//2, 
              app.screen.height//2 + 10, fill='red')
    
    
def winner(app):
    drawLabel('You WIN!', app.screen.width//2, app.screen.height//2 - 30,   
              bold=True, size=40, fill='green')
    drawLabel('Press \'r\' to restart', app.screen.width//2, 
              app.screen.height//2 + 10, fill='green')
    
def main():
    runApp()
    
main()

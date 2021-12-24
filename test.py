import numpy as np
import sys
import enum
class Id(enum.Enum):
    A = np.uint8(25)
    B = np.uint8(30)
    C = np.uint8(35)
    D = np.uint8(40)

print(sys.getrecursionlimit())
sys.setrecursionlimit(10**6)
print(sys.getrecursionlimit())

class unit:
    def __init__(self, x, y, id,  stepcost):
        self.x = x
        self.y = y
        self.id = id
        self.stepcost = stepcost
        self.hallway = False

    def copy(self):
        tmp = unit(self.x, self.y, self.id, self.stepcost)
        tmp.hallway = self.hallway
        return tmp
    

def GetData(dataset):
    data = []
    with open(dataset, 'r') as f:
        data = f.readlines()

    
    # strip the new line character
    #on x=-Id.A0..Id.A6,y=-Id.B6..17,z=-Id.C7..7

    grid=np.zeros(shape=(len(data),len(data[0])), dtype=np.uint8)
    list_of_units = []
    for y in range(len(data)):
        for x in range(len(data[y])):
            if data[y][x] == '#':
                grid[y][x] = 1
            elif data[y][x] == '.':
                grid[y][x] = 0
            elif data[y][x] == ',':
                grid[y][x] = 2
            elif data[y][x] == 'A':
                grid[y][x] = Id.A.value
            elif data[y][x] == 'B':
                grid[y][x] = Id.B.value
            elif data[y][x] == 'C':
                grid[y][x] = Id.C.value
            elif data[y][x] == 'D':
                grid[y][x] = Id.D.value
            else:
                grid[y][x] = 0
    return grid

gridexpected = GetData('./data/aoc23_expected.txt')
gridconfig = GetData('./data/aoc23_config.txt')
def ExpectedConfiguration():
    return gridexpected

def TestConfiguration():
    return gridconfig

def Scan():
    return np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                    [1,0,0,0,0,0,0,0,0,0,0,0,1,0],
                    [1,1,1,0,1,0,1,0,1,0,1,1,1,0],
                    [0,0,1,0,1,0,1,0,1,0,1,0,0,0],
                    [0,0,1,1,1,1,1,1,1,1,1,0,0,0]], dtype=np.uint8)

def GetUnits(grid):
    units = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            #print(grid[x][y], x, y)
            if grid[x][y] == Id.A.value:
                print("A", x, y)
                units.append(unit(x, y,Id.A,1))
            elif grid[x][y] == Id.B.value:
                print("B", x, y)
                units.append(unit(x, y,Id.B,10))
            elif grid[x][y] == Id.C.value:
                print("C", x, y)
                units.append(unit(x, y,Id.C,100))
            elif grid[x][y]  == Id.D.value:
                print("D", x, y)
                units.append(unit(x, y,Id.D,1000))
    return units
# true if path is blocked
def CheckPathNotBlocked(grid, start, move, scanmap):
    
    #print(start[0],start[1], scanmap[start[0]][start[1]])
    
    if grid[start[0]][start[1]] >= Id.A.value or grid[start[0]][start[1]] == 1:
        #print("collided")
        return  False, 0
    if scanmap[start[0]][start[1]]== 1:
        #print("passed")
        return  False, 0
    if start[0] == move[0] and start[1] == move[1]:
        #print("reached")
        return True, 0
    scanmap[start[0],start[1]] = 1
    #print(scanmap)
    return BreathPath(grid, start, move, scanmap)

def BreathPath(grid, start, move, scanmap):
    check , value = CheckPathNotBlocked(grid, (start[0]+1, start[1]), move, scanmap)
    if check:
        return True, value + 1
    check , value= CheckPathNotBlocked(grid, (start[0]-1, start[1]), move, scanmap)
    if check:
        return True,value + 1
    check , value = CheckPathNotBlocked(grid, (start[0], start[1]+1), move, scanmap)
    if check:
        return True,value + 1
    check , value = CheckPathNotBlocked(grid, (start[0], start[1]-1), move, scanmap)
    if check:
        return True,value + 1
    return False, 0

        

def GenerateMoves(unit, grid):
    config = TestConfiguration()
    # check if is in hallway 
    moves = []
    if config[unit.x][unit.y] == 0:
        unit.hallway = True
        #print(f"in Halway {unit.x},{unit.y}")
        for x in range(len(config)-1,-1,-1):
            for y in range(len(config[x])):
                if config[x][y] == unit.id.value:
                    check,value = BreathPath(grid, [unit.x, unit.y], [x,y], Scan())
                    #print(f"{unit.id} {unit.x},{unit.y} {x},{y} {check} {value}")
                    if check:
                        return [[x,y, value * unit.stepcost]]
                
    # Move into the hallway
    else:
        if(unit.hallway == False):
            for y in range(len(config[1])):
                if grid[1][y] == 0 and config[1][y] == 0:
                    check,value = BreathPath(grid, [unit.x, unit.y], [1,y], Scan())
                    #print(f'endvalue {value}')
                    if check:
                        moves.append([1,y, value * unit.stepcost])
                    
    return moves


def MoveUntilGrid(startgrid, expected):
    griddic = {}
    griddic[0] = [[GetUnits(startgrid),startgrid]]
    i = -1
    foundValue = 0
    foundValues = {}
    foundValues[hash(str(startgrid))] = 0
    while len(griddic) >0:
        i += 1
        if foundValue != 0 and i > foundValue:
            break
        if i in griddic:
            print(f'stepcost {i} found: {foundValue}')
            gridStates = griddic[i]
            del griddic[i]
            while len(gridStates) > 0:
                stepcost = i
                units,grid = gridStates.pop(0)
                #print(units)
                for j in range(len(units)):
                    unit = units[j]
                    moves = GenerateMoves(unit,grid)
                    #print(moves)
                    if moves != None:
                        for move in moves:
                            newgrid = grid.copy()
                            newgrid [unit.x][unit.y] = 0
                            newgrid [move[0], move[1]] = unit.id.value
                            newUnits = [u.copy() for u in units]
                            # get unit on this position
                            
                            newUnits[j].x = move[0]
                            newUnits[j].y = move[1]
                            newstepcost = move[2] + stepcost
                            #print(newstepcost, move[2], stepcost)
                            gridhash=hash(str(newgrid))

                            #print(f'grid {gridhash}')
                            #print(newgrid)
                            #print(newstepcost)
                            #print(unit.stepcost)
                            if gridhash == expected:
                                if foundValue != 0 and newstepcost > foundValue:
                                        continue
                                foundValue=newstepcost

                            if newstepcost not in griddic: griddic[newstepcost] =  []
                            if gridhash not in foundValues:
                                #print(f'new grid')
                                if foundValue != 0 and newstepcost > foundValue:
                                        continue
                                foundValues[gridhash] = newstepcost
                                griddic[newstepcost].append([newUnits,newgrid])
                                
                            else:
                                if foundValues[gridhash] > newstepcost :
                                    if foundValue != 0 and newstepcost > foundValue:
                                        continue
                                    #print(f'old grid')
                                    foundValues[gridhash] = newstepcost
                                    griddic[newstepcost].append([newUnits,newgrid])
                               
    return foundValue
                            

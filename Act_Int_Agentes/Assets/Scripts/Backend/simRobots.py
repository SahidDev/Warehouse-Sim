from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.a_star import AStarFinder
from mesa.visualization.UserParam import UserSettableParameter
from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule
import random

w = 12
h = 12

def initMaxtrix(n, m):

    matrix = [[1 for i in range(n)] for j in range(m)]

    for i in range(n):
        matrix[0][i] = 0
        matrix[m - 1][i] = 0

    for i in range(m):
        matrix[i][0] = 0
        matrix[i][n - 1] = 0

    return matrix


class Robot(Agent):
    NORMAL = 0
    LOADED = 1

    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.condition = self.NORMAL
        self.box = None
        self.rack = None
        self.roaming = False
        self.endX = 1
        self.endY = 1
        self.steps = 0

    def step(self):
        #print(self.unique_id, ": ",self.condition )

        if(self.box == None):
          if(self.condition != self.LOADED and len(self.model.boxes) > 0):
            i = random.randint(0, len(self.model.boxes) - 1)
            self.box = self.model.boxes.pop(i)
        
        else:
          if(self.pos == self.box.pos):
            self.condition = self.LOADED
            self.box = None
            agents = self.model.grid.get_cell_list_contents(self.pos)
            for agent in agents:
              if (type(agent) == Box):
                  
                  self.model.grid.remove_agent(agent)
                  agent.pos = (0,0)
                  #self.model.schedule.remove(agent)
                  agents.remove(agent)
                  self.model.matrix[self.pos[1]][self.pos[0]] == 1

        if (self.roaming == False and self.box != None):
            self.endX = self.box.pos[0]
            self.endY = self.box.pos[1]
            self.roaming = True

        if (self.rack==None):
          if(len(self.model.racks) != 0):
            i = random.randint(0, len(self.model.racks) - 1)
            self.rack = self.model.racks[i]            

        if (self.condition == self.LOADED and self.rack != None):
          self.endX = self.rack.pos[0]
          self.endY = self.rack.pos[1]
          self.roaming = True

        if (self.condition == self.LOADED):
          for neighbor in self.model.grid.neighbor_iter(self.pos, moore=True):
            if (type(neighbor) == Rack and self.condition == self.LOADED):
              if(neighbor == self.rack):
                if(neighbor.boxAmount < 5):
                  self.model.usedBoxes += 1
                  self.condition = self.NORMAL
                  neighbor.addBox()
                
                self.endX = self.pos[0]
                self.endY = self.pos[1]
                self.rack = None

        pathGrid = PathGrid(matrix=self.model.matrix)

        start = pathGrid.node(self.pos[0], self.pos[1])
        end = pathGrid.node(self.endX, self.endY)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, pathGrid)

        if (len(path) > 1):
            self.steps += 1
            next_move = path[1]
            self.model.grid.move_agent(self, next_move)
            #self.model.matrix[self.pos[1]][self.pos[0]] = 0
            
        else:
            self.roaming = False
            pathGrid.cleanup()

        return


class Rack(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.boxAmount = 0

    def step(self):
        #print(self.unique_id)
        return

    def addBox(self):
        self.boxAmount += 1


class Box(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos

    def step(self):
        #print(self.unique_id)
        return


class Wall(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos


class Warehouse(Model):
    def __init__(self):
        super().__init__()
        initRobots = 5
        boxAmount = 20
        self.initBoxes = 20
        rackAmount = 4
        self.initRacks = 4
        self.steps = 0
        self.maxCapRacks = 0
        self.usedBoxes = 0
        self.width = w
        self.height = h
        self.racks = []
        self.robots = []
        self.boxes = []
        self.grid = MultiGrid(self.width, self.height, torus=False)
        self.matrix = initMaxtrix(self.width, self.height)
        self.schedule = RandomActivation(self)

        for _, x, y in self.grid.coord_iter():
            if self.matrix[y][x] == 0:
                wall = Wall(self, (x, y))
                self.grid.place_agent(wall, wall.pos)
                self.schedule.add(wall)

        tries = 0
        while (rackAmount > 0):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)

            target = self.grid.get_cell_list_contents((x, y))

            if (len(target) == 0):
                rack = Rack(self, (x, y))
                self.grid.place_agent(rack, rack.pos)
                self.schedule.add(rack)
                self.racks.append(rack)
                self.matrix[y][x] == 0
                rackAmount -= 1
            else:
                tries += 1

            if (tries >= 100):
                rackAmount = 0

        tries = 0
        while (boxAmount > 0):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)

            target = self.grid.get_cell_list_contents((x, y))

            if (len(target) == 0):
                box = Box(self, (x, y))
                self.grid.place_agent(box, box.pos)
                self.schedule.add(box)
                self.boxes.append(box)
                self.matrix[y][x] == 0
                boxAmount -= 1
            else:
                tries += 1

            if (tries >= 100):
                boxAmount = 0
        print(len(self.boxes))
        tries = 0
        while (initRobots > 0):

            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)

            target = self.grid.get_cell_list_contents((x, y))

            if (len(target) == 0):
                robot = Robot(self, (x, y))
                self.grid.place_agent(robot, robot.pos)
                self.schedule.add(robot)
                self.robots.append(robot)
                #self.matrix[y][x] == 1
                initRobots -= 1
            else:
                tries += 1

            if (tries >= 100):
                boxAmount = 0

    def step(self):
        self.schedule.step()
        self.steps+=1

        for rack in self.racks:
          if(rack.boxAmount >= 5):
            self.maxCapRacks+=1
            self.racks.remove(rack)

        #print(self.usedBoxes)
        #print(self.maxCapRacks)
        if(self.usedBoxes == self.initBoxes or self.maxCapRacks == self.initRacks):
          print("Tiempo para recoger cajas: ",self.steps)
          for robot in self.robots:
            print("Robot con id ", robot.unique_id, " dio ", robot.steps," pasos")
          self.running = False

        #print(len(self.boxes))
        #print(len(self.robots))


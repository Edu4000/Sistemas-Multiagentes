#uwu?
import mesa
import random
import numpy as np
import math

def get_mission(pos, boxes):
    dist = 100
    assigned_box = None
    for box in boxes:
        manhattan_dist = abs(pos[0] - box.pos[0]) + abs(pos[1] - box.pos[1])
        if dist > manhattan_dist:
            dist = manhattan_dist
            assigned_box = box
    boxes.remove(assigned_box)
    return assigned_box

def get_distance(p, q):
    """ Returns euclidean distance from A to B"""
    return math.sqrt((q[1] - p[1])**2 + (q[0] - p[0])**2)

class Almacen (mesa.Model):
    def __init__(self, width, height, num_boxes) -> None:
        
        # Model Variables Shared Between Agents
        self.shared_map = [[[0] * height] * width]
        self.boxes = []
        self.dropoff_pos = (0,0)
        self.end_pos = (width-1, height-1)

        # Creating Grid        
        self.grid = mesa.space.MultiGrid(width, height, False)

        # Creating Scheduler
        self.schedule = mesa.time.BaseScheduler(self)

        # Inserting Agents
        for i in range(num_boxes):
            box = Box(f"box_{i}", self)
            pos = (random.randint(0, width-1), random.randint(0, width-1))
            while (len(self.grid.get_cell_list_contents(pos)) == 1 or pos[0] == 0 or pos[1] == 0):
                pos = (random.randint(0, width-1), random.randint(0, width-1))
            self.grid.place_agent(box, pos)
            self.boxes.append(box)

        for i in range(5):
            robot = Robot(f"robot_{i}", self)
            pos = (random.randint(0, width-1), random.randint(0, width-1))
            while (len(self.grid.get_cell_list_contents(pos)) == 1):
                pos = (random.randint(0, width-1), random.randint(0, width-1))
            self.grid.place_agent(robot, pos)
            self.schedule.add(robot)

    def step(self):
        self.schedule.step()

class Explorer(mesa.Agent):
    def __init__(self, unique_id: int, model: Almacen) -> None:
        super().__init__(unique_id, model)
        self.vision = 10
        
    def announce(self):
        pass

    def step(self):
        cells = []
        # Search for objects inside the range of vision
        for i in range(self.vision):
            x, y = self.pos

            cells.append((x+i,y))
            cells.append((x+i,y+i))
            cells.append((x-i, y-i))

        for cell in cells:
            try:
                searching = self.model.grid.get_cells_list_contents(cell)

                if len(searching) > 0:
                    for agent in searching:
                        if (isinstance(agent, Stand)):
                            self.model.stands.append(agent)
                        if (isinstance(agent, Box)):
                            self.model.boxes.append(agent)
            except:
                continue

        # Move
        pass

class Box (mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.can_be_grabbed = True

class Robot (mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.box = None
        self.assigned = None
        self.dir = True

    def get_route(self):
        if (isinstance(self.box, Box)):
            pass
        else:
            pass

    def grab(self, agent):
        agent.can_be_grabbed = False
        self.box = agent
        self.assigned = None

    def drop(self):
        self.model.grid.move_agent(self.box, self.model.dropoff_pos)
        if (len(self.model.grid.get_cell_list_contents(self.model.dropoff_pos)) == 5):
            self.model.dropoff_pos = (self.model.dropoff_pos[0], self.model.dropoff_pos[1] + 1)
        self.box = None

    def step(self):
        objective = self.pos

        if (self.assigned == None and self.box == None):
            if (len(self.model.boxes) == 0):
                # Move towards end position
                objective = self.model.end_pos
            else:
                # Get a box assignation and moves towards it
                self.assigned = get_mission(self.pos, self.model.boxes)
                objective = self.assigned.pos
                if (abs(self.pos[0] - objective[0]) + abs(self.pos[1] - objective[1]) == 1):
                    box = self.model.grid.get_cell_list_contents(objective)
                    self.grab(box[0])
                    return
        else:
            if (self.box == None):
                # Move towards assigned box
                objective = self.assigned.pos
                if (abs(self.pos[0] - objective[0]) + abs(self.pos[1] - objective[1]) == 1):
                    box = self.model.grid.get_cell_list_contents(objective)
                    self.grab(box[0])
                    return
            else:
                # Move towards dropoff location
                objective = self.model.dropoff_pos
                if (abs(self.pos[0] - objective[0]) + abs(self.pos[1] - objective[1]) == 1):
                    self.drop()
                    return

        moves = self.model.grid.get_neighborhood(self.pos, False, False, 1)

        if (objective[0] - self.pos[0] > 0):
            diff_x = 1
        elif (objective[0] - self.pos[0] < 0):
            diff_x = -1
        else:
            diff_x = 0

        if (diff_x != 0):
            next_pos = (self.pos[0] + int(diff_x), self.pos[1])
            agents = self.model.grid.get_cell_list_contents(next_pos)
            if (len(agents) == 0):
                self.model.grid.move_agent(self, next_pos)
                try:
                    self.model.grid.move_agent(self.box, next_pos)
                except:
                    pass
                return
            else:
                try:
                    moves.remove(next_pos)
                except:
                    pass

        if (objective[1] - self.pos[1] > 0):
            diff_y = 1
        elif (objective[1] - self.pos[1] < 0):
            diff_y = -1
        else:
            diff_y = 0

        if (diff_y != 0):
            next_pos = (self.pos[0], self.pos[1] + int(diff_y))
            agents = self.model.grid.get_cell_list_contents(next_pos)
            if (len(agents) == 0):
                self.model.grid.move_agent(self, next_pos)
                try:
                    self.model.grid.move_agent(self.box, next_pos)
                except:
                    pass
                return
            else:
                try:
                    moves.remove(next_pos)
                except:
                    pass

        if (not(len(self.model.boxes) == 0 and self.box == None and self.assigned == None)):
            if (len(moves) == 0):
                pass
            elif (len(moves) == 1):
                self.model.grid.move_agent(self, moves[0])
                try:
                    self.model.grid.move_agent(self.box, moves[0])
                except:
                    pass
            elif (get_distance(objective, moves[0]) < get_distance(objective, moves[1])):
                self.model.grid.move_agent(self, moves[0])
                try:
                    self.model.grid.move_agent(self.box, moves[0])
                except:
                    pass
            else:
                self.model.grid.move_agent(self, moves[1])
                try:
                    self.model.grid.move_agent(self.box, moves[1])
                except:
                    pass

class Stand(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type == "stand"
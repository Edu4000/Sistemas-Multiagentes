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
        self.ordered_boxes = []
        self.num_boxes = num_boxes

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
        self.model.ordered_boxes.append(self.box)
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
                self.dir = False
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

        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )

        depurated_steps = []

        for steps in possible_steps:
            searching = self.model.grid.get_cell_list_contents([steps])
            cannot_use_step = False

            if len(searching) > 0:
                print(f":::--Agent found in {steps}")
                for agent in searching:
                    if len(self.model.ordered_boxes) != self.model.num_boxes:
                        if isinstance(agent, Robot) or isinstance(agent, Box):
                            cannot_use_step = True
                        else:
                            print("Can use this step!")
                            break
                            # cannot move and exit
            if cannot_use_step:
                continue
            else:
                depurated_steps.append(steps)

        if (len(depurated_steps) == 0):
            return

        min = 2000
        best = []

        for opts in depurated_steps:
            x_i, y_i = opts
            x_j, y_j = objective

            new_point = [x_i, y_i]
            objective = [x_j, y_j]

            aux = get_distance(new_point, objective)

            if (aux < min):
                best = new_point
                min = aux

        print(f"The best possible distance is {min}")
        self.model.grid.move_agent(self, tuple(e for e in best))

        try:
            self.model.grid.move_agent(self.box, tuple(e for e in best))
        except:
            pass


class Stand(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type == "stand"

#uwu?
import mesa
import random
import numpy as np

class Almacen (mesa.Model):
    def __init__(self, width, height, num_boxes) -> None:
        
        # Model Variables Shared Between Agents
        self.shared_map = [[[0] * height] * width]
        self.assigned = []
        self.boxes = []
        self.stands = []

        # Creating Grid        
        self.grid = mesa.space.MultiGrid(width, height, False)

        # Creating Scheduler
        self.schedule = mesa.time.BaseScheduler(self)

        # Inserting Agents
        for i in range(num_boxes):
            box = Box(f"box_{i}", self)
            pos = (random.randint(0, width-1), random.randint(0, width-1))
            while (len(self.grid.get_cell_list_contents(pos)) == 1):
                pos = (random.randint(0, width-1), random.randint(0, width-1))
            self.grid.place_agent(box, pos)

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
        self.goal = None

    def get_route(self):
        if (isinstance(self.box, Box)):
            pass
        else:
            pass

    # Checar a que lugares puede moverse
    # Elegir nuevo lugar y comunicarlo
    # Si hay empate y se pierde el lugar, elegir uno nuevo
    # Moverse

    def grab(self, agent):
        agent.can_be_grabbed = False
        self.box = agent

    def drop(self, agent):
        self.model.grid.move_agent()
        self.box = None
    
    def step(self):
        if (isinstance(self.box, Box)):
            pass

        moves = []
        for i in [-1, 1]:
            moves.append((self.pos[0], self.pos[1] + i))
            moves.append((self.pos[0] + i, self.pos[1]))

        neighbors = self.model.grid.get_neighbors(self.pos, False, False, 1)

        for agent in neighbors:
            if (isinstance(agent, Box) and self.box == None and agent.can_be_grabbed):
                self.model.grid.move_agent(agent, self.pos)
                self.grab(agent)
                return
            try:
                moves.remove(agent.pos)
            except:
                pass

        try:
            next_pos = moves[random.randint(0, len(moves))]
            print("Moviendo de", self.pos, " a", next_pos)
            self.model.grid.move_agent(self, (int(next_pos[0]), int(next_pos[1])))
            self.model.grid.move_agent(self.box, (int(next_pos[0]), int(next_pos[1])))
        except:
            pass

class Stand(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type == "stand"
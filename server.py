from model import *

SIZE = 15

simulation_params = {
    "width": SIZE,
    "height": SIZE,
    "num_boxes":mesa.visualization.UserSettableParameter(
        "slider",
        "Numero de cajas",
        5,
        5,
        20,
        1,
        description="Elija el numero de cajas."
    )
}

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
    }
    if (isinstance(agent, Box)):
        portrayal["r"] = 0.4
        portrayal["Layer"] = 0
        portrayal["Color"] = "brown"
    elif (isinstance(agent, Robot)):
        portrayal["r"] = 0.7
        portrayal["Layer"] = 0
        portrayal["Color"] = "black"
    elif (isinstance(agent, Stand)):
        portrayal["r"] = 0.1
        portrayal["Layer"] = 0
        portrayal["Color"] = "gray"

    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, SIZE, SIZE, 500, 500)

server = mesa.visualization.ModularServer(
    Almacen, [grid], "Modelo de Interseccion", 
    simulation_params
)
server.port = 8521  # The default
server.launch()
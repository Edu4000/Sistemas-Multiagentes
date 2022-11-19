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
        10,
        1,
        description="Elija el numero de cajas."
    )
}

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.5,
    }
    if (isinstance(agent, Box)):
        portrayal["Layer"] = 0
        portrayal["Color"] = "brown"
    elif (isinstance(agent, Robot)):
        portrayal["Layer"] = 0
        portrayal["Color"] = "black"
    elif (isinstance(agent, Stand)):
        portrayal["Layer"] = 0
        portrayal["Color"] = "gray"

    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, SIZE, SIZE, 500, 500)

# chart = mesa.visualization.ChartModule(
#     [
#         {"Label": "Average Speed", "Color":"green"},
#     ],
#     canvas_height=300,
#     data_collector_name="data"
# )

# chart2 = mesa.visualization.ChartModule(
#     [
#         {"Label": "Perc. Halted Cars", "Color":"red"},
#     ],
#     canvas_height=300,
#     data_collector_name="data"
# )

server = mesa.visualization.ModularServer(
    Almacen, [grid], "Modelo de Interseccion", 
    simulation_params
)
server.port = 8521  # The default
server.launch()
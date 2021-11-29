import flask
from flask.json import jsonify
import uuid
from simRobots import Robot
from simRobots import Box
from simRobots import Rack
from simRobots import Warehouse

games = {}

app = flask.Flask(__name__)

@app.route("/games", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    games[id] = Warehouse()
    return "ok", 201, {'Location': f"/games/{id}"}


@app.route("/games/<id>", methods=["GET"])
def queryState(id):
    global model
    model = games[id]
    model.step()
    positions = []
    for agent in model.schedule.agents:
        if(type(agent)==Box):
            positions.append({"x": agent.pos[0], "y": agent.pos[1]})
        if(type(agent)==Rack):
            positions.append({"x": agent.pos[0], "y": agent.pos[1], "boxes": agent.boxAmount})
        if(type(agent)==Robot):
            positions.append({"x": agent.pos[0], "y": agent.pos[1], "isLoaded": agent.condition})
    
    return jsonify({ "Items": positions})


    #auto1 = model.schedule.agents[len(model.schedule.agents)-4]
    #auto2 = model.schedule.agents[len(model.schedule.agents)-3]
    #auto3 = model.schedule.agents[len(model.schedule.agents)-2]
    #auto4 = model.schedule.agents[len(model.schedule.agents)-1]
    
    #return jsonify({ "Items": [{"x": auto1.pos[0], "y": auto1.pos[1]},{"x": auto2.pos[0], "y": auto2.pos[1]},{"x": auto3.pos[0], "y": auto3.pos[1]},{"x": auto4.pos[0], "y": auto4.pos[1]}]})

app.run()

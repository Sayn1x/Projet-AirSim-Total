import airsim
import json
import math


with open(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\coordonnees_initiales_drone.json") as f:
    data = json.load(f)

X_DRONE_INITIAL = data["x"]
Y_DRONE_INITIAL = data["y"]
Z_DRONE_INITIAL = data["z"]

with open(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\data_plan.json") as f2:
    data_plan = json.load(f2)

IMAGE_ORIGIN_X = data_plan["x_origine"]
IMAGE_ORIGIN_Y = data_plan["y_origine"]

SCALE_PLAN = data_plan["100m"] / 10000
# pixels / cm



def calculer_position_unreal(client):
    position_drone = client.getMultirotorState().kinematics_estimated.position

    position_drone_echelle_unreal = [position_drone.x_val * 100, position_drone.y_val * 100, - position_drone.z_val * 100]
    # metres (unite AirSim) -> cm (unite UE)

    x_unreal = X_DRONE_INITIAL + position_drone_echelle_unreal[0]
    y_unreal = Y_DRONE_INITIAL + position_drone_echelle_unreal[1]
    z_unreal = Z_DRONE_INITIAL + position_drone_echelle_unreal[2]

    return x_unreal, y_unreal, z_unreal


def conversion_position_ue_vers_airsim(x, y, z):
    x_airsim = (x - X_DRONE_INITIAL) / 100
    y_airsim = (y - Y_DRONE_INITIAL) / 100
    z_airsim = - ((z - Z_DRONE_INITIAL) / 100)

    return x_airsim, y_airsim, z_airsim



def calculer_position_plan(client):
    x_unreal, y_unreal, z_unreal = calculer_position_unreal(client)

    x_img = int(IMAGE_ORIGIN_X + (x_unreal * SCALE_PLAN))
    y_img = int(IMAGE_ORIGIN_Y + (y_unreal * SCALE_PLAN))

    yaw_rad = airsim.to_eularian_angles(client.getMultirotorState().kinematics_estimated.orientation)[2]
    yaw_deg = -math.degrees(yaw_rad) - 90

    return x_img, y_img, yaw_deg

def conversion_position_plan_vers_unreal(x_plan, y_plan):
    x_unreal = (x_plan - IMAGE_ORIGIN_X) * (1 / SCALE_PLAN)
    y_unreal = (y_plan - IMAGE_ORIGIN_Y) * (1 / SCALE_PLAN)

    return x_unreal, y_unreal
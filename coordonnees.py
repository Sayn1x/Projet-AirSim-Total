import airsim
import json
import math


with open(r"C:\local\Unreal_AirSim\Python\Test1\ressources\coordonnees.json") as f:
    data = json.load(f)

X_DRONE_INITIAL = data["x"]
Y_DRONE_INITIAL = data["y"]
Z_DRONE_INITIAL = data["z"]

IMAGE_ORIGIN_X = 648
IMAGE_ORIGIN_Y = 675

SCALE_PLAN = 0.031



def calculer_position_unreal(client):
    position_drone = client.getMultirotorState().kinematics_estimated.position

    position_drone_echelle_unreal = [position_drone.x_val * 100, position_drone.y_val * 100, - position_drone.z_val * 100]

    x_unreal = X_DRONE_INITIAL + position_drone_echelle_unreal[0]
    y_unreal = Y_DRONE_INITIAL + position_drone_echelle_unreal[1]
    z_unreal = Z_DRONE_INITIAL + position_drone_echelle_unreal[2]

    return x_unreal, y_unreal, z_unreal


def calculer_position_plan(client):
    x_unreal, y_unreal, z_unreal = calculer_position_unreal(client)

    x_img = int(IMAGE_ORIGIN_X + (x_unreal * SCALE_PLAN))
    y_img = int(IMAGE_ORIGIN_Y + (y_unreal * SCALE_PLAN))

    yaw_rad = airsim.to_eularian_angles(client.getMultirotorState().kinematics_estimated.orientation)[2]
    yaw_deg = -math.degrees(yaw_rad) - 90

    return x_img, y_img, yaw_deg
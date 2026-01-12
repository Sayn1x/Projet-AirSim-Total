import airsim
import json
from pathlib import Path
import math
import coordonnees_drone

print("Chargement des donnees de parcours")
path1 = Path(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\ParcoursPositions")

while True:
    file_name = input("\tNom du fichier : ")
    fichier = path1 / file_name
    if fichier.is_file():
        print("Le fichier existe.")
        break
    else:
        print("Le fichier n'existe pas.")

    
    
with open(fichier) as f:
    data = json.load(f)

#points = {index: point for index, point in enumerate(data)}



client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

client.takeoffAsync().join()

for point in data:
    position_drone_actuelle = client.getMultirotorState().kinematics_estimated.position

    x_actuel = position_drone_actuelle.x_val
    y_actuel = position_drone_actuelle.y_val

    x_destination, y_destination, z_destination = coordonnees_drone.conversion_position_ue_vers_airsim(point["x"], point["y"], point["z"])

    delta_x = x_destination - x_actuel
    delta_y = y_destination - y_actuel

    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)


    client.moveToPositionAsync(x_destination, y_destination, z_destination, 5, yaw_mode = airsim.YawMode(is_rate = False, yaw_or_rate = angle_deg)).join()


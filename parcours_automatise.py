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
        print("Lancement du programme...")
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


def orienter_progressivement(client, angle_cible_deg, vitesse_rotation=30):
    orientation = client.getMultirotorState().kinematics_estimated.orientation 
    yaw_actuel_deg = math.degrees(airsim.to_eularian_angles(orientation)[2])

    delta_angle = angle_cible_deg - yaw_actuel_deg

    # normalisation entre -180 et 180 
    delta_angle = (delta_angle + 180) % 360 - 180

    #durée nécessaire
    duree = abs(delta_angle) / vitesse_rotation

    yaw_rate = vitesse_rotation if delta_angle > 0 else - vitesse_rotation

    client.rotateByYawRateAsync(yaw_rate, duree).join()


    

def version1():
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



def version2():
    for point in data:

        position_drone_actuelle = client.getMultirotorState().kinematics_estimated.position
        x_actuel = position_drone_actuelle.x_val
        y_actuel = position_drone_actuelle.y_val

        x_destination, y_destination, z_destination = coordonnees_drone.conversion_position_ue_vers_airsim(point["x"], point["y"], point["z"])

        delta_x = x_destination - x_actuel
        delta_y = y_destination - y_actuel

        angle_rad = math.atan2(delta_y, delta_x)
        angle_deg = math.degrees(angle_rad)

        # normalisation entre -180 et 180 
        angle_deg = (angle_deg + 180) % 360 - 180


        client.moveToPositionAsync(x_destination, y_destination, z_destination, 5, yaw_mode = airsim.YawMode(is_rate = False, yaw_or_rate = angle_deg)).join()

        orienter_progressivement(client, angle_deg)


version2()





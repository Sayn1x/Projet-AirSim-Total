import airsim
import json
from pathlib import Path
import math
import time
import coordonnees_drone

# =========================================

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

# =========================================


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


def deplacement_vers_point1_rotation_vers_point2(point1, point2):

    # ====== Vecteur direction unitaire ======

    state = client.getMultirotorState()
    pos = state.kinematics_estimated.position
    x, y, z = pos.x_val, pos.y_val, pos.z_val

    x_f, y_f, z_f = coordonnees_drone.conversion_position_ue_vers_airsim(point1["x"], point1["y"], point1["z"])

    dx = x_f - x
    dy = y_f - y
    dz = z_f - z

    distance = math.sqrt(dx**2 + dy**2 + dz**2)

    if distance < 1e-3:
        vx = vy = vz = 0
    else:
        ux = dx / distance
        uy = dy / distance
        uz = dz / distance

    # =========== Vecteur vitesse ============
    
    speed = 3.0

    vx = ux * speed
    vy = uy * speed
    vz = uz * speed

    # ========================================

    dt = 0.1
    duration = distance / speed
    steps = int(duration / dt)

    
    yaw_start = math.degrees(airsim.to_eularian_angles(state.kinematics_estimated.orientation)[2])

    # ============ Angle rotation ===========

    x2, y2, z2 = coordonnees_drone.conversion_position_ue_vers_airsim(point2["x"], point2["y"], point2["z"])

    projection_x = x2 - x_f
    projection_y = y2 - y_f

    yaw_end = math.degrees(math.atan2(projection_y, projection_x))


    # ================ Boucle ================

    for i in range(steps):
        t = i / steps
        yaw = yaw_start + (yaw_end - yaw_start) * t

        client.moveByVelocityAsync(
            vx=vx,
            vy=vy,
            vz=vz,
            duration=dt,
            yaw_mode=airsim.YawMode(False, yaw)
        )

        time.sleep(dt)

    client.hoverAsync().join()


def version3():
    for i in range(len(data)):

        if(i < len(data) - 1):
            deplacement_vers_point1_rotation_vers_point2(data[i], data[i+1])

        else:
            x_f, y_f, z_f = coordonnees_drone.conversion_position_ue_vers_airsim(data[i]["x"], data[i]["y"], data[i]["z"])

            client.moveToPositionAsync(x_f, y_f, z_f, 5).join()
    



version3()


        





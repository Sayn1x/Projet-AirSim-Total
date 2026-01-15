import airsim
import json
from pathlib import Path
import math
import os
import time
import coordonnees_drone

# =========================================

print("Chargement des donnees de parcours")
default_path = r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\ParcoursPositions"
while True:
    file_name = input("\tNom du fichier : ")
    file_name = file_name.removesuffix(".json")

    default_path = Path(default_path) / file_name

    file_path = default_path / (file_name + ".json")

    if file_path.is_file():
        print("Lancement du programme...")
        break
    else:
        print("Le fichier n'existe pas.")

with open(file_path) as f:
    data = json.load(f)


#points = {index: point for index, point in enumerate(data)}


# =========================================

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

client.takeoffAsync().join()

# variables
vitesse = 4

position_drone = client.getMultirotorState().kinematics_estimated.position
derniere_position = [position_drone.x_val, position_drone.y_val, position_drone.z_val]
distance_derniere_photo = 0

photo_file_number = 0

positions_photo_data = []

def take_a_photo():
    global distance_derniere_photo, derniere_position, photo_file_number, positions_photo_data
    position_drone = client.getMultirotorState().kinematics_estimated.position

    delta_x = position_drone.x_val - derniere_position[0]
    delta_y = position_drone.y_val - derniere_position[1]
    delta_z = position_drone.z_val - derniere_position[2]

    distance_derniere_photo = math.sqrt(delta_x ** 2 + delta_y ** 2 + delta_z ** 2)

    if(distance_derniere_photo >= 2):
        derniere_position = [position_drone.x_val, position_drone.y_val, position_drone.z_val]

        # Capture une image PNG depuis la caméra 0
        png_image = client.simGetImage("0", airsim.ImageType.Scene)

        # Dossier photos
        photos_dir = default_path / "photos"
        os.makedirs(photos_dir, exist_ok=True)

        # Nom du fichier
        photo_file_number += 1
        photo_file_name = f"rgb-{photo_file_number}.png"
        file_path = photos_dir / photo_file_name

        with open(file_path, "wb") as f:
            f.write(png_image)

        x_img, y_img, yaw_deg = coordonnees_drone.calculer_position_plan(client)
        positions_photo_data.append({"Filename": photo_file_name, "x": x_img, "y": y_img, "yaw": yaw_deg})


def move_and_take_photos(x, y, z, vitesse, yaw_mode = False):

    if yaw_mode == False:
        client.moveToPositionAsync(x, y, z, vitesse)
    else:
        client.moveToPositionAsync(x, y, z, vitesse, yaw_mode = yaw_mode)

    start_time = time.time()
    distance = math.sqrt(
        (client.getMultirotorState().kinematics_estimated.position.x_val - x)**2
        + (client.getMultirotorState().kinematics_estimated.position.y_val - y)**2
        + (client.getMultirotorState().kinematics_estimated.position.z_val - z)**2)

    TIMEOUT = distance / vitesse + 5
    # 5 secondes de marge

    while True:
        position_actuelle = client.getMultirotorState().kinematics_estimated.position

        distance_to_target = math.sqrt((x - position_actuelle.x_val)**2 + (y - position_actuelle.y_val)**2 + (z - position_actuelle.z_val)**2)

        take_a_photo()

        if distance_to_target < 1:
            break
        if time.time() - start_time > TIMEOUT:
            break

        time.sleep(0.05)



def parcours():
    global vitesse
    for point in data:

        position_drone_actuelle = client.getMultirotorState().kinematics_estimated.position
        x_actuel = position_drone_actuelle.x_val
        y_actuel = position_drone_actuelle.y_val
        z_actuel = position_drone_actuelle.z_val

        x_destination, y_destination, z_destination = coordonnees_drone.conversion_position_ue_vers_airsim(point["x"], point["y"], point["z"])

        delta_x = x_destination - x_actuel
        delta_y = y_destination - y_actuel
        delta_z = z_destination - z_actuel

        distance_horizontale = math.sqrt(delta_x ** 2 + delta_y ** 2)
        distance_verticale = abs(delta_z)


        # ROTATION VERS PROCHAIN POINT
        angle_rad = math.atan2(delta_y, delta_x)
        angle_deg = math.degrees(angle_rad)
        angle_deg = (angle_deg + 180) % 360 - 180


        if distance_verticale > 2 * distance_horizontale :
            move_and_take_photos(x_destination, y_destination, z_destination, vitesse)
        else :
            move_and_take_photos(x_destination, y_destination, z_destination, vitesse, yaw_mode = airsim.YawMode(is_rate = False, yaw_or_rate = angle_deg))


        # INSPECTION
        if point["inspection"]:
            time.sleep(3)

            t = 0
            while t < 4 :
                gimbal_pitch = - math.radians(45) * math.sin(t * math.pi / 4)

                orientation = airsim.to_quaternion(gimbal_pitch, 0, 0)

                # Pose de la caméra (position fixe, orientation variable)
                pose = airsim.Pose(airsim.Vector3r(0, 0, 0), orientation)
                # Application de la pose
                client.simSetCameraPose("0", pose)

                t += 0.02
                time.sleep(0.02)



            # client.rotateByYawRateAsync(yaw_rate=45, duration=8).join()

        take_a_photo()
        time.sleep(0.5)


    client.landAsync().join()

    chemin_fichier = os.path.join(default_path, "photos", "data_photos.json")

    with open(chemin_fichier, "w") as f:
        json.dump(positions_photo_data, f, indent=4)

    print("Informations relatives aux photos enregistrees dans :", chemin_fichier)



parcours()
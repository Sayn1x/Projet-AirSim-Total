import airsim
import map
import time
import math
from pynput import keyboard
import coordonnees_drone
import json
from datetime import datetime
import os

 
# =========================
# INITIALISATION
# =========================

trigger_affichage = False
mode_enregistrement = False
fermer_fenetres = False
positions_enregistrees = []
pressed_keys = set()

speed = 4
yaw_rate_speed = 60


# =========================
# CONNEXION AIRSIM
# =========================

client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()

print("Contrôles :")
print("Z/S = Avant / Arrière")
print("Q/D = Gauche / Droite")
print("Espace = Monter")
print("Shift = Descendre")
print("A/E = Yaw gauche / droite")
print("P = Prendre une photo")
print("CTRL + C = Quitter")


# =========================
# CLAVIER (pynput)
# =========================

def on_press(key):
    global trigger_affichage, mode_enregistrement, fermer_fenetres

    try:
        char = key.char.lower()
        pressed_keys.add(char)

        if char == 'p':
            trigger_affichage = True

        if mode_enregistrement:
            if char == 'y':
                x, y, z = coordonnees_drone.calculer_position_unreal(client)
                positions_enregistrees.append({"x": x, "y": y, "z": z})
                print(f"Position enregistrée : {x:.2f}, {y:.2f}, {z:.2f}")
                fermer_fenetres = True
                mode_enregistrement = False

            elif char == 'n':
                print("Position ignorée.")
                fermer_fenetres = True
                mode_enregistrement = False

    except AttributeError:
        pressed_keys.add(key)


def on_release(key):
    try:
        pressed_keys.discard(key.char)
    except AttributeError:
        pressed_keys.discard(key)


listener = keyboard.Listener(on_press=on_press, on_release=on_release, daemon=True)
listener.start()


# =========================
# BOUCLE PRINCIPALE
# =========================

try:
    while True:

        # --- Affichage / capture ---
        if trigger_affichage:
            img_cam, img_plan = map.generer_images(client)
            map.afficher_images(img_cam, img_plan)
            print("\nVoulez-vous enregistrer la position ? (y/n)")
            mode_enregistrement = True
            trigger_affichage = False

        if fermer_fenetres:
            map.fermer_fenetres()
            fermer_fenetres = False

        # --- Commandes ---
        v_forward = 0
        v_right = 0
        v_z = 0
        yaw_rate = 0

        if 'z' in pressed_keys:
            v_forward = speed
        if 's' in pressed_keys:
            v_forward = -speed
        if 'q' in pressed_keys:
            v_right = -speed
        if 'd' in pressed_keys:
            v_right = speed

        if keyboard.Key.space in pressed_keys:
            v_z = -speed
        if keyboard.Key.shift in pressed_keys:
            v_z = speed

        if 'a' in pressed_keys:
            yaw_rate = -yaw_rate_speed
        if 'e' in pressed_keys:
            yaw_rate = yaw_rate_speed

        # --- Conversion repère ---
        state = client.getMultirotorState()
        yaw = airsim.to_eularian_angles(
            state.kinematics_estimated.orientation
        )[2]

        vx = v_forward * math.cos(yaw) - v_right * math.sin(yaw)
        vy = v_forward * math.sin(yaw) + v_right * math.cos(yaw)

        client.moveByVelocityAsync(
            vx, vy, v_z, 0.1,
            yaw_mode=airsim.YawMode(is_rate=True, yaw_or_rate=yaw_rate)
        )

        time.sleep(0.03)

# =========================
# ARRÊT PROPRE
# =========================

except KeyboardInterrupt:
    print("\nArrêt demandé (Ctrl + C)")

finally:
    print("Nettoyage en cours...")

    try:
        listener.stop()
    except Exception:
        pass

    try:
        client.moveByVelocityAsync(0, 0, 0, 0.1)
        client.hoverAsync()
    except Exception:
        pass

    try:
        client.armDisarm(False)
        client.enableApiControl(False)
    except Exception:
        pass


    if len(positions_enregistrees) != 0:
        # Chemin complet du fichier
        nom_fichier = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        chemin_fichier = os.path.join(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\ParcoursPositions", nom_fichier)

        # Écriture du fichier JSON
        with open(chemin_fichier, "w") as f:
            json.dump(positions_enregistrees, f, indent=4)

        print("Positions enregistrées dans :", chemin_fichier)


    print("Fin du programme.")

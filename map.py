import airsim
import cv2
import numpy as np
import time
import threading
import math
import json
import coordonnees_drone

# -----------------------------
#   CONSTANTES GLOBALES
# -----------------------------

PLAN_PATH = r"C:\local\Unreal_AirSim\Python\Test1\ressources\map_assets\plan.tiff"
ARROW_PATH = r"C:\local\Unreal_AirSim\Python\Test1\ressources\map_assets\arrow.png"

SCALE_ARROW = 35 / 900

# Thread-safe flag
affichage_demande = False
client_global = None



def generer_images(client):
    # 1. Caméra
    png = client.simGetImage("0", airsim.ImageType.Scene)
    img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    img_resized = cv2.resize(img, (640, 360))


    # 2. Position drone sur plan

    x_img, y_img, yaw_deg = coordonnees_drone.calculer_position_plan(client)



    # 3. Plan
    plan = cv2.imread(PLAN_PATH)
    arrow = cv2.imread(ARROW_PATH, cv2.IMREAD_UNCHANGED)

    # Redimension flèche
    h0, w0 = arrow.shape[:2]
    arrow = cv2.resize(arrow, (int(w0 * SCALE_ARROW), int(h0 * SCALE_ARROW)))

    # Rotation
    h_arrow, w_arrow = arrow.shape[:2]
    center = (w_arrow // 2, h_arrow // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, yaw_deg, 1.0)
    arrow_rotated = cv2.warpAffine(arrow, rot_matrix, (w_arrow, h_arrow), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)

    # Collage
    x1 = x_img - w_arrow // 2
    y1 = y_img - h_arrow // 2
    x2 = x1 + w_arrow
    y2 = y1 + h_arrow

    x1c = max(0, x1)
    y1c = max(0, y1)
    x2c = min(plan.shape[1], x2)
    y2c = min(plan.shape[0], y2)

    roi_plan = plan[y1c:y2c, x1c:x2c]
    roi_arrow = arrow_rotated[y1c - y1:y2c - y1, x1c - x1:x2c - x1]

    alpha = roi_arrow[:, :, 3] / 255.0
    alpha = alpha[..., None]

    plan[y1c:y2c, x1c:x2c] = (alpha * roi_arrow[:, :, :3] + (1 - alpha) * roi_plan).astype(np.uint8)

    return img_resized, plan


def afficher_images(img_cam, img_plan):
    cv2.imshow("Plan du monde", img_plan)
    cv2.imshow("AirSim - Camera", img_cam)
    key = cv2.waitKey(1) & 0xFF

def fermer_fenetres():
    cv2.destroyAllWindows()

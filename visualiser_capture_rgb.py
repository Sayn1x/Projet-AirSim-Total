import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os

# -------------------------
# Chargement du plan initial
# -------------------------

map_path = r"C:\local\Unreal_AirSim\Python\Test1\ressources\map_assets\plan.tiff"
arrow_path = r"C:\local\Unreal_AirSim\Python\Test1\ressources\map_assets\arrow.png"

with open(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\data_plan.json") as f2:
    data_plan = json.load(f2)

width, height = data_plan["width"], data_plan["height"]

def cv2_to_tk(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return ImageTk.PhotoImage(Image.fromarray(img))

# -------------------------
# Tkinter : fenêtre principale
# -------------------------

root = tk.Tk()
root.title("Plan principal")

# Frame pour afficher le plan
label_plan = tk.Label(root)
label_plan.pack(padx=10, pady=10)

# Charger et afficher le plan.tiff
img_plan = cv2.imread(map_path)
img_plan = cv2.resize(img_plan, (width, height))
photo_plan = cv2_to_tk(img_plan)
label_plan.config(image=photo_plan)
label_plan.image = photo_plan

# -------------------------
# Fonction d'ouverture PNG
# -------------------------

def overlay_png(background, overlay, x, y):
    h, w = overlay.shape[:2]

    x -= overlay.shape[1] // 2
    y -= overlay.shape[0] // 2

    # zone où coller
    roi = background[y:y+h, x:x+w]

    # Séparer les canaux
    overlay_rgb = overlay[:, :, :3]
    overlay_alpha = overlay[:, :, 3:] / 255.0

    # Mélange alpha
    roi[:] = overlay_rgb * overlay_alpha + roi * (1 - overlay_alpha)


def rotate_image(img, angle):
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)



def ouvrir_fichier():
    chemin = filedialog.askopenfilename(
        title="Choisir une image",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.tiff *.bmp")]
    )

    if not chemin:
        return

    img2 = cv2.imread(chemin)
    if img2 is None:
        print("Impossible de charger :", chemin)
        return
    img2 = cv2.resize(img2, (480, 270))

    default_path, photo_file = os.path.split(chemin)

    print(default_path)

    data_photo_path = default_path + "/data_photos.json"
    with open(data_photo_path) as f:
        data_photo = json.load(f)

    for photo in data_photo:
        if photo["Filename"] == photo_file:
            x = int(photo["x"])
            y = int(photo["y"])
            yaw = float(photo["yaw"])

            # Charger flèche
            img_arrow = cv2.imread(arrow_path, cv2.IMREAD_UNCHANGED)
            img_arrow = cv2.resize(img_arrow, (30, 30))

            # Rotation
            img_arrow = rotate_image(img_arrow, yaw)

            # Copier le plan pour ne pas modifier l’original
            img_plan_copy = img_plan.copy()

            # Overlay
            overlay_png(img_plan_copy, img_arrow, x, y)

            # Afficher le plan avec la flèche dans la fenêtre principale
            photo_plan = cv2_to_tk(img_plan_copy)
            label_plan.config(image=photo_plan)
            label_plan.image = photo_plan


    # Nouvelle fenêtre Tkinter
    new_win = tk.Toplevel(root)
    new_win.title(f"Image : {chemin}")

    # Convertir et afficher l'image
    photo2 = cv2_to_tk(img2)
    label2 = tk.Label(new_win, image=photo2)
    label2.image = photo2
    label2.pack(padx=10, pady=10)

# -------------------------
# Menu dans la fenêtre principale
# -------------------------

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

menu_fichier = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Fichier", menu=menu_fichier)

menu_fichier.add_command(label="Ouvrir...", command=ouvrir_fichier)
menu_fichier.add_command(label="Quitter", command=root.quit)

root.mainloop()

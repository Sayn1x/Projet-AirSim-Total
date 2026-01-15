import cv2
import coordonnees_drone
from datetime import datetime
import os
import json
import tkinter as tk
from tkinter import ttk

# --- paramètres ---
image_path = r"C:\local\Unreal_AirSim\Python\Test1\ressources\map_assets\plan.tiff"

with open(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\data_plan.json") as f2:
    data_plan = json.load(f2)

width, height = data_plan["width"], data_plan["height"]

positions_parcours = []

slider_value = None


def curseur(nom):
    """Ouvre une fenêtre Tkinter avec un slider et affiche la valeur en direct."""
    global slider_value

    root = tk.Tk()
    root.title(nom)
    root.geometry("300x140")

    # Variable Tkinter pour suivre la valeur
    val = tk.DoubleVar(value=4.5)

    # Label qui affichera la valeur en temps réel
    label = ttk.Label(root, text=f"Altitude : {val.get():.2f}")
    label.pack(pady=5)

    step = 0.5

    # Fonction appelée à chaque mouvement du slider
    def update_label(event=None):
        valeur_arrondie = round(val.get() / step) * step
        val.set(valeur_arrondie)
        label.config(text=f"Altitude : {val.get():.2f}")

    # Slider
    scale = ttk.Scale(
        root,
        from_=0,
        to=15,
        orient="horizontal",
        variable=val,
        command=update_label  # mise à jour en direct
    )
    scale.pack(pady=10)

    # Bouton de validation
    def validate():
        global slider_value
        slider_value = val.get()
        root.destroy()

    def on_close():
        global slider_value
        slider_value = 4.5
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    ttk.Button(root, text="Valider", command=validate).pack(pady=5)

    root.mainloop()
    return slider_value


# --- callback souris ---
def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img_resized, (x, y), 2, (0, 0, 255), -1)

        valeur = curseur("Waypoint - Inspection")
        print(f"Altitude choisie : {valeur} m")
        altitude = -12718.0 + valeur * 100

        x_unreal, y_unreal = coordonnees_drone.conversion_position_plan_vers_unreal(x, y)
        print(f"Position enregistrée avec inspection : x={x_unreal}, y={y_unreal}, z={altitude}")
        positions_parcours.append({"x": x_unreal, "y": y_unreal, "z": altitude, "inspection": True})

    if event == cv2.EVENT_RBUTTONDOWN:
        cv2.circle(img_resized, (x, y), 2, (255, 0, 0), -1)

        valeur = curseur("Waypoint")
        print(f"Altitude choisie : {valeur} m")
        altitude = -12718.0 + valeur * 100

        x_unreal, y_unreal = coordonnees_drone.conversion_position_plan_vers_unreal(x, y)
        print(f"Position enregistrée sans inspection : x={x_unreal}, y={y_unreal}, z={altitude}")
        positions_parcours.append({"x": x_unreal, "y": y_unreal, "z": altitude, "inspection": False})


# --- chargement de l'image ---
img = cv2.imread(image_path)
if img is None:
    raise ValueError("Impossible de charger l'image.")

# redimensionner l'image
img_resized = cv2.resize(img, (width, height))

# --- création de la fenêtre ---
cv2.namedWindow("Plan", cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow("Plan", width, height)

# associer la fonction de callback
cv2.setMouseCallback("Plan", on_mouse)

# --- boucle d'affichage ---
while True:
    cv2.imshow("Plan", img_resized)
    if cv2.waitKey(1) & 0xFF == 27:  # touche ESC pour quitter
        if len(positions_parcours) != 0:
            nom_fichier = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            dossier = os.path.join(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\ParcoursPositions", nom_fichier)

            # Crée le dossier si nécessaire
            os.makedirs(dossier, exist_ok=True)

            chemin_fichier = os.path.join(dossier, nom_fichier + ".json")

            with open(chemin_fichier, "w") as f:
                json.dump(positions_parcours, f, indent=4)

            print("Positions enregistrées dans :", chemin_fichier)
        break

cv2.destroyAllWindows()

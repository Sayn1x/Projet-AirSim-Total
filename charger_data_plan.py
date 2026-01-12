import json

print("Dimensions du plan")
while True:
    try :
        width = int(input("\tWidth : "))
        break
    except :
        print("\tVeuillez entrer un nombre...")
        
while True:
    try :
        height = int(input("\tHeight : "))
        break
    except:
        print("\tVeuillez entrer un nombre...")
        
        

print("Coordonnees de l'origine Unreal Engine en unite px sur le plan")
while True:
    try :
        x= int(input("\tx : "))
        break
    except :
        print("\tVeuillez entrer un nombre...")

while True:
    try:
        y = int(input("\ty : "))
        break
    except:
        print("\tVeuillez entrer un nombre...")



print("100m Unreal Engine en nombre de pixels sur le plan")
while True:
    try:
        echelle = int(input("\tEchelle (en px) : "))
        break
    except:
        print("\tVeuillez entrer un nombre...")
        
        
data = {"width":width, "height":height, "100m":echelle, "x_origine":x, "y_origine":y}


with open(r"C:\local\Unreal_AirSim\Python\Test1\ressources\data\data_plan.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    

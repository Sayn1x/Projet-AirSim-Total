import cv2

def afficher_images(img_cam, img_plan):
    cv2.imshow("Plan du monde", img_plan)
    cv2.imshow("AirSim - Camera", img_cam)
    key = cv2.waitKey(1) & 0xFF

def fermer_fenetres():
    cv2.destroyAllWindows()

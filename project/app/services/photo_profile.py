import cv2
from PIL import Image
import os

cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")

# Extract face from image
def extract_face(image_path):
    # Load the image
    image = cv2.imread(image_path)
    image_crop = Image.open(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=2,
        minSize=(40, 60),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    # If no faces are detected, return None
    if len(faces) == 0:
        return image

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Crop
    im_crop = image_crop.crop((x-20, y-20, (x+w+20), (y+h+20)))
    return im_crop
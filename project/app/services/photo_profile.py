import cv2
from PIL import Image
import os

cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")

# Extract face from image
def extract_face(image_path):
    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Load the image
    image = cv2.imread(image_path)
    image_crop = Image.open(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=2,
        minSize=(40, 60),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Check if faces are detected
    if len(faces) == 0 or len(faces) > 1:
        print("No faces detected!")
        return None

    # Process the first detected face
    x, y, w, h = faces[0]

    # Crop the face with padding
    padding = 20
    left = max(x - padding, 0)
    top = max(y - padding, 0)
    right = min(x + w + padding, image_crop.width)
    bottom = min(y + h + padding, image_crop.height)

    im_crop = image_crop.crop((left, top, right, bottom))
    return im_crop
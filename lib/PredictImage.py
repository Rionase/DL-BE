from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import os
from io import BytesIO

from lib.GetLastModel import GetLastModelFile

def PrepocessImage(file_content):
    # Load the image from the in-memory file content
    img = Image.open(BytesIO(file_content))

    # Resize the image to the size expected by the model (256x256)
    img = img.resize((256, 256))

    # Convert the image to a numpy array
    img_array = np.array(img)

    # Normalize the pixel values (0-255 -> 0-1)
    img_array = img_array / 255.0

    # Add a batch dimension (1, 256, 256, 3)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

def PredictImage(file_content, models):
    # Preprocess the image
    img_array = PrepocessImage(file_content)

    model = load_model(f"models/{models}")

    # Make the prediction
    prediction = model.predict(img_array)

    # The model output is between 0 and 1, so we use a threshold to classify (e.g., 0.5)
    if prediction > 0.5:
        return "Unorganic Trash"
    else:
        return "Organic Trash"
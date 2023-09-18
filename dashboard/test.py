import cv2
import numpy as np
from inferenceModel import ImageToWordModel
# Load the input image
image = cv2.imread("roi_13_iPKbC3b.jpg")

# Create an instance of the ImageToWordModel class
model = ImageToWordModel(model_path="Models/08_handwriting_recognition_torch/202303142139/model.onnx")

# Call the predict method with the input image
prediction_text = model.predict(image)

# Print the predicted text
print(f"Prediction: {prediction_text}")

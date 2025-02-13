import joblib
import json
import numpy as np
import base64
import cv2
import logging
from wavelet import w2d

#these variables are used to store the name and number as key value pairs
__class_name_to_number = {} # eg. messi:1
__class_number_to_name = {} # this store the reversed key values eg. 1:messi

__model = None  #this variable will store model

#in python __ means that the variable is declared private to that file


#we can take image here either from the path or the base64 string
def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    face_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_eye.xml')

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    cropped_faces = []
    for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                cropped_faces.append(roi_color)
    return cropped_faces
 

#takes the base64 string and converts it into opnecv image
def get_cv2_image_from_base64_string(b64str):
    encoded_data = b64str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

#read the b64 string stored in the text file and return it
#this b64 can be passed to the main clssify functiion which classifies the image 
def get_b64_test_image_for_virat():
    with open("b64.txt") as f:
        return f.read()

 
def classify_image(image_base64_data, file_path=None):
    if __model is None:
        logging.error("Model is not loaded properly.")
        return []

    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)

    result = []
    for img in imgs:
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'db1', 5) #haar cascade the image
        scalled_img_har = cv2.resize(img_har, (32, 32)) #resize the haar cascade image
        combined_img = np.vstack((scalled_raw_img.reshape(32 * 32 * 3, 1), scalled_img_har.reshape(32 * 32, 1)))

        len_image_array = 32*32*3 + 32*32

        final = combined_img.reshape(1,len_image_array).astype(float)
        
        result.append({
            'class': class_number_to_name(__model.predict(final)[0]),
            'class_probability': np.around(__model.predict_proba(final)*100,2).tolist()[0],
            'class_dictionary': __class_name_to_number
        })
    return result    
#ui need the class_dictionary to map the number to the name        
    
#np.around(__model.predict_proba(final)*100,2).tolist()[0],
#we predict confidence of model for each class     
        
# model.predict_proba() is used to get the probability 
# estimates for each class.reflects the model's confidence in its predictions.
# The class with the highest probability is usually selected as the predicted class.

    


#our model will give output as a number
#hence to have an understandale output, we will use the number_to_name dictionary
#which we have created in which we have stored name:number key value pairs
def class_number_to_name(class_num):
    return __class_number_to_name[class_num]


#this function is used to load our model 
def load_saved_artifacts():
    logging.debug("Loading saved artifacts...start")
    global __class_name_to_number
    global __class_number_to_name

    try:
        with open("./artifacts/class_dictionary.json", "r") as dict_file:
            __class_name_to_number = json.load(dict_file)
            __class_number_to_name = {v: k for k, v in __class_name_to_number.items()}
    except Exception as e:
        logging.error(f"Error loading class dictionary: {e}")

    global __model
    try:
        if __model is None:
            with open('./artifacts/saved_model.pkl', 'rb') as model_file:
                __model = joblib.load(model_file)
            logging.debug("Model loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading model: {e}")


# During training, datasets are often labeled with numerical values
# for simplicity and performance reasons.
# At prediction time, these numerical values need to be mapped back to their corresponding class names.


if __name__ == '__main__':

    load_saved_artifacts()
    logging.debug("Artifacts loaded. Testing classify_image function.")

    print(classify_image(get_b64_test_image_for_virat(), None)) #just for testing the classify_image function
  
    # print(classify_image(None, "./test_images/federer1.jpg"))
    # print(classify_image(None, "./test_images/federer2.jpg"))
    # print(classify_image(None, "./test_images/virat1.jpg"))
    # print(classify_image(None, "./test_images/virat2.jpg"))
    # print(classify_image(None, "./test_images/virat3.jpg")) # Inconsistent result could be due to https://github.com/scikit-learn/scikit-learn/issues/13211
    # print(classify_image(None, "./test_images/serena1.jpg"))
    # print(classify_image(None, "./test_images/serena2.jpg"))
    # print(classify_image(None, "./test_images/sharapova1.jpg"))

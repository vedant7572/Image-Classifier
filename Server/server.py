from flask import Flask, request, jsonify
import util
import logging

app = Flask(__name__) 

logging.basicConfig(level=logging.DEBUG)

# Load the model and class dictionaries when the server starts
util.load_saved_artifacts()

@app.route('/classify_image', methods=['GET', 'POST'])
def classify_image():
    try:
        image_data = request.form['image_data']
        logging.debug(f"Received image data: {image_data[:100]}...")  # Log part of the image data for sanity check
        response = jsonify(util.classify_image(image_data))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info("Starting Python Flask Server for Celebrity Image Classification")
    app.run(port=5000)
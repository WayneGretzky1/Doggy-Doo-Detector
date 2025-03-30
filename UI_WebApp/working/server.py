from flask import Flask, Response,request, render_template, jsonify, send_from_directory
import os

app = Flask(__name__)

# === Route: Homepage ===
@app.route("/")
def index():
    return render_template("doggy.html")

# === Route: Static Video Feed Placeholder ===
@app.route("/video_feed")
def video_feed():
    # This is a placeholder. Replace with real feed streaming logic.
    return send_from_directory("static/img", "placeholder.jpg")

# Path to the dynamically created images
IMAGE_FOLDER = os.path.join(os.getcwd(), 'static/data')

@app.route('/get-images')
def get_images():
    """Returns a list of image filenames from the data folder."""
    try:
        images = [file for file in os.listdir(IMAGE_FOLDER) if file.endswith(('.jpg', '.jpeg'))]
        return jsonify(images)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/data/<path:filename>')
def serve_image(filename):
    """Serves images from the data directory."""
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/delete-image', methods=['POST'])
def delete_image():
    try:
        data = request.get_json()
        filename = data.get("filename")
        file_path = os.path.join(IMAGE_FOLDER, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": "Image deleted successfully"}), 200
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# === Start the Flask App ===
if __name__ == "__main__":
    app.run(debug=True, port=5000)

import time
import io
import threading
from flask import Flask, Response, request, render_template, jsonify, send_from_directory
import board
import busio
import adafruit_mlx90640
import numpy as np
import os
import cv2
import datetime

# Initialize sensor
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ
frame = np.zeros((24 * 32,))

# Flask app
app = Flask(__name__)
output_frame = None
lock = threading.Lock()

# # HTML template
# PAGE = """
# <html>
# <head>
#     <title>Thermal Camera Stream</title>
# </head>
# <body>
#     <h1>Live Thermal Stream</h1>
#     <img src="{{ url_for('video_feed') }}" />
# </body>
# </html>
# """

#Globals

@app.route('/')
def index():
    return render_template("doggy.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


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


def generate_stream():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def thermal_loop():
    global output_frame, lock
    centers = []
    new_centers = []
    dist_threshold = 20
    frame_threshold = 32
    max_images = 12
    image_path = "./static/data/"
    while True:
        try:
            mlx.getFrame(frame)
            temp_data = np.reshape(frame, (24, 32))
            
            temp_data = cv2.resize(temp_data, (320, 240), interpolation=cv2.INTER_NEAREST)

            # --- Color mapping ---
            norm = cv2.normalize(temp_data, None, 0, 255, cv2.NORM_MINMAX)
            norm_uint8 = np.uint8(norm)
            colored = cv2.applyColorMap(norm_uint8, cv2.COLORMAP_JET)

            # --- Thresholding based on real temp (e.g., 31.0�C) ---
            # thresh_temp = 31.0  # You can adjust this or make it a setting
            thresh_temp = np.percentile(temp_data, 95)
            thresh = np.where(temp_data > thresh_temp, 255, 0).astype(np.uint8)

            # --- Contour detection ---
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(colored, (x, y), (x + w, y + h), (255, 255, 255), 5)  # white box
                    center = (int(x+(w/2)),int(y+(h/2)))
                    new_centers.append([center, 0, False])
                    # cv2.circle(colored, center, 5, (255, 0, 255), -1)
            # Phase 1 & 2
            for center in centers:
                # Phase 1
                matching_center = False
                for new_center in new_centers:
                    # Find distance between centers
                    if np.linalg.norm(np.array(center[0]) - np.array(new_center[0])) <= dist_threshold:
                        center[1] += 1
                        if center[1] > frame_threshold:
                            center[1] = frame_threshold
                        new_centers.remove(new_center)
                        matching_center = True
                if not matching_center:
                    centers.remove(center)
                # Phase 2 & 3
                if center[1] >= frame_threshold and not center[2]:
                    center[2] = True
                    screenshot = colored.copy()
                    cv2.circle(screenshot, center[0], 5, (128, 128, 128), -1)
                    if not os.path.exists(image_path):
                        os.makedirs(image_path)
                    files = os.listdir(image_path)
                    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    num_images = len(files)
                    if(num_images <= max_images):
                        file_path = image_path + date +".jpg"
                        cv2.imwrite(file_path, screenshot)
                    
                    
            # Phase 4
            centers = centers + new_centers
            new_centers = []
                


            # Resize for display (optional)
            # display = cv2.resize(colored, (320, 240), interpolation=cv2.INTER_NEAREST)

            # Save frame to be sent via Flask
            with lock:
                output_frame = colored.copy()

            time.sleep(0.05)

        except ValueError:
            print("Frame error, skipping...")


# Background thread for capturing thermal data
t = threading.Thread(target=thermal_loop)
t.daemon = True
t.start()

# Start Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

from flask import Flask, render_template, Response, send_from_directory
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

# === Start the Flask App ===
if __name__ == "__main__":
    app.run(debug=True, port=5000)

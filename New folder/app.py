from flask import Flask, render_template, request, jsonify
import json
import os
from utils import extract_colors, find_top_palettes
from utils import extract_colors, find_top_palettes, generate_shades

app = Flask(__name__)

# Load dataset
with open("palettes_realistic_2000.json") as f:
    palettes = json.load(f)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/suggest", methods=["POST"])
def suggest():
    image = request.files["image"]
    mode = request.form["mode"]

    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    room_colors = extract_colors(image_path)

    # 🎨 DESIGN MODE
    if mode == "design":
        tone = request.form["tone"]
        style = request.form["style"]

        result = find_top_palettes(
            room_colors,
            palettes,
            tone,
            style
        )

    # 😊 PREFERENCE MODE
    else:
        mood = request.form["mood"]
        fav_color = request.form["fav_color"]

        result = generate_shades(
            fav_color,
            mood
        )

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
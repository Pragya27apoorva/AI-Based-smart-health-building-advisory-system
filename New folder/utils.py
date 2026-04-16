import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import distance
import colorsys
import random

# Extract dominant colors
def extract_colors(image_path, k=3):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (200, 200))
    image = image.reshape((-1, 3))

    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(image)

    return kmeans.cluster_centers_

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)])

def palette_score(room_colors, palette):
    palette_colors = [hex_to_rgb(c) for c in palette["colors"]]

    score = 0
    for rc in room_colors:
        score += min(distance.euclidean(rc, pc) for pc in palette_colors)

    return score


def find_top_palettes(room_colors, palettes, tone, style, top_n=3):
    exact_matches = []
    style_matches = []
    tone_matches = []

    for p in palettes:
        if p["tone"] == tone and p["style"] == style:
            exact_matches.append(p)
        elif p["style"] == style:
            style_matches.append(p)
        elif p["tone"] == tone:
            tone_matches.append(p)

    candidates = exact_matches or style_matches or tone_matches or palettes

    top_palettes = sorted(
        candidates,
        key=lambda p: palette_score(room_colors, p)
    )[:top_n]

    return top_palettes

mood_preferences = {
    "calm": {
        "tones": ["cool", "pastel", "neutral"],
        "styles": ["minimal", "modern"]
    },
    "cozy": {
        "tones": ["warm", "earthy", "pastel"],
        "styles": ["cozy", "nature"]
    },
    "energetic": {
        "tones": ["warm", "cool"],
        "styles": ["vibrant", "modern"]
    },
    "luxurious": {
        "tones": ["neutral", "warm"],
        "styles": ["luxury"]
    },
    "fresh": {
        "tones": ["cool", "pastel"],
        "styles": ["nature", "modern"]
    },
    "romantic": {
        "tones": ["pastel", "warm"],
        "styles": ["cozy", "luxury"]
    }
}


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return np.array([
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    ])


def find_top_palettes_with_mood(
    room_colors,
    palettes,
    mood,
    fav_color,
    top_n=3
):
    fav_rgb = hex_to_rgb(fav_color)

    preferred = mood_preferences[mood]

    candidates = [
        p for p in palettes
        if p["tone"] in preferred["tones"]
        and p["style"] in preferred["styles"]
    ]

    if not candidates:
        candidates = palettes

    scored = []

    for p in candidates:
        palette_colors = [hex_to_rgb(c) for c in p["colors"]]

        room_score = sum(
            min(distance.euclidean(rc, pc) for pc in palette_colors)
            for rc in room_colors
        )

        fav_score = min(
            distance.euclidean(fav_rgb, pc)
            for pc in palette_colors
        )

        total_score = room_score + fav_score

        scored.append((total_score, p))

    scored.sort(key=lambda x: x[0])

    return [p for _, p in scored[:top_n]]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return np.array([
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    ])

def rgb_to_hex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(*rgb)

def mood_shift(rgb, mood):
    rgb = rgb.astype(int)

    if mood == "calm":
        rgb = np.clip(rgb + [0, 10, 20], 0, 255)
    elif mood == "energetic":
        rgb = np.clip(rgb + [20, 10, 0], 0, 255)
    elif mood == "fresh":
        rgb = np.clip(rgb + [0, 20, 0], 0, 255)
    elif mood == "romantic":
        rgb = np.clip(rgb + [20, 0, 20], 0, 255)
    elif mood == "luxurious":
        rgb = np.clip(rgb - [20, 20, 20], 0, 255)

    return rgb

def create_palette(base_rgb, factors, mood):
    palette = []

    for factor in factors:
        new_rgb = np.clip(base_rgb * factor, 0, 255)
        new_rgb = mood_shift(new_rgb, mood)
        palette.append(rgb_to_hex(new_rgb.astype(int)))

    return {"colors": palette}

def generate_shades(base_hex, mood):
    rgb = hex_to_rgb(base_hex)

    suggestion_1 = create_palette(
        rgb,
        [1.4, 1.2, 1.0, 0.9, 0.8],
        mood
    )

    suggestion_2 = create_palette(
        rgb,
        [1.1, 1.0, 0.9, 0.8, 0.7],
        mood
    )

    suggestion_3 = create_palette(
        rgb,
        [0.9, 0.7, 0.6, 0.5, 0.4],
        mood
    )

    return [suggestion_1, suggestion_2, suggestion_3]

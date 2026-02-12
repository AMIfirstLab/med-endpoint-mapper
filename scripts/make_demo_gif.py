"""Generate the README animation. Pillow is only needed for this asset build."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/demo.gif"
W, H = 1000, 360
stages = [
    ("INPUT", "transfection efficency", "source term received"),
    ("NORMALIZE", "transfection efficency", "case · punctuation · whitespace"),
    ("CANDIDATES", "transfection efficiency", "domain-filtered similarity"),
    ("MAPPED", "EP-LNP-003", "confidence 0.93 · REVIEW"),
]

try:
    font_big = ImageFont.truetype("arial.ttf", 34)
    font = ImageFont.truetype("arial.ttf", 23)
except OSError:
    font_big = font = ImageFont.load_default()

frames = []
for index, (stage, value, note) in enumerate(stages):
    frame = Image.new("RGB", (W, H), "#091525")
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((32, 28, 968, 332), radius=24, fill="#10243b", outline="#45ddd3", width=3)
    for i, label in enumerate(["INPUT", "NORMALIZE", "CANDIDATES", "MAPPED"]):
        x = 95 + i * 245
        color = "#55f0d2" if i <= index else "#49647a"
        draw.ellipse((x - 15, 70, x + 15, 100), fill=color)
        draw.text((x - 54, 112), label, font=font, fill=color)
        if i < 3:
            draw.line((x + 22, 85, x + 215, 85), fill=color, width=4)
    draw.text((70, 195), stage, font=font_big, fill="#9e8cff")
    draw.text((70, 246), value, font=font_big, fill="white")
    draw.text((70, 294), note, font=font, fill="#a7c4d7")
    frames.append(frame)
OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=900, loop=0, optimize=True)
print(OUT)

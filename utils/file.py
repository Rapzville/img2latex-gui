import os
import json
import tempfile
import zipfile
from tkinter import filedialog
from PIL import Image
import sys
sys.path.append("../")
from config import HISTORY_FILE

def save_history(history):
    os.makedirs("hist", exist_ok=True)
    data = [(f"hist/formula_{i}.png", latex) for i, (_, latex) in enumerate(history)]
    for i, (img, _) in enumerate(history):
        img.save(f"hist/formula_{i}.png")
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f)

def load_history():
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
            for img_path, latex in data:
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    history.append((img, latex))
        except:
            pass
    return history

def export_history_zip(history):
    if not history:
        return

    path = filedialog.asksaveasfilename(initialdir="output/", defaultextension=".zip", filetypes=[("ZIP Archive", "*.zip")])
    if not path:
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        txt_path = os.path.join(tmpdir, "results.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            for i, (img, latex) in enumerate(history):
                img_path = os.path.join(tmpdir, f"formula_{i}.png")
                img.save(img_path)
                f.write(f"formula_{i}.png: {latex}\n")

        with zipfile.ZipFile(path, 'w') as zipf:
            for i in range(len(history)):
                zipf.write(os.path.join(tmpdir, f"formula_{i}.png"), arcname=f"formula_{i}.png")
            zipf.write(txt_path, arcname="results.txt")
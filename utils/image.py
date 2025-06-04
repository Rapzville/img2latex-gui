from PIL import Image, ImageTk
import platform
import subprocess
import os
import sys
sys.path.append("../")

def crop_black_borders(img, border=2):
    w, h = img.size
    return img.crop((border, border, w - border, h - border))

def process_image(img, model, result_box, image_label, render_label, history):
    img = crop_black_borders(img)
    img.thumbnail((400, 400))
    tk_img = ImageTk.PhotoImage(img)
    image_label.configure(image=tk_img)
    image_label.image = tk_img

    latex = model(img)
    result_box.delete("0.0", "end")
    result_box.insert("0.0", latex)

    from utils.latex_utils import render_latex
    rendered = render_latex(latex)
    if rendered:
        tk_render = ImageTk.PhotoImage(rendered)
        render_label.configure(image=tk_render)
        render_label.image = tk_render

    history.append((img.copy(), latex))
    if len(history) > 5:
        history.pop(0)

def take_screenshot():
    system = platform.system()
    try:
        if system == "Windows":
            import pyautogui
            return pyautogui.screenshot()
        elif system == "Linux":
            if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                region_str = subprocess.check_output(["slurp"]).decode().strip()
                output = "tmp/screenshot.png"
                subprocess.run(["grim", "-g", region_str, output], check=True)
                return Image.open(output)
            else:
                import pyautogui
                return pyautogui.screenshot()
    except Exception as e:
        print(f"Ошибка скриншота: {e}")
        return None

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from pix2tex.cli import LatexOCR
import subprocess
import platform
import io
import matplotlib.pyplot as plt
import os
import json

model = LatexOCR()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

HISTORY_FILE = "hist/history.json"

class ScreenshotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image to LaTeX")
        self.geometry("1000x800")

        self.top_bar = ctk.CTkFrame(self)
        self.top_bar.pack(fill="x")
        
        self.title_label = ctk.CTkLabel(self, text="Image to LaTeX", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)

        self.theme_switch = ctk.CTkSwitch(self.top_bar, text="Тёмная тема", command=self.toggle_theme)
        self.theme_switch.pack(side="left", padx=10, pady=5)
        self.theme_switch.select()

        self.menu_button = ctk.CTkButton(self.top_bar, text="☰ История", width=100, command=self.toggle_history)
        self.menu_button.pack(side="right", padx=10)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=20)

        self.upload_button = ctk.CTkButton(self.button_frame, text="Загрузить изображение", width=250, height=40, command=self.select_file)
        self.upload_button.pack(pady=5)

        self.screenshot_button = ctk.CTkButton(self.button_frame, text="Сделать скриншот", width=250, height=40, command=self.take_screenshot)
        self.screenshot_button.pack(pady=5)

        self.copy_button = ctk.CTkButton(self.button_frame, text="Скопировать LaTeX", width=250, height=40, command=self.copy_latex)
        self.copy_button.pack(pady=5)

        self.export_button = ctk.CTkButton(self.button_frame, text="Экспорт в PDF", width=250, height=40, command=self.export_to_pdf)
        self.export_button.pack(pady=5)


        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.pack()

        self.result_box = ctk.CTkTextbox(self, width=900, height=100)
        self.result_box.pack(pady=10)
        self.result_box.bind("<KeyRelease>", self.on_text_change)

        self.render_label = ctk.CTkLabel(self, text="")
        self.render_label.pack(pady=10)

        self.history = []
        self.history_window = None

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_history()

    def toggle_theme(self):
        current = ctk.get_appearance_mode().lower()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)

    def toggle_history(self):
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.destroy()
            self.history_window = None
        else:
            self.show_history_window()

    def show_history_window(self):
        self.history_window = ctk.CTkToplevel(self)
        self.history_window.title("История")
        self.history_window.geometry("300x600+{}+{}".format(self.winfo_x() + self.winfo_width() - 310, self.winfo_y() + 60))
        self.history_window.resizable(False, True)

        scrollable_frame = ctk.CTkScrollableFrame(self.history_window, width=280, height=540)
        scrollable_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)

        for idx, (img, formula) in enumerate(reversed(self.history)):
            thumb = img.copy()
            thumb.thumbnail((80, 80))
            img_tk = ImageTk.PhotoImage(thumb)

            button = ctk.CTkButton(scrollable_frame, image=img_tk, text=f"{formula[:30]}...", anchor="w",
                                   compound="left", width=250, height=80,
                                   command=lambda l=formula: self.insert_from_history(l))
            button.image = img_tk
            button.pack(pady=5)

        clear_btn = ctk.CTkButton(self.history_window, text="Очистить историю", command=self.clear_history)
        clear_btn.pack(pady=(0, 10))

    def insert_from_history(self, latex):
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", latex)
        self.on_text_change()  
        if self.history_window:
            self.history_window.destroy()

    def clear_history(self):
        self.history = []
        if self.history_window:
            self.history_window.destroy()
        self.save_history()

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.gif")])
        if path:
            img = Image.open(path)
            self.process_image(img, save_to_history=True)

    def take_screenshot(self):
        system = platform.system()
        if system == "Windows":
            import pyautogui
            img = pyautogui.screenshot()
            self.process_image(img, save_to_history=True)
        elif system == "Linux":
            if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                self.screenshot_wayland()
            else:
                self.screenshot_x11()
        else:
            print("ОС не поддерживается")

    def screenshot_wayland(self):
        try:
            region_str = subprocess.check_output(["slurp"]).decode().strip()
            output = "tmp/screenshot.png"
            subprocess.run(["grim", "-g", region_str, output], check=True)
            img = Image.open(output)
            img = self.crop_black_borders(img)
            self.process_image(img, save_to_history=True)
        except Exception as e:
            print(f"Wayland скриншот не удался: {e}")

    def screenshot_x11(self):
        try:
            import pyautogui
            img = pyautogui.screenshot()
            self.process_image(img, save_to_history=True)
        except Exception as e:
            print(f"X11 скриншот не удался: {e}")

    def process_image(self, img, save_to_history=True):
        img = self.crop_black_borders(img)
        img.thumbnail((400, 400))
        tk_img = ImageTk.PhotoImage(img)
        self.image_label.configure(image=tk_img)
        self.image_label.image = tk_img

        latex = model(img)
        self.result_box.delete("0.0", "end")
        self.result_box.insert("0.0", latex)

        rendered = self.render_latex(latex)
        if rendered:
            tk_render = ImageTk.PhotoImage(rendered)
            self.render_label.configure(image=tk_render)
            self.render_label.image = tk_render

        if save_to_history:
            self.history.append((img.copy(), latex))
            if len(self.history) > 5:
                self.history.pop(0)

    def crop_black_borders(self, img, border=2):
        w, h = img.size
        return img.crop((border, border, w - border, h - border))

    def render_latex(self, latex_str):
        try:
            fig = plt.figure(figsize=(0.1, 0.1), dpi=300)
            fig.text(0, 0, f"${latex_str}$", fontsize=12)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)
            plt.close(fig)
            return Image.open(buf)
        except Exception as e:
            print(f"Ошибка рендера LaTeX: {e}")
            return None

    def on_text_change(self, event=None):
        latex = self.result_box.get("0.0", "end").strip()
        if latex:
            rendered = self.render_latex(latex)
            if rendered:
                tk_render = ImageTk.PhotoImage(rendered)
                self.render_label.configure(image=tk_render)
                self.render_label.image = tk_render

    def copy_latex(self):
        latex = self.result_box.get("0.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(latex)
        self.update()

    def export_to_pdf(self):
        latex = self.result_box.get("0.0", "end").strip()
        img = self.render_latex(latex)
        if img:
            path = filedialog.asksaveasfilename(initialdir="output/", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if path:
                img.save(path, "PDF", resolution=300)

    def on_close(self):
        self.save_history()
        self.destroy()

    def save_history(self):
        data = [(f"hist/formula_{i}.png", latex) for i, (_, latex) in enumerate(self.history)]
        for i, (img, _) in enumerate(self.history):
            img.save(f"hist/formula_{i}.png")
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data, f)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                self.history = []
                for img_path, latex in data:
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        self.history.append((img, latex))
            except:
                pass

if __name__ == "__main__":
    app = ScreenshotApp()
    app.mainloop()

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from pix2tex.cli import LatexOCR
import sys
sys.path.append("../")
from ui.history_panel import show_history_window
from utils.image import process_image, take_screenshot
from utils.latex import render_latex, copy_to_clipboard, export_to_pdf 
from utils.file import load_history, save_history, export_history_zip
from config import HISTORY_FILE

model = LatexOCR()

class ScreenshotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image to LaTeX")
        self.geometry("1000x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

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
        ctk.set_appearance_mode("light" if current == "dark" else "dark")

    def toggle_history(self):
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.destroy()
            self.history_window = None
        else:
            self.show_history_window()

    def show_history_window(self):
        self.history_window = show_history_window(
            self, self.history, self.insert_from_history, self.clear_history, self.export_history_zip
        )

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
        save_history(self.history)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.gif")])
        if path:
            img = Image.open(path)
            process_image(img, model, self.result_box, self.image_label, self.render_label, self.history)

    def take_screenshot(self):
        img = take_screenshot()
        if img:
            process_image(img, model, self.result_box, self.image_label, self.render_label, self.history)

    def on_text_change(self, event=None):
        latex = self.result_box.get("0.0", "end").strip()
        if latex:
            rendered = render_latex(latex)
            if rendered:
                tk_render = ImageTk.PhotoImage(rendered)
                self.render_label.configure(image=tk_render)
                self.render_label.image = tk_render

    def copy_latex(self):
        latex = self.result_box.get("0.0", "end").strip()
        copy_to_clipboard(self, latex)

    def export_to_pdf(self):
        latex = self.result_box.get("0.0", "end").strip()
        export_to_pdf(latex)

    def export_history_zip(self):
        export_history_zip(self.history)

    def on_close(self):
        save_history(self.history)
        self.destroy()

    def load_history(self):
        self.history = load_history()

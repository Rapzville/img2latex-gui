import customtkinter as ctk
from PIL import ImageTk
import sys
sys.path.append("../")

def show_history_window(parent, history, insert_callback, clear_callback, export_callback):
    win = ctk.CTkToplevel(parent)
    win.title("История")
    win.geometry(f"300x600+{parent.winfo_x() + parent.winfo_width() - 310}+{parent.winfo_y() + 60}")
    win.resizable(False, True)

    scrollable_frame = ctk.CTkScrollableFrame(win, width=280, height=540)
    scrollable_frame.pack(padx=10, pady=(10, 5), fill="both", expand=True)

    for img, formula in reversed(history):
        thumb = img.copy()
        thumb.thumbnail((80, 80))
        img_tk = ImageTk.PhotoImage(thumb)
        button = ctk.CTkButton(scrollable_frame, image=img_tk, text=f"{formula[:30]}...", anchor="w",
                               compound="left", width=250, height=80,
                               command=lambda l=formula: insert_callback(l))
        button.image = img_tk
        button.pack(pady=5)

    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(pady=(0, 10))

    clear_btn = ctk.CTkButton(btn_frame, text="Очистить историю", command=clear_callback)
    clear_btn.pack(side="left", padx=10)

    zip_btn = ctk.CTkButton(btn_frame, text="Экспорт в ZIP", command=export_callback)
    zip_btn.pack(side="left", padx=10)

    return win

import io
import matplotlib.pyplot as plt
from PIL import Image
from tkinter import filedialog
import sys
sys.path.append("../")

def render_latex(latex_str):
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

def copy_to_clipboard(app, latex):
    app.clipboard_clear()
    app.clipboard_append(latex)
    app.update()

def export_to_pdf(latex):
    img = render_latex(latex)
    if img:
        path = filedialog.asksaveasfilename(initialdir="output/", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            img.save(path, "PDF", resolution=300)

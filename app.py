import os
import threading
import ctypes
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader
import docx
from llm.llm_client import run_llm
from logic.clause_extractor import extract_clauses
from customtkinter import CTkCanvas
from PIL import Image, ImageTk

from logic.pipeline import process_document

# ---------------------------
# Windows 11 Acrylic Blur (Mica)
# ---------------------------
def blur_fx(window):
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_MICA = 2
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_SYSTEMBACKDROP_TYPE,
        ctypes.byref(ctypes.c_int(DWMWA_MICA)),
        ctypes.sizeof(ctypes.c_int)
    )

# ---------------------------
#  Button Ripple
# ---------------------------
class ButtonRipple(ctk.CTkButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Button-1>", self._ripple)
        self.ripple_canvas = None

    def _detect_bg(self):
        return "#1e1e1e" if self.master.dark_mode_enabled else "#f5f5f5"

    def _ripple(self, event):
        # Creates the canvas if not created
        if self.ripple_canvas is None:
            self.ripple_canvas = CTkCanvas(
                self,
                width=self.winfo_width(),
                height=self.winfo_height(),
                bg=self._detect_bg(),
                highlightthickness=0
            )
            self.ripple_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Detects mode that is present 
        parent = self.master
        dark_mode = getattr(parent, "dark_mode_enabled", False)

        ripple_color = "#ffffff30" if dark_mode else "#00000020"

        x, y = event.x, event.y
        radius = 0

        circle = self.ripple_canvas.create_oval(
            x, y, x, y,
            fill=ripple_color,
            outline=""
        )

        def animate():
            nonlocal radius
            radius += 8
            self.ripple_canvas.coords(circle, x-radius, y-radius, x+radius, y+radius)

            if radius < self.winfo_width():
                self.after(10, animate)
            else:
                self.ripple_canvas.delete(circle)

        animate()

# ---------------------------
# Main App
# ---------------------------
class ContractDisclosureApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Contract Disclosure Tool")
        self.root.geometry("900x750")
        self.dark_mode_enabled = False
        self.file_path = None
        self.is_processing = False

        # Enables blur background
        self.root.after(200, lambda: blur_fx(self.root))

        # Appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Main Card with shadow
        self.card = ctk.CTkFrame(self.root, corner_radius=20, fg_color="#f5f5f5")
        self.card.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        self.title = ctk.CTkLabel(
            self.card,
            text="Contract Disclosure Tool",
            font=("Segoe UI", 26, "bold")
        )
        self.title.pack(pady=(20, 10))

        # Dark Mode Toggle
        self.dark_button = ButtonRipple(
            self.card,
            text="🌙 Dark Mode",
            command=self.toggle_dark_mode,
            corner_radius=12,
            width=160,
            height=40
        )
        self.dark_button.pack(pady=10)

        # Upload + Process Buttons Row
        self.button_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.upload_btn = ButtonRipple(
            self.button_frame,
            text="Upload Contract File",
            command=self.upload_file,
            corner_radius=12,
            width=200,
            height=40
        )
        self.upload_btn.pack(side="left", padx=10)

        self.process_btn = ButtonRipple(
            self.button_frame,
            text="Generate Disclosures",
            command=self.start_analysis,
            corner_radius=12,
            width=200,
            height=40
        )
        self.process_btn.pack(side="right", padx=10)

        # Split Frame for editable contract + output
        self.split_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.split_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Left column
        self.contract_text = ctk.CTkTextbox(
            self.split_frame,
            border_width=5,
            width=420,
            height=380,
            corner_radius=12,
            font=("Segoe UI", 13)
        )
        self.contract_text.pack(side="left", fill="both", expand=True, padx=(0,10))

        # Right column
        self.output = ctk.CTkTextbox(
            self.split_frame,
            border_width=5,
            width=420,
            height=380,
            corner_radius=12,
            font=("Segoe UI", 13)
        )
        self.output.pack(side="right", fill="both", expand=True, padx=(10,0))

        # Progress Bar
        self.progress = ctk.CTkProgressBar(
            self.card,
            width=500,
            height=12,
            corner_radius=8
        )
        self.progress.pack(pady=15)
        self.progress.set(0)
        self.progress.pack_forget()

    # ---------------------------
    # Hover Glow UI thing
    # ---------------------------
    def apply_hover_glow(self, widget):
        def on_enter(e):
            glow_color = "#333333" if self.dark_mode_enabled else "#e0eaff"
            widget.configure(fg_color=glow_color)
        def on_leave(e):
            normal_color = "#1e1e1e" if self.dark_mode_enabled else "#f5f5f5"
            widget.configure(fg_color=normal_color)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    
    # ---------------------------
    # Dark / Light Mode
    # ---------------------------
    def toggle_dark_mode(self):
        self.dark_mode_enabled = not self.dark_mode_enabled
        mode_text = "☀️ Light Mode" if self.dark_mode_enabled else "🌙 Dark Mode"
        self.dark_button.configure(text=mode_text)
        if self.dark_mode_enabled:
            ctk.set_appearance_mode("dark")
            self.card.configure(fg_color="#1e1e1e")
            self.contract_text.configure(fg_color="#1e1e1e", text_color="white")
            self.output.configure(fg_color="#1e1e1e", text_color="white")
        else:
            ctk.set_appearance_mode("light")
            self.card.configure(fg_color="#f5f5f5")
            self.contract_text.configure(fg_color="#f5f5f5", text_color="black")
            self.output.configure(fg_color="#f5f5f5", text_color="black")

        

    # ---------------------------
    # File Upload
    # ---------------------------
    def upload_file(self):
        path = filedialog.askopenfilename(
            title="Select a contract file",
            filetypes=[
                ("All supported", "*.pdf *.docx *.txt"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Text", "*.txt"),
            ]
        )
        if path:
            self.file_path = path
            text = self.extract_text(path) or ""
            self.contract_text.delete("1.0", tk.END)
            self.contract_text.insert("1.0", text)
            self.output.insert("end", f"\nLoaded: {os.path.basename(path)}\n\n")

    # ---------------------------
    # Start Process
    # ---------------------------
    def start_analysis(self):
        if not self.contract_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Contract text is empty.")
            return

        self.progress.pack(pady=10)
        self.progress.set(0)

        thread = threading.Thread(target=self.process_file_thread)
        thread.start()
        self.animate_progress()

    # ---------------------------
    #  "Progress" Animation
    # ---------------------------
    def animate_progress(self):
        if self.progress.get() < 0.95:
            self.progress.set(self.progress.get() + 0.01)
            self.root.after(60, self.animate_progress)

    # ---------------------------
    # Thread Worker
    # ---------------------------

    def process_file_thread(self):
        self.is_processing = True
        try:
            text = self.contract_text.get("1.0", tk.END)
            result = process_document(text)  # <-- uses your pipeline
            self.root.after(0, lambda: self.show_result(result))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        self.is_processing = False

    # ---------------------------
    # Display Result
    # ---------------------------
    def show_result(self, result):
        self.progress.set(1)
        self.root.after(300, lambda: self.progress.pack_forget())
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", f"\n\n--- Disclosure Sheet ---\n{result}\n")

    # ---------------------------
    # Extract Text
    # ---------------------------
    def extract_text(self, filepath):
        ext = filepath.lower().split('.')[-1]
        if ext == "pdf":
            reader = PdfReader(filepath)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        if ext == "docx":
            document = docx.Document(filepath)
            return "\n".join(p.text for p in document.paragraphs)
        if ext == "txt":
            return open(filepath, "r", encoding="utf-8", errors="ignore").read()
        return None

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    app = ContractDisclosureApp(root)
    root.mainloop()

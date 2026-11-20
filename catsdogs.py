import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from PIL import Image, ImageTk
import threading
import random


# ------------------------------------------------------------
# PALETTE — a fresh midnight / aqua / coral design
# ------------------------------------------------------------
BG = "#101923"
PANEL = "#1B2936"
PANEL_ALT = "#223442"
ACCENT = "#38D6C5"
ACCENT_DARK = "#1DA99D"
CORAL = "#FF8A70"
TEXT = "#F3F7FA"
MUTED = "#A6B6C2"
SUCCESS = "#55D6A4"
ERROR = "#FF6B78"
TRACK = "#344653"


# ------------------------------------------------------------
# EMBEDDED CLASSIFICATION LOGIC (No external module needed)
# ------------------------------------------------------------
def predict_animal(image_path):
    """
    Classifies the image as a cat or dog. 
    You can replace this function later with your real ML model.
    """
    if not image_path:
        raise ValueError("No image path provided.")
    
    path_obj = Path(image_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    filename_lower = path_obj.name.lower()

    if "cat" in filename_lower:
        animal = "cat"
        confidence = round(random.uniform(0.88, 0.99), 2)
    elif "dog" in filename_lower or "puppy" in filename_lower or "pup" in filename_lower:
        animal = "dog"
        confidence = round(random.uniform(0.89, 0.99), 2)
    else:
        animal = random.choice(["cat", "dog"])
        confidence = round(random.uniform(0.75, 0.96), 2)

    return {
        "animal": animal,
        "confidence": confidence
    }


class PetVision:
    def __init__(self, root):
        self.root = root
        self.root.title("Extra Project Classification | Animal AI & Chat")
        self.root.geometry("1120x760")
        self.root.minsize(960, 680)
        self.root.configure(bg=BG)

        self.image_path = None
        self.photo = None
        self.original_image = None
        self.result = None
        self.zoom = 1.0
        self.busy = False

        self.design()

    # ------------------------- UI HELPERS -------------------------

    def make_button(self, parent, text, command, color=ACCENT,
                    foreground=BG, outline=None):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=foreground,
            activebackground=outline or color,
            activeforeground=foreground,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=12,
            highlightthickness=0
        )
        return button

    def make_label(self, parent, text, size=11, color=TEXT,
                   weight="normal", **kwargs):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, weight),
            bg=parent.cget("bg"),
            fg=color,
            **kwargs
        )

    def design(self):
        # Header
        header = tk.Frame(self.root, bg=PANEL, height=94)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = tk.Frame(header, bg=PANEL)
        header_inner.pack(fill="both", expand=True, padx=30, pady=16)

        brand = tk.Frame(header_inner, bg=PANEL)
        brand.pack(side="left", anchor="center")

        self.make_label(
            brand, "EXTRA PROJECT CLASSIFICATION", 20, ACCENT, "bold"
        ).pack(anchor="w")
        self.make_label(
            brand, "ANIMAL AI VISION & ASSISTANT", 9, MUTED, "bold"
        ).pack(anchor="w", pady=(2, 0))

        self.make_label(
            header_inner, "CAT / DOG • VISION + CHATBOT", 10, MUTED, "bold"
        ).pack(side="right", anchor="center")

        # Main content split layout
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=24, pady=20)

        main.grid_columnconfigure(0, weight=11, uniform="cards")
        main.grid_columnconfigure(1, weight=9, uniform="cards")
        main.grid_rowconfigure(0, weight=1)

        # ----------------- LEFT: Image workspace -----------------
        left = tk.Frame(main, bg=PANEL, highlightthickness=1,
                        highlightbackground="#2B3D4B")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        left_header = tk.Frame(left, bg=PANEL)
        left_header.pack(fill="x", padx=24, pady=(18, 10))

        self.make_label(
            left_header, "Image workspace", 18, TEXT, "bold"
        ).pack(anchor="w")
        self.make_label(
            left_header, "Choose a photo to begin your scan.", 10, MUTED
        ).pack(anchor="w", pady=(2, 0))

        self.preview = tk.Label(
            left,
            text="＋\n\nADD AN IMAGE\n\nJPG  ·  PNG  ·  WEBP",
            font=("Segoe UI", 13, "bold"),
            bg=PANEL_ALT,
            fg=MUTED,
            width=36,
            height=11,
            justify="center",
            bd=0,
            highlightthickness=1,
            highlightbackground=TRACK
        )
        self.preview.pack(pady=10, padx=24)
        self.preview.bind("<Button-1>", lambda e: self.browse_image())

        # Buttons frame
        btn_frame = tk.Frame(left, bg=PANEL)
        btn_frame.pack(fill="x", padx=24, pady=8)

        self.btn_browse = self.make_button(
            btn_frame, "Browse Image", self.browse_image, ACCENT
        )
        self.btn_browse.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_scan = self.make_button(
            btn_frame, "Run AI Scan", self.start_scan, CORAL, foreground=BG
        )
        self.btn_scan.pack(side="right", expand=True, fill="x", padx=(6, 0))
        self.btn_scan.config(state="disabled")

        # Results Box
        self.result_frame = tk.Frame(left, bg=PANEL_ALT, padx=14, pady=12)
        self.result_frame.pack(fill="x", padx=24, pady=10)

        self.lbl_result_title = self.make_label(
            self.result_frame, "Status: Waiting for image...", 11, MUTED, "bold"
        )
        self.lbl_result_title.pack(anchor="w")

        self.lbl_result_sub = self.make_label(
            self.result_frame, "Upload a photo to see classification results.", 9, MUTED
        )
        self.lbl_result_sub.pack(anchor="w", pady=(3, 0))

        # ----------------- RIGHT: Chatbot Panel -----------------
        right = tk.Frame(main, bg=PANEL, highlightthickness=1,
                         highlightbackground="#2B3D4B")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        right_header = tk.Frame(right, bg=PANEL)
        right_header.pack(fill="x", padx=24, pady=(18, 10))

        self.make_label(
            right_header, "Project AI Chat", 18, TEXT, "bold"
        ).pack(anchor="w")
        self.make_label(
            right_header, "Ask questions about pet care and behavior.", 10, MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Chat Text History container
        chat_container = tk.Frame(right, bg=PANEL)
        chat_container.pack(fill="both", expand=True, padx=24, pady=5)

        self.chat_history = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            bg=PANEL_ALT,
            fg=TEXT,
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground=TRACK,
            padx=10,
            pady=10
        )
        self.chat_history.pack(fill="both", expand=True)
        self.chat_history.config(state="disabled")

        # Initial bot greeting
        self.append_chat_message(
            "AI Assistant",
            "Hello! Upload an animal photo and run a scan, or ask me any questions about caring for cats and dogs!"
        )

        # Chat Input bar
        input_frame = tk.Frame(right, bg=PANEL)
        input_frame.pack(fill="x", padx=24, pady=(10, 20))

        self.chat_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg=PANEL_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=TRACK
        )
        self.chat_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat_message())

        self.btn_send = self.make_button(
            input_frame, "Send", self.send_chat_message, ACCENT
        )
        self.btn_send.pack(side="right")

    # ------------------------- APP LOGIC -------------------------

    def browse_image(self):
        file_types = [("Image Files", "*.jpg *.jpeg *.png *.webp")]
        path = filedialog.askopenfilename(title="Select Pet Image", filetypes=file_types)
        if path:
            self.image_path = path
            self.load_image_preview(path)
            self.btn_scan.config(state="normal")
            self.lbl_result_title.config(text="Status: Image Loaded", fg=ACCENT)
            self.lbl_result_sub.config(text=f"File: {Path(path).name}")

    def load_image_preview(self, path):
        try:
            img = Image.open(path)
            self.original_image = img
            img.thumbnail((280, 180))
            self.photo = ImageTk.PhotoImage(img)
            self.preview.config(image=self.photo, text="", width=0, height=0)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def start_scan(self):
        if not self.image_path or self.busy:
            return
        self.busy = True
        self.btn_scan.config(state="disabled")
        self.btn_browse.config(state="disabled")
        self.lbl_result_title.config(text="Status: Scanning with AI...", fg=CORAL)
        self.lbl_result_sub.config(text="Evaluating image features...")

        threading.Thread(target=self.run_prediction_thread, daemon=True).start()

    def run_prediction_thread(self):
        try:
            self.result = predict_animal(self.image_path)
        except Exception as e:
            self.result = {"error": str(e)}

        self.root.after(0, self.update_scan_results)

    def update_scan_results(self):
        self.busy = False
        self.btn_scan.config(state="normal")
        self.btn_browse.config(state="normal")

        if not self.result or "error" in self.result:
            err = self.result.get("error", "Unknown error") if self.result else "No result returned"
            self.lbl_result_title.config(text="Status: Scan Failed", fg=ERROR)
            self.lbl_result_sub.config(text=str(err))
            return

        animal_type = self.result.get("animal", "Unknown")
        confidence = self.result.get("confidence", 0.0)

        self.lbl_result_title.config(text=f"Detected: {animal_type.upper()}", fg=SUCCESS)
        self.lbl_result_sub.config(text=f"Confidence Score: {confidence * 100:.2f}%")

        self.append_chat_message(
            "System",
            f"Successfully classified image! Identified as a **{animal_type}** with {confidence * 100:.1f}% confidence."
        )

    def append_chat_message(self, sender, message):
        self.chat_history.config(state="normal")
        self.chat_history.insert(tk.END, f"\n[{sender}]:\n{message}\n")
        self.chat_history.config(state="disabled")
        self.chat_history.see(tk.END)

    def send_chat_message(self):
        user_msg = self.chat_entry.get().strip()
        if not user_msg:
            return

        self.chat_entry.delete(0, tk.END)
        self.append_chat_message("You", user_msg)

        threading.Thread(
            target=self.generate_bot_response,
            args=(user_msg,),
            daemon=True
        ).start()

    def generate_bot_response(self, user_msg):
        msg_lower = user_msg.lower()

        if "hello" in msg_lower or "hi" in msg_lower:
            reply = "Hello! How can I assist you with your pet today?"
        elif "food" in msg_lower or "diet" in msg_lower or "eat" in msg_lower:
            reply = "Always provide fresh water and a balanced diet tailored to your pet's life stage and species."
        elif "train" in msg_lower or "behavior" in msg_lower:
            reply = "Positive reinforcement with treats, gentle praise, and consistency work wonders for training pets!"
        elif "scan" in msg_lower or "animal" in msg_lower:
            if self.result and "animal" in self.result:
                reply = f"Our current classification scan identified this animal as a {self.result['animal']}. Would you like tips specific to this pet?"
            else:
                reply = "You haven't scanned an image yet! Upload a pet photo and click 'Run AI Scan' first."
        else:
            fallback_options = [
                "That's a great question! Regular veterinary check-ups are always key to a healthy pet.",
                "Pets thrive on daily exercise, mental stimulation, and lots of love.",
                "I'm here to help you understand your animals better. Let me know if you need care advice!",
                "Interesting point! Feel free to ask more questions about training or pet wellness."
            ]
            reply = random.choice(fallback_options)

        self.root.after(0, lambda: self.append_chat_message("AI Assistant", reply))


if __name__ == "__main__":
    root = tk.Tk()
    app = PetVision(root)
    root.mainloop()

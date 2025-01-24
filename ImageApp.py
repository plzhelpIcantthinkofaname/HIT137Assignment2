import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np
 
class SimpleImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image App")
 
        self.image = None
        self.cropped_image = None
 
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)
 
        self.canvas = tk.Canvas(root, width=500, height=450, bg="lightgray")
        self.canvas.pack()
 
        self.save_button = tk.Button(root, text="Save Image", command=self.save_image, state="disabled")
        self.save_button.pack(pady=10)
 
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = cv2.resize(self.image, (500, 450))
            self.display_image()
 
    def display_image(self):
        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.canvas.create_image(0, 0, anchor="nw", image=image_tk)
        self.canvas.image_tk = image_tk
        self.save_button["state"] = "normal"
 
    def save_image(self):
        if self.image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                cv2.imwrite(file_path, self.image)
                tk.messagebox.showinfo("Save Image", "Image saved successfully!")
 
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleImageApp(root)
    root.mainloop()
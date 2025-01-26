"""
Program: EZ Image Editor
Description: A program developed for Assignment 3 of HIT137 to load, crop, resize image and save. 
The program also has additional bonus features: rotate, flip (vertical and horizontal), undo/redo and keyboard shortcuts to enhance functionality.

Authors: Darren Swann, Brayden Brown, Rijan Koirala and Jaafar Mehydeen
Last Updated: 24/01/2025

Features:
1. Load an image: Allows the user to load an image from their local system and it will automatically resize it to fit within the canvas.
2. Crop an image: Allows the user to select an area on the left-hand window and crop that part of the image, which is displayed in the right hand window.
3. Resize the cropped image: Provides a slider to resize the cropped image from 50% to 200% of its current size.
4. Rotate the cropped image: Rotates the cropped image by 90 degrees clockwise.
5. Flip the cropped image: Flip horizontally (mirrors the image along its vertical axis) or Flip vertically (mirrors the image along its horizontal axis).
6. Save the cropped image: Allows the user to save the cropped and edited image to their system.
7. Undo/Redo: Undo reverts the cropped image to its previous state. Redo restores an undone change to the cropped image.
8. Keyboard Shortcuts:
    - Ctrl + L: Load an image.
    - Ctrl + S: Save the cropped image.
    - Ctrl + R: Rotate the cropped image.
    - Ctrl + H: Flip the cropped image horizontally.
    - Ctrl + V: Flip the cropped image vertically.
    - Ctrl + Z: Undo the last action.
    - Ctrl + Y: Redo the last undone action.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk


class EZImageEditor:
    def __init__(self, root):
        """
        Initialise the EZ Image Editor with GUI components.
        """
        self.root = root
        self.root.title("EZ Image Editor")

        # Initialise variables
        self.image = None
        self.original_image = None
        self.cropped_image = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.history = []
        self.redo_stack = []

        # Frame for canvases
        self.image_frame = tk.Frame(root)
        self.image_frame.pack()

        # Original Image Canvas
        self.original_canvas = tk.Canvas(self.image_frame, width=500, height=450, bg="lightgray")
        self.original_canvas.pack(side="left", padx=5)

        # Cropped Image Canvas
        self.cropped_canvas = tk.Canvas(self.image_frame, width=500, height=450, bg="lightgray")
        self.cropped_canvas.pack(side="left", padx=5)

        # Add a red instruction label above all buttons
        self.instruction_label = tk.Label(
            root, 
            text="Crop your image and then edit", 
            fg="red", 
            font=("Helvetica", 12, "bold")
        )
        self.instruction_label.pack(pady=5)

        # Bottom Frame for buttons
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(pady=10)

        # Buttons
        self.load_button = tk.Button(self.bottom_frame, text="Load", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=10)

        # Slider for resizing the cropped image
        self.resize_label = tk.Label(self.bottom_frame, text="Resize Cropped:")
        self.resize_label.grid(row=0, column=1, padx=10)

        self.resize_slider = tk.Scale(
            self.bottom_frame, from_=50, to=200, orient="horizontal", command=self.resize_cropped_image, state="disabled"
        )
        self.resize_slider.grid(row=0, column=2, padx=10)

        self.rotate_button = tk.Button(self.bottom_frame, text="Rotate", command=self.rotate_90, state="disabled")
        self.rotate_button.grid(row=0, column=3, padx=10)

        self.flip_h_button = tk.Button(self.bottom_frame, text="Flip Horizontal", command=self.flip_horizontal, state="disabled")
        self.flip_h_button.grid(row=0, column=4, padx=10)

        self.flip_v_button = tk.Button(self.bottom_frame, text="Flip Vertical", command=self.flip_vertical, state="disabled")
        self.flip_v_button.grid(row=0, column=5, padx=10)

        self.save_button = tk.Button(self.bottom_frame, text="Save", command=self.save_image, state="disabled")
        self.save_button.grid(row=0, column=6, padx=10)

        # Frame for shortcut instructions
        self.shortcut_frame = tk.Frame(root)
        self.shortcut_frame.pack(pady=5)

        # Shortcut instructions label
        self.shortcut_label = tk.Label(
            self.shortcut_frame,
            text="Shortcuts: Ctrl+L (Load), Ctrl+S (Save), Ctrl+R (Rotate), Ctrl+H (Flip Horizontal), Ctrl+V (Flip Vertical), Ctrl+Z (Undo), Ctrl+Y (Redo)",
            fg="blue",
        )
        self.shortcut_label.pack()

        # Bind mouse events to the original canvas
        self.original_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.original_canvas.bind("<B1-Motion>", self.draw_crop_rectangle)
        self.original_canvas.bind("<ButtonRelease-1>", self.perform_crop)

        # Bind keyboard shortcuts
        root.bind("<Control-z>", lambda event: self.undo())
        root.bind("<Control-y>", lambda event: self.redo())
        root.bind("<Control-l>", lambda event: self.load_image())
        root.bind("<Control-s>", lambda event: self.save_image())
        root.bind("<Control-r>", lambda event: self.rotate_90())
        root.bind("<Control-h>", lambda event: self.flip_horizontal())
        root.bind("<Control-v>", lambda event: self.flip_vertical())

    def load_image(self):
        """Load an image from the user's system and display it resized to fit the canvas."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.image = self.resize_to_fit_canvas(self.original_image, self.original_canvas)
            self.display_image(self.image, self.original_canvas)

            # Reset cropped image and buttons
            self.cropped_image = None
            self.save_button["state"] = "disabled"
            self.rotate_button["state"] = "disabled"
            self.flip_h_button["state"] = "disabled"
            self.flip_v_button["state"] = "disabled"
            self.resize_slider["state"] = "disabled"
            self.history.clear()
            self.redo_stack.clear()

    def resize_to_fit_canvas(self, image, canvas):
        """Resize an image to fit within a canvas while maintaining aspect ratio."""
        canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()
        image_height, image_width = image.shape[:2]

        # Calculate scaling factor
        scale = min(canvas_width / image_width, canvas_height / image_height)
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)

        return cv2.resize(image, (new_width, new_height))

    def display_image(self, image, canvas):
        """Display an OpenCV image on a Tkinter canvas."""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)
        canvas.create_image(0, 0, anchor="nw", image=image_tk)
        canvas.image_tk = image_tk

    def start_crop(self, event):
        """Start the cropping process by recording the initial mouse click position."""
        self.start_x, self.start_y = event.x, event.y

    def draw_crop_rectangle(self, event):
        """Draw a rectangle to visualise the cropping area."""
        if self.rect_id:
            self.original_canvas.delete(self.rect_id)
        self.rect_id = self.original_canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red"
        )

    def perform_crop(self, event):
        """Crop the selected area and display it in the cropped canvas."""
        if self.image is not None:
            # Get the ending coordinates of the cropping rectangle
            end_x, end_y = event.x, event.y
            x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
            x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

            # Get the actual dimensions of the displayed (resized) image
            canvas_width, canvas_height = self.original_canvas.winfo_width(), self.original_canvas.winfo_height()
            displayed_height, displayed_width = self.image.shape[:2]

            # Calculate the scaling factor used to fit the image to the canvas
            scale_x = self.original_image.shape[1] / displayed_width
            scale_y = self.original_image.shape[0] / displayed_height

            # Map canvas coordinates back to original image coordinates
            x1 = int(x1 * scale_x)
            x2 = int(x2 * scale_x)
            y1 = int(y1 * scale_y)
            y2 = int(y2 * scale_y)

            # Ensure the coordinates are within bounds
            x1 = max(0, min(self.original_image.shape[1] - 1, x1))
            x2 = max(0, min(self.original_image.shape[1] - 1, x2))
            y1 = max(0, min(self.original_image.shape[0] - 1, y1))
            y2 = max(0, min(self.original_image.shape[0] - 1, y2))

            # Crop the original image using the mapped coordinates
            self.cropped_image = self.original_image[y1:y2, x1:x2]

            # Add the cropped image to history for undo/redo functionality
            self.add_to_history(self.cropped_image)

            # Display the cropped image in the cropped canvas
            self.display_image(self.cropped_image, self.cropped_canvas)

            # Enable buttons for editing cropped image
            self.save_button["state"] = "normal"
            self.rotate_button["state"] = "normal"
            self.flip_h_button["state"] = "normal"
            self.flip_v_button["state"] = "normal"
            self.resize_slider["state"] = "normal"
            self.resize_slider.set(100)  # Reset the slider to 100%

    def resize_cropped_image(self, scale):
        """Resize the cropped image based on the slider value."""
        if self.cropped_image is not None:
            scale = int(scale) / 100.0
            resized_width = int(self.cropped_image.shape[1] * scale)
            resized_height = int(self.cropped_image.shape[0] * scale)
            resized_image = cv2.resize(self.cropped_image, (resized_width, resized_height))
            self.display_image(resized_image, self.cropped_canvas)

    def save_image(self):
        """Save the cropped image to a file."""
        if self.cropped_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                cv2.imwrite(file_path, self.cropped_image)
                messagebox.showinfo("Save Image", "Cropped image saved successfully!")

    def rotate_90(self):
        """Rotate the cropped image by 90 degrees."""
        if self.cropped_image is not None:
            self.add_to_history(self.cropped_image)
            self.cropped_image = cv2.rotate(self.cropped_image, cv2.ROTATE_90_CLOCKWISE)
            self.display_image(self.cropped_image, self.cropped_canvas)

    def flip_horizontal(self):
        """Flip the cropped image horizontally."""
        if self.cropped_image is not None:
            self.add_to_history(self.cropped_image)
            self.cropped_image = cv2.flip(self.cropped_image, 1)
            self.display_image(self.cropped_image, self.cropped_canvas)

    def flip_vertical(self):
        """Flip the cropped image vertically."""
        if self.cropped_image is not None:
            self.add_to_history(self.cropped_image)
            self.cropped_image = cv2.flip(self.cropped_image, 0)
            self.display_image(self.cropped_image, self.cropped_canvas)

    def add_to_history(self, image):
        """Add the current state of the cropped image to the history stack for undo/redo functionality."""
        self.history.append(image.copy())
        self.redo_stack.clear()  # Clear the redo stack whenever a new action is performed

    def undo(self):
        """Undo the last action performed on the cropped image."""
        if self.history:
            self.redo_stack.append(self.cropped_image.copy())
            self.cropped_image = self.history.pop()
            self.display_image(self.cropped_image, self.cropped_canvas)

    def redo(self):
        """Redo the last undone action on the cropped image."""
        if self.redo_stack:
            self.history.append(self.cropped_image.copy())
            self.cropped_image = self.redo_stack.pop()
            self.display_image(self.cropped_image, self.cropped_canvas)

# Entry point for the application
if __name__ == "__main__":
    root = tk.Tk()
    app = EZImageEditor(root)
    root.mainloop()
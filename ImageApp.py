"""
Program: Simple Image App
Description: This program allows the user to load, display, and save images using a graphical interface built with Tkinter.
It uses OpenCV for image processing and PIL for handling images in the Tkinter GUI.

Authors: Darren Swann, Brayden Brown, Rijan Koirala and Jaafar Mehydeen
Last Updated: 24/01/2025

Features:
- Load an image from the user's system.
- Display the image in a Tkinter canvas.
- Crop the image (Work in progress)
- Save the image to a specified location.
"""

import tkinter as tk # Import for the GUI development
from tkinter import filedialog # Import the module for file selection dialogs
import cv2 # Import for image processing
from PIL import Image, ImageTk #Import for image conversion and manipulation
import numpy as np # Import numerical operations

# Define class for the simple image app
class SimpleImageApp:
    def __init__(self, root):
        """
        Initialise the Simple Image App with GUI

        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Simple Image App") # Set the window title
     
        self.image = None # Placeholder for the loaded image
        self.cropped_image = None # Placeholder for cropped images

        # Create a button to load an image
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10) # Add padding around the button

        # Create a canvas to display the image
        self.canvas = tk.Canvas(root, width=500, height=450, bg="lightgray")
        self.canvas.pack() # Place the canvas in the window

        # Create a button to save the loaded image
        self.save_button = tk.Button(root, text="Save Image", command=self.save_image, state="disabled")
        self.save_button.pack(pady=10) # Add padding around the button
 
    def load_image(self):
        """
        Load an image file selected by the user, resize it, and display it on the canvas.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.image = cv2.imread(file_path) # Read the image using OpenCV
            self.image = cv2.resize(self.image, (500, 450)) # Resize the image to fit the canvas
            self.display_image() # Display the image on the canvas
 
    def display_image(self):
        """
        Convert the OpenCV image to a format suitable for Tkinter and display it on the canvas.
        """
        image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB) # Convert BGR to RGB
        image_pil = Image.fromarray(image_rgb) # Convert the image to a PIL image
        image_tk = ImageTk.PhotoImage(image_pil) # Convert the PIL image to an ImageTk object
        self.canvas.create_image(0, 0, anchor="nw", image=image_tk) # Place the image on the canvas
        self.canvas.image_tk = image_tk # Keep a reference
        self.save_button["state"] = "normal" # Enable the save button
 
    def save_image(self):
        """
        Save the currently loaded image to a file specified by the user.
        """
        if self.image is not None:
            # Open a save dialog to get the file path for saving
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                cv2.imwrite(file_path, self.image) # Save the image using OpenCV
                tk.messagebox.showinfo("Save Image", "Image saved successfully!") # Show a success message

# Entry for the program
if __name__ == "__main__":
    root = tk.Tk() # Create the main Tkinter window
    app = SimpleImageApp(root) # Instantiate the app
    root.mainloop() # Start the Tkinter event loop

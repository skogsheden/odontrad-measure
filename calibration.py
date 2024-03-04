from tkinter import filedialog, simpledialog, messagebox
import math
import os
import json


def set_pixels_per_mm(self):
    pixels_per_mm = simpledialog.askfloat("Ange pixlar per mm", "Ange antal pixlar per millimeter:")
    if pixels_per_mm:
        self.pixels_per_mm = pixels_per_mm
        messagebox.showinfo("Pixlar per mm inställda",
                            f"Pixlar per mm inställda till: {pixels_per_mm:.2f} vilket motsvarar pixelstorleken {1 / pixels_per_mm:.2f}")
        self.calibration_done = True
        self.save_calibration_data()


def set_pixels_size(self):
    pixels_size = simpledialog.askfloat("Ange pixelstorlek", "Ange storleken på pixlarna i millimeter:")
    if pixels_size:
        self.pixels_per_mm = 1 / pixels_size
        messagebox.showinfo("Pixelstorleken inställd",
                            f"Pixelstorleken är inställd till  {pixels_size} vilket motsvarar {self.pixels_per_mm:.2f} pixlar per mm ")
        self.calibration_done = True
        self.save_calibration_data()


def calibrate_pixels_to_mm(self):
    if self.image:
        self.calibration_done = False
        self.canvas.bind("<Button-1>", lambda event: self.calibrate_click(event))
        messagebox.showinfo("Kalibrering",
                            "Tryck ned vänster musknapp dra en linje över ett objekt med en känd längd.")
        self.calibration_active = True
        self.reset_canvas()


def calibrate_click(self, event):
    self.measure1 = (event.x, event.y)
    self.canvas.bind("<B1-Motion>", self.calibrate_motion)
    self.canvas.bind("<ButtonRelease-1>", self.calibrate_release)


def calibrate_motion(self, event):
    self.measure2 = (event.x, event.y)
    if self.blue_lines:
        self.canvas.delete(self.blue_lines[-1])
    line = self.canvas.create_line(self.measure1[0], self.measure1[1], self.measure2[0], self.measure2[1],
                                   fill="red", width=2)
    self.blue_lines.append(line)


def calibrate_release(self, event):
    self.canvas.unbind("<B1-Motion>")
    self.canvas.unbind("<ButtonRelease-1>")

    distance_pixels = math.sqrt(
        (self.measure2[0] - self.measure1[0]) ** 2 + (self.measure2[1] - self.measure1[1]) ** 2)
    distance_mm = simpledialog.askfloat("Kalibrering",
                                        "Skriv in sträckan som den den röda linjen motsvarar i millimeter:")
    if distance_mm:
        self.pixels_per_mm = distance_pixels / distance_mm
        messagebox.showinfo("Kalibrering", f"Pixlar per mm enligt kalibrering: {self.pixels_per_mm:.2f}")
        self.calibration_done = True
        self.calibration_active = False
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))  # Rebind left-click event
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))  # Rebind right-click event
        self.save_calibration_data()
    self.reset_canvas()


def save_calibration_data(self):
    if self.calibration_done and self.image_filepath:
        # Extract the filename and directory from the image filepath
        filepath, filename = os.path.split(self.image_filepath)
        # Remove the extension from the filename
        filename_no_ext = os.path.splitext(filename)[0]
        # Create the calibration filepath with the same directory and filename but different extension
        calibration_filepath = os.path.join(filepath, filename_no_ext + ".calib")

        # Create a dictionary with calibration data
        calibration_data = {
            "pixels_per_mm": self.pixels_per_mm
        }

        # Save calibration data to file
        with open(calibration_filepath, "w") as calib_file:
            json.dump(calibration_data, calib_file)


def load_calibration_data(self):
    if self.image_filepath:
        # Extract the filename and directory from the image filepath
        filepath, filename = os.path.split(self.image_filepath)
        # Remove the extension from the filename
        filename_no_ext = os.path.splitext(filename)[0]
        # Create the calibration filepath with the same directory and filename but different extension
        calibration_filepath = os.path.join(filepath, filename_no_ext + ".calib")

        # Check if the calibration file exists
        if os.path.exists(calibration_filepath):
            # Load calibration data from file
            with open(calibration_filepath, "r") as calib_file:
                calibration_data = json.load(calib_file)
                pixels_per_mm = calibration_data.get("pixels_per_mm")
                if pixels_per_mm:
                    print(f"Laddar sparad kalibrering för {filename}: {pixels_per_mm:.2f} pixlar per mm")
                else:
                    print(f"Ingen sparad kalibrering för{filename}")
        else:
            print(f"Ingen sparad kalibrering för {filename}")

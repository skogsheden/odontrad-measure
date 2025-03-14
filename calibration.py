from tkinter import filedialog, simpledialog, messagebox
import math
import os
import json


def set_pixels_per_mm(self):
    pixels_per_mm = simpledialog.askfloat("Enter pixels per mm", "Enter number of pixels per millimeter:")
    if pixels_per_mm:
        self.pixels_per_mm = pixels_per_mm
        messagebox.showinfo("Pixels per mm set",
                            f"Pixels per mm set to: {pixels_per_mm:.2f} which corresponds to pixel size {1 / pixels_per_mm:.2f}")
        self.calibration_done = True
        self.save_calibration_data()


def set_pixels_size(self):
    pixels_size = simpledialog.askfloat("Enter pixel size", "Enter the size of pixels in millimeters:")
    if pixels_size:
        self.pixels_per_mm = 1 / pixels_size
        messagebox.showinfo("Pixel size set",
                            f"The pixel size is set to {pixels_size} which corresponds to {self.pixels_per_mm:.2f} pixels per mm")
        self.calibration_done = True
        self.save_calibration_data()


def calibrate_pixels_to_mm(self):
    if self.image:
        self.calibration_done = False
        self.canvas.bind("<Button-1>", lambda event: self.calibrate_click(event))
        messagebox.showinfo("Calibration",
                            "Press the left mouse button and drag a line over an object with a known length.")
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
    self.measure1 = (int(self.measure1[0] * self.image_scale_x), int(self.measure1[1] * self.image_scale_y))
    self.measure2 = (int(self.measure2[0] * self.image_scale_x), int(self.measure2[1] * self.image_scale_y))

    distance_pixels = math.sqrt(
        (self.measure2[0] - self.measure1[0]) ** 2 + (self.measure2[1] - self.measure1[1]) ** 2)
    distance_mm = simpledialog.askfloat("Calibration",
                                        "Enter the distance that the red line represents in millimeters:")
    if distance_mm:
        self.pixels_per_mm = distance_pixels / distance_mm
        messagebox.showinfo("Calibration", f"Pixels per mm according to calibration: {self.pixels_per_mm:.2f}")
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
                self.pixels_per_mm = calibration_data.get("pixels_per_mm")
                if self.pixels_per_mm:
                    print(f"Loading saved calibration for {filename}: {self.pixels_per_mm:.2f} pixels per mm")
                    self.calibration_done = True
                else:
                    print(f"No saved calibration for {filename}")
        else:
            print(f"No saved calibration for {filename}")
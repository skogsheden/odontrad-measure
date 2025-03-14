__author__ = "Nils Gustafsson"
__copyright__ = "Copyright 2025, Skogsheden"
__license__ = "GPL 3.0"
__version__ = "0.2.1"
__maintainer__ = "Nils Gustafsson"
__email__ = "nils.gustafsson@umu.se"
__status__ = "Development"

# Executable built with command: pyinstaller --name 'odontrad-measure' --icon 'icon.ico' --windowed main.py -F

import tkinter as tk
from tkinter import messagebox
import random
from PIL import ImageTk, Image, ImageEnhance
import math
import json
import os
# Import from other files
import settings
import annotation
import measurment
import calibration
import save_data
import load_data


class XrayMeasure:
    def __init__(self, master):
        self.master = master
        self.master.title("OdontRad - Measure")

        # Set initial window size to ensure menu fits
        self.master.minsize(640, 480)  # Minimum window size

        # Canvas
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_image = None

        # Image load
        self.image_list = {}
        self.image_current_id = 0
        self.image = None
        self.photo_image = None
        self.image_filename = None
        self.image_filepath = None
        self.image_scale_x = 1
        self.image_scale_y = 1

        # Add these zoom-related attributes
        self.zoom_factor = 1.0
        self.original_image = None
        self.image_x_offset = 0
        self.image_y_offset = 0
        self.dragging_image = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.current_adjustments = {'brightness': 1.0, 'contrast': 1.0, 'sharpness': 1.0}

        # Calibration
        self.pixels_per_mm = None
        self.calibration_done = False
        self.calibration_active = False

        # Draw and measure
        self.measurements_active = False
        self.draw = None
        self.measure1 = None
        self.measure2 = None
        self.blue_lines = []
        self.green_lines = []
        self.saved_lines = []
        self.measurements = {"blue": [], "green": []}  # Separate measurements for blue and green lines
        self.save_measurement_list = []
        self.lines_state = "normal"

        # Settings
        self.username = ""
        self.function1_enabled = tk.BooleanVar(value=False)  # Fråga om tandyta: Aktiverad
        self.function2_enabled = tk.BooleanVar(value=False)  # Behåll linjer: Aktiverad

        # Annotation
        self.annotation_active = False
        self.annotation_start_point = None
        self.annotation_end_point = None
        self.rectangles = []
        self.annotation_current_color = 'red'
        self.annotation_previous_color = 'red'
        self.colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
        self.annotate_angle = False

        # Menu
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open image (o)", command=self.open_image)
        file_menu.add_command(label="Open folder (p)", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Export measurements", command=self.save_measurements_to_file)
        file_menu.add_command(label="Import measurements", command=self.load_measurements_from_file)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings_window)
        file_menu.add_separator()
        file_menu.add_command(label="Exit (q)", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)

        image_menu = tk.Menu(menubar, tearoff=0)
        image_menu.add_command(label="Next image (n)", command=self.open_next)
        image_menu.add_command(label="Previous image (b)", command=self.open_prev)
        image_menu.add_command(label="Adjustment", command=self.adjust_brightness_contrast)
        image_menu.add_separator()
        image_menu.add_command(label="Zoom in (+)", command=self.zoom_in)
        image_menu.add_command(label="Zoom out (-)", command=self.zoom_out)
        image_menu.add_command(label="Reset zoom (0)", command=self.reset_zoom)
        menubar.add_cascade(label="Image", menu=image_menu)

        mesaurment_menu = tk.Menu(menubar, tearoff=0)
        mesaurment_menu.add_command(label="Hide/show (g)", command=self.toggle_lines_visibility)
        mesaurment_menu.add_command(label="Show saved (v)", command=self.show_saved_measurements)
        mesaurment_menu.add_command(label="Clear saved", command=self.clear_all_saved)
        menubar.add_cascade(label="Measurements", menu=mesaurment_menu)
        mesaurment_menu.add_command(label="Adjust line", command=self.adjust_line)

        annotation_menu = tk.Menu(menubar, tearoff=0)
        annotation_menu.add_command(label="Start/stop (a)", command=self.toggle_annotate)
        annotation_menu.add_separator()
        annotation_menu.add_command(label="Save empty(Space)",
                                    command=self.save_blank_and_next)
        annotation_menu.add_command(label="Hide/show (h)", command=self.toggle_rectangles_visibility)
        menubar.add_cascade(label="Annotation", menu=annotation_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Calibrate in image (c)", command=self.calibrate_pixels_to_mm)
        settings_menu.add_command(label="Pixels/mm", command=self.set_pixels_per_mm)
        settings_menu.add_command(label="Pixel size", command=self.set_pixels_size)
        menubar.add_cascade(label="Calibration", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Keyboard shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_program_info)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Bind keyboard shortcuts
        self.master.bind("q", self.exit)
        self.master.bind("a", self.toggle_annotate)
        self.master.bind("o", self.open_image)
        self.master.bind("g", self.toggle_lines_visibility)
        self.master.bind("s", self.save_measurement)
        self.master.bind("v", self.show_saved_measurements)
        self.master.bind("c", self.calibrate_pixels_to_mm)
        self.master.bind("h", lambda event: self.toggle_rectangles_visibility())
        self.master.bind("n", self.open_next)
        self.master.bind("b", self.open_prev)
        self.master.bind("p", self.open_folder)
        self.master.bind("<space>", lambda event: self.save_blank_and_next())
        self.master.bind("+", self.zoom_in)
        self.master.bind("-", self.zoom_out)
        self.master.bind("0", self.reset_zoom)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.mouse_wheel_zoom)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.mouse_wheel_zoom)  # Linux scroll down
        self.canvas.bind("<ButtonPress-2>", self.start_image_drag)  # Middle mouse button
        self.canvas.bind("<B2-Motion>", self.drag_image)
        self.canvas.bind("<ButtonRelease-2>", self.stop_image_drag)

        # Load settings from file
        settings.load_settings(self)

    def auto_save_measurements_as_json(self):
        """
        Automatically save measurements to a JSON file with the naming convention
        filename_measurements.json in the same directory as the image.
        """
        if self.save_measurement_list and self.image_filepath:
            # Create filename for the JSON file (image filename + _measurements.json)
            base_filename = os.path.splitext(self.image_filepath)[0]
            json_file_path = f"{base_filename}_measurements.json"

            # Filter measurements for current image only
            current_image_measurements = [
                measurement for measurement in self.save_measurement_list
                if measurement.get('filename') == self.image_filename
            ]

            if current_image_measurements:
                with open(json_file_path, "w") as json_file:
                    json.dump(current_image_measurements, json_file, indent=4)
                print(f"Measurements auto-saved to {json_file_path}")
            else:
                print("No measurements for current image to save")

    def auto_load_measurements_from_json(self):
        """
        Automatically load measurements from a JSON file with the naming convention
        filename_measurements.json from the same directory as the image.
        """
        if self.image_filepath:
            # Create expected filename for the JSON file
            base_filename = os.path.splitext(self.image_filepath)[0]
            json_file_path = f"{base_filename}_measurements.json"

            # Check if the file exists
            if os.path.exists(json_file_path):
                try:
                    with open(json_file_path, "r") as json_file:
                        measurements = json.load(json_file)

                    # Add measurements to the save_measurement_list
                    for measurement in measurements:
                        # Check if this measurement is not already in the list
                        is_duplicate = False
                        for existing_measurement in self.save_measurement_list:
                            if (existing_measurement.get('filename') == measurement.get('filename') and
                                    existing_measurement.get('blue_coordinates') == measurement.get(
                                        'blue_coordinates') and
                                    existing_measurement.get('green_coordinates') == measurement.get(
                                        'green_coordinates')):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            self.save_measurement_list.append(measurement)

                    # Draw the measurements on the canvas
                    for measurement in measurements:
                        # Draw blue line if it exists
                        if "blue_coordinates" in measurement and measurement["blue_coordinates"]:
                            blue_coordinates = measurement["blue_coordinates"]
                            self.saved_lines.append(
                                self.canvas.create_line(
                                    blue_coordinates[0][0] / self.image_scale_x,
                                    blue_coordinates[0][1] / self.image_scale_y,
                                    blue_coordinates[1][0] / self.image_scale_x,
                                    blue_coordinates[1][1] / self.image_scale_y,
                                    fill="blue", width=2
                                )
                            )

                        # Draw green line if it exists
                        if "green_coordinates" in measurement and measurement["green_coordinates"]:
                            green_coordinates = measurement["green_coordinates"]
                            self.saved_lines.append(
                                self.canvas.create_line(
                                    green_coordinates[0][0] / self.image_scale_x,
                                    green_coordinates[0][1] / self.image_scale_y,
                                    green_coordinates[1][0] / self.image_scale_x,
                                    green_coordinates[1][1] / self.image_scale_y,
                                    fill="green", width=2
                                )
                            )

                    print(f"Measurements auto-loaded from {json_file_path}")
                    return True
                except Exception as e:
                    print(f"Error loading measurements from JSON: {e}")
                    return False
            else:
                print(f"No measurement JSON file found: {json_file_path}")
                return False
        return False

    def save_blank_and_next(self):
        """Saves a blank annotation and moves to the next image."""
        annotation.save_blank_annotation(self)  # Call the function from annotation.py
        self.open_next()

    def exit(self, event=None):
        settings.save_settings(self)  # Save settings before exiting
        self.master.destroy()

    def zoom_in(self, event=None):
        """Increase zoom factor and redraw the image"""
        if self.image:
            self.zoom_factor *= 1.2
            self.apply_zoom()

    def zoom_out(self, event=None):
        """Decrease zoom factor and redraw the image"""
        if self.image:
            self.zoom_factor /= 1.2
            # Don't allow zooming out too far
            if self.zoom_factor < 0.1:
                self.zoom_factor = 0.1
            self.apply_zoom()

    def reset_zoom(self, event=None):
        """Reset zoom to the original size"""
        if self.image:
            self.zoom_factor = 1.0
            self.image_x_offset = 0
            self.image_y_offset = 0
            self.apply_zoom()

    def mouse_wheel_zoom(self, event):
        """Handle zooming via mouse wheel, centered around the mouse position"""
        if not self.image:
            return

        # Store old zoom factor for calculations
        old_zoom = self.zoom_factor

        # Get the current mouse position
        mouse_x, mouse_y = event.x, event.y

        # Calculate position relative to image (before zoom change)
        rel_x = (mouse_x - self.image_x_offset) / old_zoom
        rel_y = (mouse_y - self.image_y_offset) / old_zoom

        # Determine zoom direction based on the event
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            # Zoom in
            self.zoom_factor *= 1.1
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            # Zoom out
            self.zoom_factor /= 1.1
            # Don't allow zooming out too far
            if self.zoom_factor < 0.1:
                self.zoom_factor = 0.1

        # Calculate new offset to keep the point under the cursor at the same place
        new_x_offset = mouse_x - (rel_x * self.zoom_factor)
        new_y_offset = mouse_y - (rel_y * self.zoom_factor)

        # Update offsets
        self.image_x_offset = new_x_offset
        self.image_y_offset = new_y_offset

        # Apply the zoom with the new offsets
        self.apply_zoom()

    def apply_zoom(self):
        """Apply the current zoom factor to the image"""
        if not self.image:
            return

        # Store the original image on first zoom
        if self.original_image is None:
            self.original_image = self.image

        # Calculate new dimensions
        width = int(self.original_image.width * self.zoom_factor)
        height = int(self.original_image.height * self.zoom_factor)

        # Resize the image
        resized_image = self.original_image.resize((width, height), Image.LANCZOS)

        # Apply any active adjustments (brightness, contrast, etc.)
        if hasattr(self, 'current_adjustments'):
            brightness = self.current_adjustments.get('brightness', 1.0)
            contrast = self.current_adjustments.get('contrast', 1.0)
            sharpness = self.current_adjustments.get('sharpness', 1.0)

            contrast_img = ImageEnhance.Contrast(resized_image)
            adjusted_image = contrast_img.enhance(contrast)
            brightness_img = ImageEnhance.Brightness(adjusted_image)
            adjusted_image = brightness_img.enhance(brightness)
            sharpness_img = ImageEnhance.Sharpness(adjusted_image)
            resized_image = sharpness_img.enhance(sharpness)

        self.photo_image = ImageTk.PhotoImage(resized_image)

        # Update the image on the canvas
        if self.canvas_image:
            self.canvas.delete(self.canvas_image)

        # Position the image with offset
        self.canvas_image = self.canvas.create_image(
            self.image_x_offset, self.image_y_offset,
            anchor=tk.NW, image=self.photo_image
        )

        # Update scale factors for measurements - kritisk för korrekt ritning av linjer
        if self.original_image:
            original_width = self.original_image.width
            original_height = self.original_image.height
            self.image_scale_x = original_width / width
            self.image_scale_y = original_height / height
            print(f"Scale factors updated: x={self.image_scale_x}, y={self.image_scale_y}")

        # Redraw existing lines and rectangles with new scale
        self.redraw_annotations_and_measurements()

    def clear_all_lines(self):
        """Ta bort alla linjer från canvas och rensa listorna"""
        # Ta bort alla linjer från canvas
        for line in self.saved_lines:
            self.canvas.delete(line)
        for line in self.blue_lines:
            self.canvas.delete(line)
        for line in self.green_lines:
            self.canvas.delete(line)

        # Rensa listorna
        self.saved_lines = []
        self.blue_lines = []
        self.green_lines = []

    def redraw_annotations_and_measurements(self):
        """Ritar om alla markeringar och mätlinjer efter zoom-ändring"""
        # Rensa först bort alla befintliga linjer
        self.clear_all_lines()

        # Ta bort alla mätningsetiketter
        self.canvas.delete("measurement_label")

        # Rensa bort alla rektanglar
        for rect_data in self.rectangles:
            if "rect" in rect_data:
                self.canvas.delete(rect_data["rect"])
            if "text" in rect_data:
                self.canvas.delete(rect_data["text"])

        # Rita sparade linjer från mätdata
        for measurement in self.save_measurement_list:
            # Rita blå linje om den finns i mätningen
            if 'blue_coordinates' in measurement:
                coords = measurement['blue_coordinates']
                # Konvertera originalkoordinater till nuvarande displaykoordinater
                x1 = coords[0][0] / self.image_scale_x + self.image_x_offset
                y1 = coords[0][1] / self.image_scale_y + self.image_y_offset
                x2 = coords[1][0] / self.image_scale_x + self.image_x_offset
                y2 = coords[1][1] / self.image_scale_y + self.image_y_offset

                new_line = self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="saved_line")
                self.saved_lines.append(new_line)

                # Visa mätning som etikett bredvid linjen
                if 'blue_length_pixels' in measurement:
                    pixels = measurement['blue_length_pixels']
                    text = f"{pixels:.1f} px"
                    if 'blue_length_mm' in measurement:
                        mm = measurement['blue_length_mm']
                        text = f"{pixels:.1f} px / {mm:.1f} mm"

            # Rita grön linje om den finns i mätningen
            if 'green_coordinates' in measurement:
                coords = measurement['green_coordinates']
                # Konvertera originalkoordinater till nuvarande displaykoordinater
                x1 = coords[0][0] / self.image_scale_x + self.image_x_offset
                y1 = coords[0][1] / self.image_scale_y + self.image_y_offset
                x2 = coords[1][0] / self.image_scale_x + self.image_x_offset
                y2 = coords[1][1] / self.image_scale_y + self.image_y_offset

                new_line = self.canvas.create_line(x1, y1, x2, y2, fill="green", width=2, tags="saved_line")
                self.saved_lines.append(new_line)

                # Visa mätning som etikett bredvid linjen
                if 'green_length_pixels' in measurement:
                    pixels = measurement['green_length_pixels']
                    text = f"{pixels:.1f} px"
                    if 'green_length_mm' in measurement:
                        mm = measurement['green_length_mm']
                        text = f"{pixels:.1f} px / {mm:.1f} mm"

        # Rita aktiva blå linjer
        for coords in self.measurements["blue"]:
            # Konvertera originalkoordinater till nuvarande displaykoordinater
            x1 = coords[0][0] / self.image_scale_x + self.image_x_offset
            y1 = coords[0][1] / self.image_scale_y + self.image_y_offset
            x2 = coords[1][0] / self.image_scale_x + self.image_x_offset
            y2 = coords[1][1] / self.image_scale_y + self.image_y_offset

            new_line = self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="blue_line")
            self.blue_lines.append(new_line)

            # Beräkna och visa mätning
            distance_pixels = math.sqrt((coords[1][0] - coords[0][0]) ** 2 + (coords[1][1] - coords[0][1]) ** 2)
            if self.calibration_done:
                distance_mm = distance_pixels / self.pixels_per_mm
                text = f"{distance_pixels:.1f} px / {distance_mm:.1f} mm"
            else:
                text = f"{distance_pixels:.1f} px"

        # Rita aktiva gröna linjer
        for coords in self.measurements["green"]:
            # Konvertera originalkoordinater till nuvarande displaykoordinater
            x1 = coords[0][0] / self.image_scale_x + self.image_x_offset
            y1 = coords[0][1] / self.image_scale_y + self.image_y_offset
            x2 = coords[1][0] / self.image_scale_x + self.image_x_offset
            y2 = coords[1][1] / self.image_scale_y + self.image_y_offset

            new_line = self.canvas.create_line(x1, y1, x2, y2, fill="green", width=2, tags="green_line")
            self.green_lines.append(new_line)

            # Beräkna och visa mätning
            distance_pixels = math.sqrt((coords[1][0] - coords[0][0]) ** 2 + (coords[1][1] - coords[0][1]) ** 2)
            if self.calibration_done:
                distance_mm = distance_pixels / self.pixels_per_mm
                text = f"{distance_pixels:.1f} px / {distance_mm:.1f} mm"
            else:
                text = f"{distance_pixels:.1f} px"

        # Rita rektanglar (markeringar)
        for rect_data in self.rectangles:
            if "coordinates" in rect_data:
                coords = rect_data["coordinates"]
                x1 = coords[0][0] / self.image_scale_x + self.image_x_offset
                y1 = coords[0][1] / self.image_scale_y + self.image_y_offset
                x2 = coords[1][0] / self.image_scale_x + self.image_x_offset
                y2 = coords[1][1] / self.image_scale_y + self.image_y_offset

                new_rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline=rect_data["color"], tags="annotation")

                text_x = min(x1, x2)
                text_y = min(y1, y2)
                new_text = self.canvas.create_text(
                    text_x, text_y,
                    text=rect_data["tooth_id"],
                    anchor=tk.NW,
                    fill=rect_data["color"],
                    tags="annotation_text"
                )

                rect_data["rect"] = new_rect
                rect_data["text"] = new_text

    def start_image_drag(self, event):
        """Start dragging the image for panning"""
        if self.zoom_factor > 1.0:  # Only enable panning when zoomed in
            self.dragging_image = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def drag_image(self, event):
        """Update image position during drag"""
        if self.dragging_image:
            # Calculate the movement
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y

            # Update the start position for next movement
            self.drag_start_x = event.x
            self.drag_start_y = event.y

            # Update image offset
            self.image_x_offset += dx
            self.image_y_offset += dy

            # Move the image on the canvas
            self.canvas.move(self.canvas_image, dx, dy)

            # Move all lines and annotations
            for line in self.saved_lines + self.blue_lines + self.green_lines:
                self.canvas.move(line, dx, dy)

            for rect_data in self.rectangles:
                if "rect" in rect_data and "text" in rect_data:
                    self.canvas.move(rect_data["rect"], dx, dy)
                    self.canvas.move(rect_data["text"], dx, dy)

    def stop_image_drag(self, event):
        """Stop dragging the image"""
        self.dragging_image = False

    # Modify apply_adjustments to store current adjustment settings
    def apply_adjustments(self, brightness, contrast, sharpness):
        if self.image:
            # Store current adjustment values
            self.current_adjustments = {
                'brightness': brightness,
                'contrast': contrast,
                'sharpness': sharpness
            }

            if self.original_image:
                # If we're zoomed, apply adjustments to the zoomed version
                self.apply_zoom()
            else:
                # Original adjustment logic
                contrast_img = ImageEnhance.Contrast(self.image)
                adjusted_image = contrast_img.enhance(contrast)
                brightness_img = ImageEnhance.Brightness(adjusted_image)
                adjusted_image = brightness_img.enhance(brightness)
                sharpness_img = ImageEnhance.Sharpness(adjusted_image)
                adjusted_image = sharpness_img.enhance(sharpness)
                self.photo_image = ImageTk.PhotoImage(adjusted_image)

                # Update canvas image
                if self.canvas_image:
                    self.canvas.itemconfig(self.canvas_image, image=self.photo_image)

    def adjust_brightness_contrast(self):
        adjust_window = tk.Toplevel(self.master)
        adjust_window.title("Adjust brightness, contras and sharpness")

        initial_brightness = 1.0  # Initial brightness
        initial_contrast = 1.0  # Initial contrast
        initial_sharpness = 1.0  # Initial sharpness

        brightness_label = tk.Label(adjust_window, text="Brightness")
        brightness_label.grid(row=0, column=0, padx=10, pady=5)
        brightness_slider = tk.Scale(adjust_window, from_=0, to=400, orient=tk.HORIZONTAL,
                                     command=lambda value: self.apply_adjustments(float(value) / 100,
                                                                                  float(contrast_slider.get()) / 100,
                                                                                  float(sharpness_slider.get()) / 100))
        brightness_slider.set(initial_brightness * 100)
        brightness_slider.grid(row=0, column=1, padx=10, pady=5)

        contrast_label = tk.Label(adjust_window, text="Contrast")
        contrast_label.grid(row=1, column=0, padx=10, pady=5)
        contrast_slider = tk.Scale(adjust_window, from_=0, to=400, orient=tk.HORIZONTAL,
                                   command=lambda value: self.apply_adjustments(float(brightness_slider.get()) / 100,
                                                                                float(value) / 100,
                                                                                float(sharpness_slider.get()) / 100))
        contrast_slider.set(initial_contrast * 100)
        contrast_slider.grid(row=1, column=1, padx=10, pady=5)

        sharpness_label = tk.Label(adjust_window, text="Sharpness")
        sharpness_label.grid(row=2, column=0, padx=10, pady=5)
        sharpness_slider = tk.Scale(adjust_window, from_=0, to=400, orient=tk.HORIZONTAL,
                                    command=lambda value: self.apply_adjustments(float(brightness_slider.get()) / 100,
                                                                                 float(contrast_slider.get()) / 100,
                                                                                 float(value) / 100))
        sharpness_slider.set(initial_sharpness * 100)
        sharpness_slider.grid(row=2, column=1, padx=10, pady=5)

        reset_button = tk.Button(adjust_window, text="Reset",
                                 command=lambda: self.reset_adjustments(brightness_slider, contrast_slider,
                                                                        sharpness_slider))
        reset_button.grid(row=3, column=0, columnspan=2, pady=10)

    def reset_adjustments(self, brightness_slider, contrast_slider, sharpness_slider):
        brightness_slider.set(100)
        contrast_slider.set(100)
        sharpness_slider.set(100)
        self.apply_adjustments(1.0, 1.0, 1.0)  # Reset adjustments to default values

    # Load data
    def open_image(self, event=None):
        """Öppna en bild och se till att alla mätningar rensas"""
        # Rensa alla mätningsrelaterade data
        self.rectangles.clear()
        self.clear_all_lines()
        self.measurements = {"blue": [], "green": []}  # Rensa aktiva mätningar
        self.save_measurement_list = []  # Rensa sparade mätningar
        self.canvas.delete("measurement_label")  # Ta bort alla mätningsetiketter

        # Återställ bild- och zoomrelaterade variabler
        self.original_image = None
        self.zoom_factor = 1.0
        self.image_x_offset = 0
        self.image_y_offset = 0

        # Öppna bilden
        load_data.open_image(self)

        # Se till att original-bilden är korrekt inställd
        if self.image and not self.original_image:
            self.original_image = self.image

        # Uppdatera skala baserat på original-bildens storlek
        if self.original_image:
            # Säkerställ att skalningsfaktorerna är 1.0 vid start
            self.image_scale_x = 1.0
            self.image_scale_y = 1.0

        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))

    def open_folder(self, event=None):
        """Öppna en mapp med bilder och se till att alla mätningar rensas"""
        # Rensa alla mätningsrelaterade data
        self.rectangles.clear()
        self.clear_all_lines()
        self.measurements = {"blue": [], "green": []}  # Rensa aktiva mätningar
        self.save_measurement_list = []  # Rensa sparade mätningar
        self.canvas.delete("measurement_label")  # Ta bort alla mätningsetiketter

        # Återställ bild- och zoomrelaterade variabler
        self.original_image = None
        self.zoom_factor = 1.0
        self.image_x_offset = 0
        self.image_y_offset = 0

        # Öppna mappen
        load_data.load_images_from_folder(self)
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
        load_data.open_image_from_list(self, self.image_current_id)

    def open_next(self, event=None):
        """Öppna nästa bild och rensa aktiva mätningar (behåll sparade)"""
        if len(self.image_list) > 0:
            if self.image_current_id < len(self.image_list):
                self.image_current_id = self.image_current_id + 1

                # Rensa aktiva mätningar, men behåll sparade
                self.rectangles.clear()
                for line in self.blue_lines + self.green_lines:
                    self.canvas.delete(line)
                self.blue_lines = []
                self.green_lines = []
                self.measurements = {"blue": [], "green": []}
                self.canvas.delete("measurement_label")  # Ta bort temporära mätningsetiketter

                # Återställ bild- och zoomrelaterade variabler
                self.original_image = None
                self.zoom_factor = 1.0
                self.image_x_offset = 0
                self.image_y_offset = 0

                self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
                self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
                load_data.open_image_from_list(self, self.image_current_id)
                self.annotation_active = False
            else:
                print("Last image")
        else:
            print("No images loaded")

    def open_prev(self, event=None):
        """Öppna föregående bild och rensa aktiva mätningar (behåll sparade)"""
        if len(self.image_list) > 0:
            if self.image_current_id > 0:
                self.image_current_id = self.image_current_id - 1

                # Rensa aktiva mätningar, men behåll sparade
                self.rectangles.clear()
                for line in self.blue_lines + self.green_lines:
                    self.canvas.delete(line)
                self.blue_lines = []
                self.green_lines = []
                self.measurements = {"blue": [], "green": []}
                self.canvas.delete("measurement_label")  # Ta bort temporära mätningsetiketter

                # Återställ bild- och zoomrelaterade variabler
                self.original_image = None
                self.zoom_factor = 1.0
                self.image_x_offset = 0
                self.image_y_offset = 0

                self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
                self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
                load_data.open_image_from_list(self, self.image_current_id)
                self.annotation_active = False
            else:
                print("First image")
        else:
            print("No images loaded")

    def load_measurements_from_file(self):
        load_data.load_measurements_from_file(self)

    def load_annotations(self):
        annotation.load_annotations(self)

    def load_calibration_data(self):
        calibration.load_calibration_data(self)

    # Settings
    def show_program_info(self):
        settings.show_program_info(self)

    def show_shortcuts(self):
        settings.show_shortcuts(self)

    def open_settings_window(self):
        settings.open_settings_window(self)

    def save_user(self):
        settings.save_user(self)

    def save_settings(self):
        settings.save_settings(self)

    def clear_all_saved(self):
        settings.clear_all_saved(self)

    def reset_canvas(self):
        settings.reset_canvas(self)

    def save_measurements_to_file(self):
        save_data.save_measurements_to_file(self)

    # Calibration
    def set_pixels_per_mm(self):
        calibration.set_pixels_size(self)

    def set_pixels_size(self):
        calibration.set_pixels_size(self)

    def calibrate_pixels_to_mm(self, event=None):
        calibration.calibrate_pixels_to_mm(self)

    def calibrate_click(self, event):
        calibration.calibrate_click(self, event)

    def calibrate_motion(self, event):
        calibration.calibrate_motion(self, event)

    def calibrate_release(self, event):
        calibration.calibrate_release(self, event)

    def save_calibration_data(self):
        calibration.save_calibration_data(self)

    # Measurement
    def adjust_line(self, event=None):
        measurment.adjust_line(self, event)

    def prepare_line_adjustment(self, measurement_idx, line_color, select_window):
        measurment.prepare_line_adjustment(self, measurement_idx, line_color, select_window)

    def apply_line_adjustment(self, measurement_idx, line_color, start_x, start_y, end_x, end_y, window, canvas_items):
        measurment.apply_line_adjustment(self, measurement_idx, line_color, start_x, start_y, end_x, end_y, window,
                                         canvas_items)

    def cancel_line_adjustment(self, window, canvas_items):
        measurment.cancel_line_adjustment(self, window, canvas_items)

    def click(self, event, button):
        measurment.click(self, event, button)

    def motion(self, event, color):
        measurment.motion(self, event, color)

    def release(self, event, color):
        measurment.release(self, event, color)

    def save_measurement(self, event=None):
        measurment.save_measurement(self, event=None)

    def show_saved_measurements(self, event=None):
        measurment.show_saved_measurements(self)

    def toggle_lines_visibility(self, event=None):
        measurment.toggle_lines_visibility(self)

    # Annotation
    def toggle_annotate(self, event=None):
        if self.annotation_active == False:
            self.annotation_active = True
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Button-3>")
            self.canvas.bind("<Button-1>", self.start_rectangle)
            self.canvas.bind("<B1-Motion>", self.draw_rectangle)
            self.canvas.bind("<ButtonRelease-1>", self.end_rectangle)
            self.canvas.bind("<Button-3>", self.delete_last_rectangle)
            messagebox.showinfo("BBox annotation",
                                "Press the left mouse button and mark the areas you want to annotate.\n"
                                "Right mouse button deletes the latest annotation.\n"
                                "Press Escape to exit annotation.")
        else:
            self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
            self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
            self.annotation_active = False

    def start_rectangle(self, event):
        annotation.start_rectangle(self, event)

    def draw_rectangle(self, event):
        annotation.draw_rectangle(self, event)

    def end_rectangle(self, event):
        annotation.end_rectangle(self, event)

    def generate_random_color(self):
        color_options = [color for color in self.colors if color != self.annotation_previous_color]
        return random.choice(color_options)

    def delete_last_rectangle(self, event):
        annotation.delete_last_rectangle(self, event)

    def toggle_rectangles_visibility(self):
        annotation.toggle_rectangles_visibility(self)

    def save_annotations(self):
        annotation.save_annotations(self)


def main():
    root = tk.Tk()
    app = XrayMeasure(root)
    root.mainloop()


if __name__ == "__main__":
    main()

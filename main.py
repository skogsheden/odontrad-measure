__author__ = "Nils Gustafsson"
__copyright__ = "Copyright 2024, Skogsheden"
__license__ = "GPL 3.0"
__version__ = "0.1.5"
__maintainer__ = "Nils Gustafsson"
__email__ = "nils.gustafsson@umu.se"
__status__ = "Development"

# Executable built with command: pyinstaller --name 'odontrad-measure' --icon 'icon.ico' --windowed main.py -F

import tkinter as tk
from tkinter import messagebox
import random
from PIL import ImageTk, Image, ImageEnhance
import cv2

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
        self.master.title("OdontRad - Mätverktyg")

        # Canvas
        self.canvas = tk.Canvas(self.master, cursor="cross")
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
        file_menu.add_command(label="Öppna bild (o)", command=self.open_image)
        file_menu.add_command(label="Öppna mapp (p)", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exportera mätningar", command=self.save_measurements_to_file)
        file_menu.add_command(label="Importera mätningar", command=self.load_measurements_from_file)
        file_menu.add_separator()
        file_menu.add_command(label="Inställningar", command=self.open_settings_window)
        file_menu.add_separator()
        file_menu.add_command(label="Avsluta (q)", command=self.exit)
        menubar.add_cascade(label="Arkiv", menu=file_menu)

        image_menu = tk.Menu(menubar, tearoff=0)
        image_menu.add_command(label="Nästa bild (n)", command=self.open_next)
        image_menu.add_command(label="Föregående bild (b)", command=self.open_prev)
        image_menu.add_command(label="Bildjustering", command=self.adjust_brightness_contrast)
        menubar.add_cascade(label="Bild", menu=image_menu)

        mesaurment_menu = tk.Menu(menubar, tearoff=0)
        mesaurment_menu.add_command(label="Dölj/Visa (g)", command=self.toggle_lines_visibility)
        mesaurment_menu.add_command(label="Visa sparade (v)", command=self.show_saved_measurements)
        mesaurment_menu.add_command(label="Rensa sparade", command=self.clear_all_saved)
        menubar.add_cascade(label="Mätningar", menu=mesaurment_menu)

        annotation_menu = tk.Menu(menubar, tearoff=0)
        annotation_menu.add_command(label="Starta/stoppa (a)", command=self.toggle_annotate)
        annotation_menu.add_separator()
        annotation_menu.add_command(label="Dölj/Visa (h)", command=self.toggle_rectangles_visibility)
        menubar.add_cascade(label="Annotering", menu=annotation_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Kalibrera i bilden (c)", command=self.calibrate_pixels_to_mm)
        settings_menu.add_command(label="Ange pixlar per mm", command=self.set_pixels_per_mm)
        settings_menu.add_command(label="Ange pixelstorlek", command=self.set_pixels_size)
        menubar.add_cascade(label="Kalibrering", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kortkommandon", command=self.show_shortcuts)
        help_menu.add_command(label="Om", command=self.show_program_info)
        menubar.add_cascade(label="Hjälp", menu=help_menu)

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

        # Load settings from file
        settings.load_settings(self)

    def exit(self, event=None):
        settings.save_settings(self)  # Save settings before exiting
        self.master.destroy()

    def adjust_brightness_contrast(self):
        adjust_window = tk.Toplevel(self.master)
        adjust_window.title("Justera ljusstyrka, kontrast och skärpa")

        initial_brightness = 1.0  # Initial brightness
        initial_contrast = 1.0  # Initial contrast
        initial_sharpness = 1.0  # Initial sharpness

        brightness_label = tk.Label(adjust_window, text="Ljusstyrka")
        brightness_label.grid(row=0, column=0, padx=10, pady=5)
        brightness_slider = tk.Scale(adjust_window, from_=0, to=400, orient=tk.HORIZONTAL,
                                     command=lambda value: self.apply_adjustments(float(value) / 100,
                                                                                  float(contrast_slider.get()) / 100,
                                                                                  float(sharpness_slider.get()) / 100))
        brightness_slider.set(initial_brightness * 100)
        brightness_slider.grid(row=0, column=1, padx=10, pady=5)

        contrast_label = tk.Label(adjust_window, text="Kontrast")
        contrast_label.grid(row=1, column=0, padx=10, pady=5)
        contrast_slider = tk.Scale(adjust_window, from_=0, to=400, orient=tk.HORIZONTAL,
                                   command=lambda value: self.apply_adjustments(float(brightness_slider.get()) / 100,
                                                                                float(value) / 100,
                                                                                float(sharpness_slider.get()) / 100))
        contrast_slider.set(initial_contrast * 100)
        contrast_slider.grid(row=1, column=1, padx=10, pady=5)

        sharpness_label = tk.Label(adjust_window, text="Skärpa")
        sharpness_label.grid(row=2, column=0, padx=10, pady=5)
        sharpness_slider = tk.Scale(adjust_window, from_=0, to=400, orient=tk.HORIZONTAL,
                                    command=lambda value: self.apply_adjustments(float(brightness_slider.get()) / 100,
                                                                                 float(contrast_slider.get()) / 100,
                                                                                 float(value) / 100))
        sharpness_slider.set(initial_sharpness * 100)
        sharpness_slider.grid(row=2, column=1, padx=10, pady=5)

        reset_button = tk.Button(adjust_window, text="Återställ",
                                 command=lambda: self.reset_adjustments(brightness_slider, contrast_slider,
                                                                        sharpness_slider))
        reset_button.grid(row=3, column=0, columnspan=2, pady=10)

    def reset_adjustments(self, brightness_slider, contrast_slider, sharpness_slider):
        brightness_slider.set(100)
        contrast_slider.set(100)
        sharpness_slider.set(100)
        self.apply_adjustments(1.0, 1.0, 1.0)  # Reset adjustments to default values

    def apply_adjustments(self, brightness, contrast, sharpness):
        if self.image:
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

    # Load data
    def open_image(self, event=None):
        self.rectangles.clear()
        load_data.open_image(self)
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))

    def open_folder(self, event=None):
        self.rectangles.clear()
        load_data.load_images_from_folder(self)
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
        load_data.open_image_from_list(self, self.image_current_id)

    def open_next(self, event=None):
        if len(self.image_list) > 0:
            if self.image_current_id < len(self.image_list):
                self.image_current_id = self.image_current_id + 1
                self.rectangles.clear()
                self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
                self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
                load_data.open_image_from_list(self, self.image_current_id)
                self.annotation_active = False
            else:
                print("Sista bilden i mappen")
        else:
            print("Inga bilder laddade")

    def open_prev(self, event=None):
        if len(self.image_list) > 0:
            if self.image_current_id > 0:
                self.image_current_id = self.image_current_id - 1
                self.rectangles.clear()
                self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
                self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
                load_data.open_image_from_list(self, self.image_current_id)
                self.annotation_active = False
            else:
                print("Första bilden i mappen")
        else:
            print("Inga bilder laddade")

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
            messagebox.showinfo("Annotering",
                                "Tryck ned vänster musknapp och markera tänderna du vill annotera.\n"
                                "Höger musknapp raderar senaste annotering.\n"
                                "Tryck på Escape för att avsluta annotering.")
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

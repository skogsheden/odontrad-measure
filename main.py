__author__ = "Nils Gustafsson"
__copyright__ = "Copyright 2024, Skogsheden"
__license__ = "GPL 3.0"
__version__ = "0.1.1"
__maintainer__ = "Nils Gustafsson"
__email__ = "nils.gustafsson@umu.se"
__status__ = "Development"

import tkinter as tk
import settings
import measurment
import calibration
import save_data
import load_data


class XrayMeasure:
    def __init__(self, master):
        self.master = master
        self.master.title("OdontRad - Mätverktyg")

        self.canvas = tk.Canvas(self.master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.photo_image = None
        self.draw = None
        self.measure1 = None
        self.measure2 = None
        self.pixels_per_mm = None
        self.calibration_done = False
        self.calibration_active = False

        self.blue_lines = []
        self.green_lines = []
        self.saved_lines = []
        self.measurements = {"blue": [], "green": []}  # Separate measurements for blue and green lines
        self.save_measurement_list = []
        self.image_filename = None

        self.username = ""
        self.function1_enabled = tk.BooleanVar(value=False)  # Förinställning: Aktiverad
        self.function2_enabled = tk.BooleanVar(value=False)  # Förinställning: Aktiverad

        # Menu
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Öppna bild", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Visa sparade mätningar", command=self.show_saved_measurements)
        file_menu.add_command(label="Importera sparade mätningar", command=self.load_measurements_from_file)
        file_menu.add_command(label="Rensa alla mätningar", command=self.clear_all_saved)
        file_menu.add_command(label="Spara till fil", command=self.save_measurements_to_file)
        file_menu.add_separator()
        file_menu.add_command(label="Inställningar", command=self.open_settings_window)
        file_menu.add_separator()
        file_menu.add_command(label="Avsluta", command=self.exit)
        menubar.add_cascade(label="Arkiv", menu=file_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Kalibrera i bilden", command=self.calibrate_pixels_to_mm)
        settings_menu.add_command(label="Ange pixlar per mm", command=self.set_pixels_per_mm)
        settings_menu.add_command(label="Ange pixelstorlek", command=self.set_pixels_size)
        menubar.add_cascade(label="Kalibrering", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kortkommandon", command=self.show_shortcuts)
        help_menu.add_command(label="Om", command=self.show_program_info)
        menubar.add_cascade(label="Hjälp", menu=help_menu)

        if self.calibration_active:
            self.canvas.bind("<Button-1>", lambda event: self.calibrate_click(event))
        else:
            self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
        self.master.bind("s", self.save_measurement)
        self.master.bind("q", self.exit)

        settings.load_settings(self)

    def exit(self, event=None):
        settings.save_settings(self)  # Save settings before exiting
        self.master.destroy()

    # Load data
    def open_image(self):
        load_data.open_image(self)

    def load_measurements_from_file(self):
        load_data.load_measurements_from_file(self)

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

    def calibrate_pixels_to_mm(self):
        calibration.calibrate_pixels_to_mm(self)

    def calibrate_click(self, event):
        calibration.calibrate_click(self, event)

    def calibrate_motion(self, event):
        calibration.calibrate_motion(self, event)

    def calibrate_release(self, event):
        calibration.calibrate_release(self, event)

    # Measurement
    def click(self, event, button):
        measurment.click(self, event, button)

    def motion(self, event, color):
        measurment.motion(self, event, color)

    def release(self, event, color):
        measurment.release(self, event, color)

    def save_measurement(self, event=None):
        measurment.save_measurement(self, event=None)

    def show_saved_measurements(self):
        measurment.show_saved_measurements(self)

    def calculate_distance(self, point1, point2):
        measurment.calculate_distance(self, point1, point2)


def main():
    root = tk.Tk()
    app = XrayMeasure(root)
    root.mainloop()


if __name__ == "__main__":
    main()

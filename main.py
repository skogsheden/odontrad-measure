__author__ = "Nils Gustafsson"
__copyright__ = "Copyright 2024, Skogsheden"
__license__ = "GPL 3.0"
__version__ = "0.1.1"
__maintainer__ = "Nils Gustafsson"
__email__ = "nils.gustafsson@umu.se"
__status__ = "Development"

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

import settings
import measurment
import calibration
import save_data
import load_data
import random


class XrayMeasure:
    def __init__(self, master):
        self.master = master
        self.master.title("OdontRad - Mätverktyg")

        # Canvas
        self.canvas = tk.Canvas(self.master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Image load
        self.image = None
        self.photo_image = None
        self.image_filename = None

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

        # Settings
        self.username = ""
        self.function1_enabled = tk.BooleanVar(value=False)  # Behåll linjer: Aktiverad
        self.function2_enabled = tk.BooleanVar(value=False)  # Fråga om tandyta: Aktiverad

        # Annotation
        self.annotation_active = False
        self.annotation_start_point = None
        self.annotation_end_point = None
        self.rectangles = []
        self.annotation_current_color = 'red'
        self.annotation_previous_color = 'red'
        self.colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']

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

        annotation_menu = tk.Menu(menubar, tearoff=0)
        annotation_menu.add_command(label="Starta annotering", command=self.annotate)
        annotation_menu.add_command(label="Avsluta annotering", command=self.stop_annotation)
        file_menu.add_separator()
        annotation_menu.add_command(label="Dölj/Visa rektanglar", command=self.toggle_rectangles_visibility)
        menubar.add_cascade(label="Annotering", menu=annotation_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Kalibrera i bilden", command=self.calibrate_pixels_to_mm)
        settings_menu.add_command(label="Ange pixlar per mm", command=self.set_pixels_per_mm)
        settings_menu.add_command(label="Ange pixelstorlek", command=self.set_pixels_size)
        menubar.add_cascade(label="Kalibrering", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kortkommandon", command=self.show_shortcuts)
        help_menu.add_command(label="Om", command=self.show_program_info)
        menubar.add_cascade(label="Hjälp", menu=help_menu)

        # Bind keyboard shortcuts
        self.master.bind("q", self.exit)
        self.master.bind("s", self.save_measurement)

        # Load settings from file
        settings.load_settings(self)

    def exit(self, event=None):
        settings.save_settings(self)  # Save settings before exiting
        self.master.destroy()

    # Load data
    def open_image(self):
        load_data.open_image(self)
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))

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

    # Annotation
    def annotate(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        self.canvas.bind("<Button-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.end_rectangle)
        self.canvas.bind("<Button-3>", self.delete_last_rectangle)
        self.master.bind("<Escape>", self.stop_annotation)
        messagebox.showinfo("Annotering",
                            "Tryck ned vänster musknapp och markera tänderna du vill annotera.\n"
                            "Höger musknapp raderar senaste annotering.\n"
                            "Tryck på Escape för att avsluta annotering.")

    def start_rectangle(self, event):
        self.annotation_start_point = (event.x, event.y)
        self.annotation_previous_color = self.annotation_current_color
        self.annotation_current_color = self.generate_random_color()

    def draw_rectangle(self, event):
        if self.annotation_start_point:
            if self.annotation_end_point:
                self.canvas.delete(self.rect)
            self.annotation_end_point = (event.x, event.y)

            self.rect = self.canvas.create_rectangle(self.annotation_start_point[0], self.annotation_start_point[1],
                                                     self.annotation_end_point[0], self.annotation_end_point[1],
                                                     outline=self.annotation_current_color)

    def end_rectangle(self, event):
        if self.annotation_start_point and self.annotation_end_point:
            name = simpledialog.askstring("Ange tand", "Skriv in namnet på tanden:")
            if not name:
                name = "NA"  # No id provided
            if name:
                # Determine position of text
                x1, y1 = self.annotation_start_point
                x2, y2 = self.annotation_end_point
                text_x = min(x1, x2)
                text_y = min(y1, y2)

                # Store data
                rectangle = {
                    "image": self.image_filename,
                    "tooth_id": name,
                    "coordinates": (self.annotation_start_point, self.annotation_end_point),
                    "rect": self.rect,
                    "text": self.canvas.create_text(text_x, text_y, text=name, anchor=tk.NW, fill=self.annotation_current_color),
                    "color": self.annotation_current_color,
                }
                self.canvas.itemconfigure(rectangle["rect"], state="normal")
                self.rectangles.append(rectangle)
                # Rita namnet i det övre vänstra hörnet

            self.annotation_start_point = None
            self.annotation_end_point = None
            print(self.rectangles)

    def generate_random_color(self):
        color_options = [color for color in self.colors if color != self.annotation_previous_color]
        return random.choice(color_options)

    def delete_last_rectangle(self, event):
        if self.rectangles:
            print("delete")
            print(self.rectangles)
            last_rectangle = self.rectangles[-1]["rect"]
            last_text = self.rectangles[-1]["text"]
            self.canvas.delete(last_rectangle)  # Delete the rectangle from the canvas
            self.canvas.delete(last_text)
            self.rectangles.pop()
        else:
            print("Inget att radera")

    def stop_annotation(self, event=None):
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
        self.canvas.unbind("<Escape>")

    def toggle_rectangles_visibility(self):
        for rectangle_data in self.rectangles:
            rectangle = rectangle_data["rect"]
            text = rectangle_data["text"]
            color = rectangle_data["color"]
            current_state = self.canvas.itemcget(rectangle, "state")
            new_state = "hidden" if current_state == "normal" else "normal"
            self.canvas.itemconfigure(rectangle, state=new_state)
            self.canvas.itemconfigure(text, state=new_state)

def main():
    root = tk.Tk()
    app = XrayMeasure(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
def open_image(self):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff")])
    if file_path:
        self.image = Image.open(file_path)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.draw = ImageDraw.Draw(self.image)
        self.image_filename = file_path
        print("Bild laddad")

def load_measurements_from_file(self, line_color=None):
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            lines = file.readlines()
            measurements = []
            current_measurement = {}
            current_filename = None
            found_matching_file = False
            for line in lines:
                if not found_matching_file:
                    if line.startswith("Filename:"):
                        current_filename = line.split("Filename:")[1].strip()
                        if current_filename == self.image_filename:
                            found_matching_file = True
                            firstpass = False
                        else:
                            continue  # Gå vidare till nästa rad om filnamnet inte matchar
                    else:
                        continue  # Gå vidare till nästa rad om det inte är en filnamnrad
                else:
                    if line.startswith("Blue coordinates:"):
                        blue_coordinates = eval(line.split(":")[1].strip())
                        current_measurement["blue_coordinates"] = blue_coordinates
                    elif line.startswith("Green coordinates:"):
                        green_coordinates = eval(line.split(":")[1].strip())
                        current_measurement["green_coordinates"] = green_coordinates
                    elif line.startswith("Ratio (Green/Blue):"):
                        ratio = float(line.split(":")[1].strip())
                        current_measurement["ratio"] = ratio
                        current_measurement = {}
                    elif line.startswith("Filename:"):
                        measurements.append(current_measurement)
                        current_measurement = {}
                        current_filename = line.split("Filename:")[1].strip()
                        if current_filename == self.image_filename:
                            found_matching_file = True
                        else:
                            found_matching_file = False
                measurements.append(current_measurement)  # If end reached save last measurment
                current_measurement = {}
        if found_matching_file:
            if measurements:
                # Nu har vi mätningsinformation för aktuell fil
                # Rita ut linjerna på bilden baserat på denna information
                for measurement in measurements:
                    if "blue_coordinates" in measurement:
                        blue_coordinates = measurement["blue_coordinates"]
                        self.saved_lines.append(self.canvas.create_line(blue_coordinates[0][0], blue_coordinates[0][1],
                                                                        blue_coordinates[1][0],
                                                                        blue_coordinates[1][1], fill="blue", width=2))
                    if "green_coordinates" in measurement:
                        green_coordinates = measurement["green_coordinates"]
                        self.saved_lines.append(
                            self.canvas.create_line(green_coordinates[0][0], green_coordinates[0][1],
                                                    green_coordinates[1][0],
                                                    green_coordinates[1][1], fill="green", width=2))
            else:
                messagebox.showerror("Inga mätningar hittades",
                                     "Inga mätningar för den aktuella bilden hittades i filen.")
        else:
            messagebox.showerror("Fel fil öppnad",
                                 f"Ingen information hittades för den aktuella bilden \"{self.image_filename}\".")

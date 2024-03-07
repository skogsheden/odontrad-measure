import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw


def open_image(self):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff")])
    if file_path:
        self.image_filepath = file_path
        original_image = Image.open(file_path)
        # Rescale the image to fit the screen while preserving pixel values
        img_height = original_image.height
        img_width = original_image.width
        if img_height > img_width:
            img_q = img_width / img_height
            screen_height = self.canvas.winfo_screenheight()
            screen_width = round(screen_height * img_q)
        else:
            img_q = img_width / img_height
            screen_width = self.canvas.winfo_screenwidth()
            screen_height = round(screen_width / img_q)
        resized_image = original_image.resize((screen_width, screen_height), Image.LANCZOS )
        self.image = resized_image
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=screen_width, height=screen_height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.draw = ImageDraw.Draw(self.image)
        filename_parts = file_path.split('/')
        self.image_filename = filename_parts[-1]  # Sista delen är filnamnet, hela path behövs ej
        print("Bild laddad")

        # Calculate scale conversion
        self.image_scale_x = img_width / screen_width
        self.image_scale_y = img_height / screen_height

        self.load_annotations()
        self.load_calibration_data()


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
                self.save_measurement_list.append(current_measurement)
                current_measurement = {}

        if found_matching_file:
            if measurements:
                # Nu har vi mätningsinformation för aktuell fil
                # Rita ut linjerna på bilden baserat på denna information
                for measurement in measurements:
                    if "blue_coordinates" in measurement:
                        blue_coordinates = measurement["blue_coordinates"]
                        self.saved_lines.append(self.canvas.create_line(blue_coordinates[0][0]/self.image_scale_x, blue_coordinates[0][1]/self.image_scale_y,
                                                                        blue_coordinates[1][0]/self.image_scale_x,
                                                                        blue_coordinates[1][1]/self.image_scale_y, fill="blue", width=2))
                    if "green_coordinates" in measurement:
                        green_coordinates = measurement["green_coordinates"]
                        self.saved_lines.append(
                            self.canvas.create_line(green_coordinates[0][0]/self.image_scale_x, green_coordinates[0][1]/self.image_scale_y,
                                                    green_coordinates[1][0]/self.image_scale_x,
                                                    green_coordinates[1][1]/self.image_scale_y, fill="green", width=2))
            else:
                messagebox.showerror("Inga mätningar hittades",
                                     "Inga mätningar för den aktuella bilden hittades i filen.")
        else:
            messagebox.showerror("Fel fil öppnad",
                                 f"Ingen information hittades för den aktuella bilden \"{self.image_filename}\".")


import tkinter as tk
import os
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import json
import save_data


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
                                existing_measurement.get('blue_coordinates') == measurement.get('blue_coordinates') and
                                existing_measurement.get('green_coordinates') == measurement.get('green_coordinates')):
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        self.save_measurement_list.append(measurement)

                print(f"Measurements auto-loaded from {json_file_path}")

                # Use after to ensure the image is fully loaded and scaled correctly
                # before redrawing the measurements
                self.master.after(100, self.redraw_annotations_and_measurements)
                return True
            except Exception as e:
                print(f"Error loading measurements from JSON: {e}")
                return False
        else:
            print(f"No measurement JSON file found: {json_file_path}")
            return False
    return False

def load_images_from_folder(self):
    folder_path = filedialog.askdirectory()
    if not folder_path:  # Check if user cancels the dialog
        return

    folder_path = os.path.normpath(folder_path)  # Normalizing path

    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))
                   and f.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.tif'))]

    self.image_list = [os.path.join(folder_path, file_name) for file_name in image_files]
    self.image_current_id = 0


def open_image_from_list(self, index):
    if 0 <= index < len(self.image_list):
        if self.rectangles:
            for rectangle in self.rectangles:
                last_rectangle = rectangle["rect"]
                last_text = rectangle["text"]
                self.canvas.delete(last_rectangle)  # Delete the rectangle from the canvas
                self.canvas.delete(last_text)
            self.rectangles.clear()
        self.image_filepath = self.image_list[index]
        original_image = Image.open(self.image_filepath)
        screen_q = self.canvas.winfo_screenwidth() / self.canvas.winfo_screenheight()
        # Rescale the image to fit the screen while preserving pixel values
        img_height = original_image.height
        img_width = original_image.width
        img_q = img_width / img_height
        if img_q > screen_q:
            screen_width = self.canvas.winfo_screenwidth() - 100
            screen_height = round(screen_width / img_q)
        else:
            screen_height = self.canvas.winfo_screenheight() - 150
            screen_width = round(screen_height * img_q)

        resized_image = original_image.resize((screen_width, screen_height), Image.LANCZOS)
        self.image = resized_image
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=screen_width, height=screen_height)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.draw = ImageDraw.Draw(self.image)
        filename_parts = self.image_filepath.split(os.path.sep)
        self.image_filename = filename_parts[-1]  # Sista delen är filnamnet, hela path behövs ej

        # Calculate scale conversion
        self.image_scale_x = img_width / screen_width
        self.image_scale_y = img_height / screen_height

        self.load_annotations()
        self.load_calibration_data()

        # Auto-load measurements from JSON if available
        self.auto_load_measurements_from_json()

        print("Bild laddad från listan")
    else:
        print("Utanför index")

def open_image(self):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff")])

    if self.rectangles:
        for rectangle in self.rectangles:
            last_rectangle = rectangle["rect"]
            last_text = rectangle["text"]
            self.canvas.delete(last_rectangle)  # Delete the rectangle from the canvas
            self.canvas.delete(last_text)
        self.rectangles.clear()

    if file_path:
        self.image_filepath = file_path
        original_image = Image.open(self.image_filepath)
        screen_q = self.canvas.winfo_screenwidth() / self.canvas.winfo_screenheight()
        # Rescale the image to fit the screen while preserving pixel values
        img_height = original_image.height
        img_width = original_image.width
        img_q = img_width / img_height
        print(screen_q, img_q)
        if img_q > screen_q:
            screen_width = self.canvas.winfo_screenwidth() - 100
            screen_height = round(screen_width / img_q)
        else:
            screen_height = self.canvas.winfo_screenheight() - 150
            screen_width = round(screen_height * img_q)
        resized_image = original_image.resize((screen_width, screen_height), Image.LANCZOS)
        self.image = resized_image
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=screen_width, height=screen_height)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        self.draw = ImageDraw.Draw(self.image)
        filename_parts = self.image_filepath.split('/')
        self.image_filename = filename_parts[-1]  # Sista delen är filnamnet, hela path behövs ej
        print("Bild laddad")

        # Calculate scale conversion
        self.image_scale_x = img_width / screen_width
        self.image_scale_y = img_height / screen_height

        self.load_annotations()
        self.load_calibration_data()

        # Auto-load measurements from JSON if available
        self.auto_load_measurements_from_json()
        self.master.after(200, self.redraw_annotations_and_measurements)

def load_measurements_from_file(self, line_color=None):
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt")])
    if file_path:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.csv':
            # Handle CSV file format
            import csv
            with open(file_path, "r", newline='') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)  # Skip the header row

                measurements = []
                for row in csv_reader:
                    if len(row) < 2:  # Skip empty rows
                        continue

                    # Check if this row matches the current image
                    current_filename = row[1].strip()  # Filename is in the second column
                    if current_filename == self.image_filename:
                        current_measurement = {
                            "filename": current_filename,
                            "tooth_id": row[2] if len(row) > 2 and row[2] else None,
                        }

                        # Blue coordinates
                        if len(row) > 3 and row[3]:
                            try:
                                current_measurement["blue_coordinates"] = eval(row[3])
                            except:
                                pass

                        # Blue length pixels
                        if len(row) > 4 and row[4]:
                            try:
                                current_measurement["blue_length_pixels"] = float(row[4])
                            except:
                                pass

                        # Blue length mm
                        if len(row) > 5 and row[5]:
                            try:
                                current_measurement["blue_length_mm"] = float(row[5])
                            except:
                                pass

                        # Green coordinates
                        if len(row) > 6 and row[6]:
                            try:
                                current_measurement["green_coordinates"] = eval(row[6])
                            except:
                                pass

                        # Green length pixels
                        if len(row) > 7 and row[7]:
                            try:
                                current_measurement["green_length_pixels"] = float(row[7])
                            except:
                                pass

                        # Green length mm
                        if len(row) > 8 and row[8]:
                            try:
                                current_measurement["green_length_mm"] = float(row[8])
                            except:
                                pass

                        # Ratio
                        if len(row) > 9 and row[9]:
                            try:
                                current_measurement["ratio"] = float(row[9])
                            except:
                                pass

                        measurements.append(current_measurement)
                        self.save_measurement_list.append(current_measurement)

        else:
            # Original code for handling text files
            with open(file_path, "r") as file:
                lines = file.readlines()
                measurements = []
                current_measurement = {}
                found_matching_file = False
                for line in lines:
                    if not found_matching_file:
                        if line.startswith("Filename:"):
                            current_filename = line.split("Filename:")[1].strip().replace('\n', '')
                            if current_filename == self.image_filename:
                                found_matching_file = True
                                current_filename = current_filename.rstrip('\n')
                                current_measurement["filename"] = current_filename
                            else:
                                continue  # Gå vidare till nästa rad om filnamnet inte matchar
                        else:
                            continue  # Gå vidare till nästa rad om det inte är en filnamnrad
                    else:
                        if line.startswith("Tooth id:"):
                            tooth_id = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["tooth_id"] = tooth_id
                        elif line.startswith("Blue coordinates:"):
                            blue_coordinates = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["blue_coordinates"] = blue_coordinates
                        elif line.startswith("Blue Length (pixels):"):
                            blue_length_pixels = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["blue_length_pixels"] = blue_length_pixels
                        elif line.startswith("Blue Length (mm):"):
                            blue_length_mm = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["blue_length_mm"] = blue_length_mm
                        elif line.startswith("Green coordinates:"):
                            green_coordinates = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["green_coordinates"] = green_coordinates
                        elif line.startswith("Green Length (pixels):"):
                            green_length_pixels = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["green_length_pixels"] = green_length_pixels
                        elif line.startswith("Green Length (mm):"):
                            green_length_mm = eval(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["green_length_mm"] = green_length_mm
                        elif line.startswith("Ratio (Green/Blue):"):
                            ratio = float(line.split(":")[1].strip().replace('\n', ''))
                            current_measurement["ratio"] = ratio
                            found_matching_file = False
                        elif line.startswith("Filename:"):
                            current_filename = line.split("Filename:")[1].strip().replace('\n', '')
                            if current_filename == self.image_filename:
                                measurements.append(current_measurement)  # If end reached save last measurement
                                print(current_measurement)
                                self.save_measurement_list.append(current_measurement)
                                current_measurement = {}
                                found_matching_file = True
                                current_filename = current_filename.rstrip('\n')
                                current_measurement["filename"] = current_filename
                            else:
                                found_matching_file = False
                measurements.append(current_measurement)  # If end reached save last measurement
                self.save_measurement_list.append(current_measurement)

        # Draw the measurements on the canvas
        if measurements:
            # Rita ut linjerna på bilden baserat på denna information
            for measurement in measurements:
                if "blue_coordinates" in measurement and measurement["blue_coordinates"]:
                    blue_coordinates = measurement["blue_coordinates"]
                    self.saved_lines.append(self.canvas.create_line(blue_coordinates[0][0] / self.image_scale_x,
                                                                    blue_coordinates[0][1] / self.image_scale_y,
                                                                    blue_coordinates[1][0] / self.image_scale_x,
                                                                    blue_coordinates[1][1] / self.image_scale_y,
                                                                    fill="blue", width=2))
                if "green_coordinates" in measurement and measurement["green_coordinates"]:
                    green_coordinates = measurement["green_coordinates"]
                    self.saved_lines.append(
                        self.canvas.create_line(green_coordinates[0][0] / self.image_scale_x,
                                                green_coordinates[0][1] / self.image_scale_y,
                                                green_coordinates[1][0] / self.image_scale_x,
                                                green_coordinates[1][1] / self.image_scale_y, fill="green",
                                                width=2))
        else:
            messagebox.showerror("No measurements found",
                                 "No measurements found for this image.")
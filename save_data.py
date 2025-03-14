from tkinter import filedialog, simpledialog, messagebox
import csv
import os
import json


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

def save_measurements_to_file(self):
    if self.save_measurement_list:
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline='') as file:
                csv_writer = csv.writer(file)

                # Write header row
                header = ["Examiner", "Filename", "Tooth ID", "Blue Coordinates", "Blue Length (pixels)",
                          "Blue Length (mm)", "Green Coordinates", "Green Length (pixels)",
                          "Green Length (mm)", "Ratio (Green/Blue)"]
                csv_writer.writerow(header)

                # Write data rows
                for measurement_info in self.save_measurement_list:
                    row = [
                        self.username,
                        measurement_info.get('filename', ''),
                        measurement_info.get('tooth_id', ''),
                        measurement_info.get('blue_coordinates', ''),
                        f"{measurement_info.get('blue_length_pixels', 0):.2f}" if 'blue_length_pixels' in measurement_info else '',
                        f"{measurement_info.get('blue_length_mm', 0):.2f}" if 'blue_length_mm' in measurement_info else '',
                        measurement_info.get('green_coordinates', ''),
                        f"{measurement_info.get('green_length_pixels', 0):.2f}" if 'green_length_pixels' in measurement_info else '',
                        f"{measurement_info.get('green_length_mm', 0):.2f}" if 'green_length_mm' in measurement_info else '',
                        f"{measurement_info.get('ratio', 0):.2f}" if 'ratio' in measurement_info else ''
                    ]
                    csv_writer.writerow(row)

            messagebox.showinfo("Measurements saved", "Measurements saved to CSV file.")
    else:
        messagebox.showinfo("No measurements", "No measurements to save.")
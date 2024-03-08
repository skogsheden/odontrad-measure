from tkinter import filedialog, simpledialog, messagebox


def save_measurements_to_file(self):
    if self.save_measurement_list:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(f"Examiner: {self.username}\n")
                for measurement_info in self.save_measurement_list:
                    if "filename" in measurement_info:
                        file.write(f"Filename: {measurement_info['filename']}\n")
                    if 'tooth_id' in measurement_info:
                        file.write(f"Tooth id: {measurement_info['tooth_id']}\n")
                    if 'blue_coordinates' in measurement_info:
                        file.write(f"Blue coordinates: {measurement_info['blue_coordinates']}\n")
                    if 'blue_length_pixels' in measurement_info:
                        file.write(f"Blue Length (pixels): {measurement_info['blue_length_pixels']:.2f}\n")
                    if 'blue_length_mm' in measurement_info:
                        file.write(f"Blue Length (mm): {measurement_info['blue_length_mm']:.2f}\n")
                    if 'green_coordinates' in measurement_info:
                        file.write(f"Green coordinates: {measurement_info['green_coordinates']}\n")
                    if 'green_length_pixels' in measurement_info:
                        file.write(f"Green Length (pixels): {measurement_info['green_length_pixels']:.2f}\n")
                    if 'green_length_mm' in measurement_info:
                        file.write(f"Green Length (mm): {measurement_info['green_length_mm']:.2f}\n")
                    if 'ratio' in measurement_info:
                        file.write(f"Ratio (Green/Blue): {measurement_info['ratio']:.2f}\n\n")
            messagebox.showinfo("Mätningar sparade", "Mätningar sparade till filen.")
    else:
        messagebox.showinfo("Inga mätningar", "Inga mätningar att spara.")

# App name: OdontRad - Mätverktyg
# Author: Nils Gustafsson
# Year: 2024
#

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import math


class ImageMeasureApp:
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
        self.measurements = {"blue": [], "green": []}  # Separate measurements for blue and green lines
        self.save_measurement_list = []
        self.image_filename = None

        # Menu
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Öppna bild", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Visa sparade mätningar", command=self.show_saved_measurements)
        file_menu.add_command(label="Spara till fil", command=self.save_measurements)
        file_menu.add_separator()
        file_menu.add_command(label="Importera sparade mätningar", command=self.load_measurements_from_file)
        file_menu.add_separator()
        file_menu.add_command(label="Avsluta", command=self.master.destroy)
        menubar.add_cascade(label="Arkiv", menu=file_menu)

        calibration_menu = tk.Menu(menubar, tearoff=0)
        calibration_menu.add_command(label="Kalibrera i bilden", command=self.calibrate_pixels_to_mm)
        calibration_menu.add_command(label="Ange pixlar per mm", command=self.set_pixels_per_mm)
        menubar.add_cascade(label="Kalibrera", menu=calibration_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Programinfo", command=self.show_program_info)
        help_menu.add_command(label="Kortkommandon", command=self.show_shortcuts)
        menubar.add_cascade(label="Hjälp", menu=help_menu)

        if self.calibration_active:
            self.canvas.bind("<Button-1>", lambda event: self.calibrate_click(event))
        else:
            self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))
        self.master.bind("s", self.save_measurement)
        self.master.bind("q", self.exit)

    def exit(self, event=None):
        self.master.destroy()

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

    def show_program_info(self):
        info_text = """
        Mät avståndet mellan två punkter i röntgenbilder.
        
        Skapat av: 
        Nils Gustafsson (2024)
        """
        messagebox.showinfo("Programinfo", info_text)

    def show_shortcuts(self):
        shortcut_text = """
        - Vänsterklicka: Rita blå linje. 
        - Högerklicka: Rita en grön linje.
        - Tryck på 's': Spara mätningen
        - Tryck på 'q': Avsluta programmet
        """
        messagebox.showinfo("Kortkommandon", shortcut_text)

    def click(self, event, button):
        if self.image:
            color = "blue" if button == "left" else "green"
            if not self.measure1:
                self.measure1 = (event.x, event.y)
                if button == "left":
                    self.canvas.bind("<B1-Motion>", lambda event: self.motion(event, color))
                    self.canvas.bind("<ButtonRelease-1>", lambda event: self.release(event, color))
                else:
                    self.canvas.bind("<B3-Motion>", lambda event: self.motion(event, color))
                    self.canvas.bind("<ButtonRelease-3>", lambda event: self.release(event, color))
        elif not self.image:
            messagebox.showerror("Ingen bild öppnad", "Öppja en bild först.")

    def motion(self, event, color):
        self.measure2 = (event.x, event.y)
        lines = self.blue_lines if color == "blue" else self.green_lines
        if lines:
            self.canvas.delete(lines[-1])
        line = self.canvas.create_line(self.measure1[0], self.measure1[1], self.measure2[0], self.measure2[1],
                                       fill=color, width=2)
        lines.append(line)
        self.measurements[color].append((self.measure1, self.measure2))

    def release(self, event, color):
        if color == "blue":
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
        else:
            self.canvas.unbind("<B3-Motion>")
            self.canvas.unbind("<ButtonRelease-3>")

        if self.measure2:
            distance_pixels = math.sqrt(
                (self.measure2[0] - self.measure1[0]) ** 2 + (self.measure2[1] - self.measure1[1]) ** 2)
            if self.calibration_done:
                print(f"Sträcka: {distance_pixels} pixlar och {distance_pixels / self.pixels_per_mm} mm")
            else:
                print(f"Sträcka: {distance_pixels} pixlar")
        else:
            print("Mätning ej slutförd.")

        self.measure1 = None
        self.measure2 = None
    def save_measurement(self, event=None):
        if self.image_filename:
            blue_measurements = self.measurements["blue"]
            green_measurements = self.measurements["green"]
            if blue_measurements and green_measurements:
                # Get the latest measurement for blue and green
                latest_blue_measurement = blue_measurements[-1]
                latest_green_measurement = green_measurements[-1]

                # Calculate length in pixels and mm for blue lines
                blue_length_pixels = math.sqrt((latest_blue_measurement[1][0] - latest_blue_measurement[0][0]) ** 2 + (
                        latest_blue_measurement[1][1] - latest_blue_measurement[0][1]) ** 2)
                if self.calibration_done:
                    blue_length_mm = blue_length_pixels / self.pixels_per_mm

                # Calculate length in pixels and mm for green lines
                green_length_pixels = math.sqrt(
                    (latest_green_measurement[1][0] - latest_green_measurement[0][0]) ** 2 + (
                            latest_green_measurement[1][1] - latest_green_measurement[0][1]) ** 2)
                if self.calibration_done:
                    green_length_mm = green_length_pixels / self.pixels_per_mm

                # Compute the ratio between the lengths
                ratio = green_length_pixels / blue_length_pixels

                # Append the measurement information to a list
                if self.calibration_done:
                    measurement_info = {
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "blue_length_mm": blue_length_mm,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "green_length_mm": green_length_mm,
                        "ratio": ratio
                    }
                else:
                    measurement_info = {
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "ratio": ratio
                    }
                self.save_measurement_list.append(measurement_info)
                # Do something with measurement_info
                # Visa popup "Sparat" som försvinner efter 1 sekund
                popup = tk.Toplevel(self.master)
                popup.title("Sparat")

                # Hämta pekarens position
                x, y = self.master.winfo_pointerxy()
                popup.geometry(f"+{x}+{y}")  # Placera popup relativt till pekarens position
                label = tk.Label(popup, text="Sparar")
                label.pack(pady=5)
                popup.after(200, popup.destroy)  # Stäng popup efter 1 sekund

                print("Save Measurement List:", self.save_measurement_list)
                # Do something with measurement_info
                #  print("Measurement Info:", measurement_info)
            elif blue_measurements:
                # Get the latest measurement for blue and green
                latest_blue_measurement = blue_measurements[-1]

                # Calculate length in pixels and mm for blue lines
                blue_length_pixels = math.sqrt((latest_blue_measurement[1][0] - latest_blue_measurement[0][0]) ** 2 + (
                        latest_blue_measurement[1][1] - latest_blue_measurement[0][1]) ** 2)
                if self.calibration_done:
                    blue_length_mm = blue_length_pixels / self.pixels_per_mm

                # Append the measurement information to a list
                if self.calibration_done:
                    measurement_info = {
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "blue_length_mm": blue_length_mm
                    }
                else:
                    measurement_info = {
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels
                    }
                self.save_measurement_list.append(measurement_info)
                # Do something with measurement_info
                # Visa popup "Sparat" som försvinner efter 1 sekund
                popup = tk.Toplevel(self.master)
                popup.title("Sparat")

                # Hämta pekarens position
                x, y = self.master.winfo_pointerxy()
                popup.geometry(f"+{x}+{y}")  # Placera popup relativt till pekarens position
                label = tk.Label(popup, text="Sparar")
                label.pack(pady=5)
                popup.after(500, popup.destroy)  # Stäng popup efter 1 sekund

                print("Save Measurement List:", self.save_measurement_list)
                # Do something with measurement_info
                #  print("Measurement Info:", measurement_info)
            elif green_measurements:
                # Get the latest measurement for blue and green
                latest_green_measurement = green_measurements[-1]

                # Calculate length in pixels and mm for green lines
                green_length_pixels = math.sqrt(
                    (latest_green_measurement[1][0] - latest_green_measurement[0][0]) ** 2 + (
                            latest_green_measurement[1][1] - latest_green_measurement[0][1]) ** 2)
                if self.calibration_done:
                    green_length_mm = green_length_pixels / self.pixels_per_mm

                # Append the measurement information to a list
                if self.calibration_done:
                    measurement_info = {
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "green_length_mm": green_length_mm
                    }
                else:
                    measurement_info = {
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels
                    }
                self.save_measurement_list.append(measurement_info)
                # Do something with measurement_info
                # Visa popup "Sparat" som försvinner efter 1 sekund
                popup = tk.Toplevel(self.master)
                popup.title("Sparat")

                # Hämta pekarens position
                x, y = self.master.winfo_pointerxy()
                popup.geometry(f"+{x}+{y}")  # Placera popup relativt till pekarens position
                label = tk.Label(popup, text="Sparar")
                label.pack(pady=5)
                popup.after(500, popup.destroy)  # Stäng popup efter 1 sekund

                print("Save Measurement List:", self.save_measurement_list)
                # Do something with measurement_info
                #  print("Measurement Info:", measurement_info)
            else:
                messagebox.showinfo("Inte tillräckligt med mätningar",
                                    "Det krävs minst minst en sparad mätning.")
        else:
            messagebox.showerror("Ingen bild öppen", "Öppna en bild först.")

    def show_saved_measurements(self):
        if self.save_measurement_list:
            saved_measurements_window = tk.Toplevel(self.master)
            saved_measurements_window.title("Sparade mätningar")

            scrollbar = tk.Scrollbar(saved_measurements_window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_area = tk.Text(saved_measurements_window, wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_area.pack(fill=tk.BOTH, expand=True)

            for measurement_info in self.save_measurement_list:
                if 'filename' in measurement_info:
                    text_area.insert(tk.END, f"Filename: {measurement_info['filename']}\n")
                if 'blue_coordinates' in measurement_info:
                    text_area.insert(tk.END, f"Blue coordinates: {measurement_info['blue_coordinates']}\n")
                if 'blue_length_pixels' in measurement_info:
                    text_area.insert(tk.END, f"Blue Length (pixels): {measurement_info['blue_length_pixels']:.2f} px\n")
                if 'blue_length_mm' in measurement_info:
                    text_area.insert(tk.END, f"Blue Length (mm): {measurement_info['blue_length_mm']:.2f} mm\n")
                if 'green_coordinates' in measurement_info:
                    text_area.insert(tk.END, f"Green coordinates: {measurement_info['green_coordinates']}\n")
                if 'green_length_pixels' in measurement_info:
                    text_area.insert(tk.END,
                                     f"Green Length (pixels): {measurement_info['green_length_pixels']:.2f} px\n")
                if 'green_length_mm' in measurement_info:
                    text_area.insert(tk.END, f"Green Length (mm): {measurement_info['green_length_mm']:.2f} mm\n")
                if 'ratio' in measurement_info:
                    text_area.insert(tk.END, f"Ratio (Green/Blue): {measurement_info['ratio']:.2f}\n")
                text_area.insert(tk.END, f"\n")
            scrollbar.config(command=text_area.yview)
        else:
            messagebox.showinfo("Inga sparade mätningar", "Ingen mätningsdata sparad för närvarande.")

    def set_pixels_per_mm(self):
        pixels_per_mm = simpledialog.askfloat("Ange pixlar per mm", "Ange antal pixlar per millimeter:")
        if pixels_per_mm:
            self.pixels_per_mm = pixels_per_mm
            messagebox.showinfo("Pixlar per mm inställda", f"Pixlar per mm inställda till: {pixels_per_mm:.2f}")
            self.calibration_done = True

    def calibrate_pixels_to_mm(self):
        if self.image:
            self.calibration_done = False
            self.canvas.bind("<Button-1>", lambda event: self.calibrate_click(event))
            messagebox.showinfo("Kalibrering", "Tryck ned vänster musknapp dra en linje över ett objekt med en känd längd.")
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

        distance_pixels = math.sqrt(
            (self.measure2[0] - self.measure1[0]) ** 2 + (self.measure2[1] - self.measure1[1]) ** 2)
        distance_mm = simpledialog.askfloat("Kalibrering", "Skriv in sträckan som den den röda linjen motsvarar i millimeter:")
        if distance_mm:
            self.pixels_per_mm = distance_pixels / distance_mm
            messagebox.showinfo("Kalibrering", f"Pixlar per mm enligt kalibrering: {self.pixels_per_mm:.2f}")
            self.calibration_done = True
            self.calibration_active = False
            self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))  # Rebind left-click event
            self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))  # Rebind right-click event
        self.reset_canvas()

    def reset_canvas(self):
        for line in self.blue_lines:
            self.canvas.delete(line)
        for line in self.green_lines:
            self.canvas.delete(line)
        self.blue_lines.clear()
        self.green_lines.clear()
        self.measure1 = None
        self.measure2 = None

    def calculate_distance(self, point1, point2):
        if self.pixels_per_mm:
            return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) / self.pixels_per_mm
        else:
            return 0

    def save_measurements(self):
        if self.save_measurement_list:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if file_path:
                with open(file_path, "w") as file:
                    for measurement_info in self.save_measurement_list:
                        file.write(f"Filename: {self.image_filename}\n")
                        if 'blue_coordinates' in measurement_info:
                            file.write(f"Blue coordinates: {measurement_info['blue_coordinates']}\n")
                        if 'blue_length_pixels' in measurement_info:
                            file.write(f"Blue Length (pixels): {measurement_info['blue_length_pixels']:.2f} px\n")
                        if 'blue_length_mm' in measurement_info:
                            file.write(f"Blue Length (mm): {measurement_info['blue_length_mm']:.2f} mm\n")
                        if 'green_coordinates' in measurement_info:
                            file.write(f"Green coordinates: {measurement_info['green_coordinates']}\n")
                        if 'green_length_pixels' in measurement_info:
                            file.write(f"Green Length (pixels): {measurement_info['green_length_pixels']:.2f} px\n")
                        if 'green_length_mm' in measurement_info:
                            file.write(f"Green Length (mm): {measurement_info['green_length_mm']:.2f} mm\n")
                        if 'ratio' in measurement_info:
                            file.write(f"Ratio (Green/Blue): {measurement_info['ratio']:.2f}\n\n")
                messagebox.showinfo("Mätningar sparade", "Mätningar sparade till filen.")
        else:
            messagebox.showinfo("Inga mätningar", "Inga mätningar att spara.")

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
                    measurements.append(current_measurement) #If end reached save last measurment
                    current_measurement = {}
            if found_matching_file:
                if measurements:
                    # Nu har vi mätningsinformation för aktuell fil
                    # Rita ut linjerna på bilden baserat på denna information
                    for measurement in measurements:
                        if "blue_coordinates" in measurement:
                            blue_coordinates = measurement["blue_coordinates"]
                            self.canvas.create_line(blue_coordinates[0][0], blue_coordinates[0][1], blue_coordinates[1][0],
                                                    blue_coordinates[1][1], fill="blue", width=2)
                        if "green_coordinates" in measurement:
                            green_coordinates = measurement["green_coordinates"]
                            self.canvas.create_line(green_coordinates[0][0], green_coordinates[0][1], green_coordinates[1][0],
                                                    green_coordinates[1][1], fill="green", width=2)
                else:
                    messagebox.showerror("Inga mätningar hittades",
                                         "Inga mätningar för den aktuella bilden hittades i filen.")
            else:
                messagebox.showerror("Fel fil öppnad",
                                     f"Ingen information hittades för den aktuella bilden \"{self.image_filename}\".")


def main():
    root = tk.Tk()
    app = ImageMeasureApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

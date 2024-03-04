import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import math


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
        messagebox.showerror("Ingen bild öppnad", "Öppna en bild först.")


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
        matching_rectangles = []

        # Check if any measurement is within an annotated rectangle
        if self.rectangles:
            for rectangle in self.rectangles:
                # Extract coordinates of the rectangle
                x1, y1 = rectangle["coordinates"][0]
                x2, y2 = rectangle["coordinates"][1]

                # Check if both blue and green coordinates are within the rectangle
                if blue_measurements and green_measurements:
                    if all(x1 <= point[0] <= x2 and y1 >= point[1] >= y2 for point in
                           blue_measurements[-1] + green_measurements[-1]):
                        matching_rectangles.append(rectangle)
                # Check if only blue measurements are within the rectangle
                elif blue_measurements and not green_measurements:
                    if all(x1 <= point[0] <= x2 and y1 >= point[1] >= y2 for point in
                           blue_measurements[-1]):
                        matching_rectangles.append(rectangle)
                # Check if only green measurements are within the rectangle
                elif not blue_measurements and green_measurements:
                    if all(x1 <= point[0] <= x2 and y1 >= point[1] >= y2 for point in
                           green_measurements[-1]):
                        matching_rectangles.append(rectangle)
            if matching_rectangles:
                if len(matching_rectangles) > 1:
                    # If multiple matching rectangles, prompt the user to select one
                    rectangle_names = [rectangle["tooth_id"] for rectangle in matching_rectangles]
                    names_string = "\n".join(rectangle_names)

                    selected_rectangle = simpledialog.askstring("Ingen träff - Ange tand",
                                                                "Tillgängliga tandnamn:\n" + names_string + "\n\nSkriv in namnet på tanden:")
                    if selected_rectangle:
                        if selected_rectangle in rectangle_names:
                            tooth_id = selected_rectangle
                        else:
                            confirm_selection = messagebox.askyesno("Bekräftelse",
                                                                     selected_rectangle + " fanns inte i listan. Vill du spara?")
                            if confirm_selection:
                                tooth_id = selected_rectangle
                            else:
                                tooth_id = "NA"
                                return  # User cancelled selection
                else:
                    # Only one matching rectangle found
                    tooth_id = matching_rectangles[0]["tooth_id"]
            else:
                # No matching rectangles found
                tooth_id = simpledialog.askstring("Ingen träff - Ange tand", "Skriv in namnet på tanden:")
                if not tooth_id:
                    tooth_id = "NA"
        else:
            # No rectangles present
            if self.function1_enabled.get():
                tooth_id = simpledialog.askstring("Ingen träff - Ange tand", "Skriv in namnet på tanden:")
                if not tooth_id:
                    tooth_id = "NA"
            else:
                tooth_id = "NA"

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
            if tooth_id == "NA":
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
            else:
                if self.calibration_done:
                    measurement_info = {
                        "tooth_id": tooth_id,
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
                        "tooth_id": tooth_id,
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


        elif blue_measurements:
            # Get the latest measurement for blue and green
            latest_blue_measurement = blue_measurements[-1]

            # Calculate length in pixels and mm for blue lines
            blue_length_pixels = math.sqrt((latest_blue_measurement[1][0] - latest_blue_measurement[0][0]) ** 2 + (
                    latest_blue_measurement[1][1] - latest_blue_measurement[0][1]) ** 2)
            if self.calibration_done:
                blue_length_mm = blue_length_pixels / self.pixels_per_mm

            # Append the measurement information to a list
            if tooth_id == "NA":
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
            else:
                if self.calibration_done:
                    measurement_info = {
                        "tooth_id": tooth_id,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "blue_length_mm": blue_length_mm
                    }
                else:
                    measurement_info = {
                        "tooth_id": tooth_id,
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
            if tooth_id == "NA":
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
            else:
                if self.calibration_done:
                    measurement_info = {
                        "tooth_id": tooth_id,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "green_length_mm": green_length_mm
                    }
                else:
                    measurement_info = {
                        "tooth_id": tooth_id,
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

        else:
            messagebox.showinfo("Inte tillräckligt med mätningar",
                                "Det krävs minst minst en mätning för att kunna spara.")
    else:
        messagebox.showerror("Ingen bild öppen", "Öppna en bild först.")

    # Behåll linjer om function2 är aktiv
    if self.function2_enabled.get():
        if self.blue_lines:
            self.saved_lines.extend(self.blue_lines)
        if self.green_lines:
            self.saved_lines.extend(self.green_lines)
        self.blue_lines.clear()
        self.green_lines.clear()


def show_saved_measurements(self):
    if self.save_measurement_list:
        saved_measurements_window = tk.Toplevel(self.master)
        saved_measurements_window.title("Sparade mätningar")

        scrollbar = tk.Scrollbar(saved_measurements_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_area = tk.Text(saved_measurements_window, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_area.pack(fill=tk.BOTH, expand=True)

        if self.username:
            text_area.insert(tk.END, f"Examiner: {self.username}\n")

        for measurement_info in self.save_measurement_list:
            if 'filename' in measurement_info:
                text_area.insert(tk.END, f"Filename: {measurement_info['filename']}\n")
            if 'tooth_id' in measurement_info:
                text_area.insert(tk.END, f"Tooth id: {measurement_info['tooth_id']}\n")
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


def toggle_lines_visibility(self):
    if not self.saved_lines:
        messagebox.showinfo("Inga sparade mätningar", "Inga sparade mätningar att dölja")
    else:
        # Toggle the state of all lines based on the state
        new_state = "hidden" if self.lines_state == "normal" else "normal"
        self.lines_state = new_state
        for line in self.saved_lines:
            self.canvas.itemconfigure(line, state=new_state)


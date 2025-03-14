import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import math
from save_data import auto_save_measurements_as_json

def click(self, event, button):
    """Hantera klick för att starta mätningar"""
    if self.image:
        # Säkerställ att original-bilden är inställd
        if not self.original_image:
            self.original_image = self.image
            self.image_scale_x = 1.0
            self.image_scale_y = 1.0

        color = "blue" if button == "left" else "green"
        if not self.measure1:
            # Konvertera från skärmkoordinater till originalbildkoordinater
            x = (event.x - self.image_x_offset) * self.image_scale_x
            y = (event.y - self.image_y_offset) * self.image_scale_y
            self.measure1 = (x, y)

            if button == "left":
                self.canvas.bind("<B1-Motion>", lambda event: self.motion(event, color))
                self.canvas.bind("<ButtonRelease-1>", lambda event: self.release(event, color))
            else:
                self.canvas.bind("<B3-Motion>", lambda event: self.motion(event, color))
                self.canvas.bind("<ButtonRelease-3>", lambda event: self.release(event, color))
    elif not self.image:
        messagebox.showerror("No image opened", "Open an image first.")


def motion(self, event, color):
    """Hantera musrörelse när en linje ritas"""
    # Konvertera från skärmkoordinater till originalbildkoordinater
    x = (event.x - self.image_x_offset) * self.image_scale_x
    y = (event.y - self.image_y_offset) * self.image_scale_y
    self.measure2 = (x, y)

    # Ta bort endast temporära linjer av samma färg som vi ritar nu
    # Detta gör att befintliga linjer av annan färg inte påverkas
    if color == "blue":
        # Ta bort alla befintliga blå linjer
        for line in self.blue_lines:
            self.canvas.delete(line)
        self.blue_lines = []
    else:  # color == "green"
        # Ta bort alla befintliga gröna linjer
        for line in self.green_lines:
            self.canvas.delete(line)
        self.green_lines = []

    # Konvertera originalbildkoordinater tillbaka till skärmkoordinater för visning
    x1 = self.measure1[0] / self.image_scale_x + self.image_x_offset
    y1 = self.measure1[1] / self.image_scale_y + self.image_y_offset
    x2 = self.measure2[0] / self.image_scale_x + self.image_x_offset
    y2 = self.measure2[1] / self.image_scale_y + self.image_y_offset

    # Skapa en ny linje
    line = self.canvas.create_line(
        x1, y1, x2, y2,
        fill=color,
        width=2
    )

    # Lägg till linjen i rätt lista
    if color == "blue":
        self.blue_lines.append(line)
    else:
        self.green_lines.append(line)

    # Uppdatera measurements-listan
    if color == "blue":
        # Om det redan finns en mätning, ersätt den
        if self.measurements["blue"]:
            self.measurements["blue"] = [(self.measure1, self.measure2)]
        else:
            self.measurements["blue"].append((self.measure1, self.measure2))
    else:
        # Om det redan finns en mätning, ersätt den
        if self.measurements["green"]:
            self.measurements["green"] = [(self.measure1, self.measure2)]
        else:
            self.measurements["green"].append((self.measure1, self.measure2))

    # Beräkna och visa avstånd under musritning
    if self.measure1 and self.measure2:
        distance_pixels = math.sqrt(
            (self.measure2[0] - self.measure1[0]) ** 2 +
            (self.measure2[1] - self.measure1[1]) ** 2)

        if self.calibration_done:
            distance_mm = distance_pixels / self.pixels_per_mm
            # Här kan vi lägga till kod för att visa mätningen direkt
            print(f"Distance: {distance_pixels:.2f} pixels, {distance_mm:.2f} mm")
        else:
            print(f"Distance: {distance_pixels:.2f} pixels")

# Modify the release method in measurement.py
def release(self, event, color):
    if color == "blue":
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
    else:
        self.canvas.unbind("<B3-Motion>")
        self.canvas.unbind("<ButtonRelease-3>")

    if self.measure2:
        # No need to scale coordinates again as they're already in original image coordinates
        distance_pixels = math.sqrt(
            (self.measure2[0] - self.measure1[0]) ** 2 + (self.measure2[1] - self.measure1[1]) ** 2)
        if self.calibration_done:
            print(f"Distance: {distance_pixels} pixels and {distance_pixels / self.pixels_per_mm} mm")
            print(self.measure1, self.measure2)
        else:
            print(f"Distance: {distance_pixels} pixels")
    else:
        print("Measurement not completed.")

    self.measure1 = None
    self.measure2 = None

def adjust_line(self, event=None):
    """Function to adjust the position of existing lines"""
    if not self.saved_lines:
        messagebox.showinfo("No lines to adjust", "There are no saved lines to adjust.")
        return

    # Create a window to select which line to adjust
    select_window = tk.Toplevel(self.master)
    select_window.title("Select Line to Adjust")
    select_window.geometry("400x500")

    # Create a frame for the list
    list_frame = tk.Frame(select_window)
    list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Add a label with instructions
    instructions = tk.Label(list_frame, text="Select a measurement to adjust:", font=("Arial", 12, "bold"))
    instructions.pack(anchor=tk.W, pady=(0, 10))

    # Create a canvas with scrollbar for the buttons
    canvas = tk.Canvas(list_frame)
    scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add buttons for each measurement
    for i, measurement in enumerate(self.save_measurement_list):
        frame = tk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=1)
        frame.pack(fill=tk.X, padx=5, pady=5)

        # Display information about the measurement
        tooth_id = measurement.get('tooth_id', 'NA')
        info_text = f"Measurement #{i + 1} - Tooth ID: {tooth_id}"

        line_types = []
        if 'blue_coordinates' in measurement:
            blue_px = measurement.get('blue_length_pixels', 0)
            blue_text = f"Blue: {blue_px:.2f}px"
            if 'blue_length_mm' in measurement:
                blue_text += f" / {measurement['blue_length_mm']:.2f}mm"
            line_types.append(blue_text)

        if 'green_coordinates' in measurement:
            green_px = measurement.get('green_length_pixels', 0)
            green_text = f"Green: {green_px:.2f}px"
            if 'green_length_mm' in measurement:
                green_text += f" / {measurement['green_length_mm']:.2f}mm"
            line_types.append(green_text)

        # Add measurement info
        info_label = tk.Label(frame, text=info_text, font=("Arial", 10, "bold"))
        info_label.pack(anchor=tk.W)

        # Add line details
        if line_types:
            details_label = tk.Label(frame, text=", ".join(line_types))
            details_label.pack(anchor=tk.W)

        # Add buttons for each line color available
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)

        if 'blue_coordinates' in measurement:
            blue_button = tk.Button(
                button_frame,
                text="Adjust Blue Line",
                bg="lightblue",
                command=lambda idx=i, color="blue": self.prepare_line_adjustment(idx, color, select_window)
            )
            blue_button.pack(side=tk.LEFT, padx=5)

        if 'green_coordinates' in measurement:
            green_button = tk.Button(
                button_frame,
                text="Adjust Green Line",
                bg="lightgreen",
                command=lambda idx=i, color="green": self.prepare_line_adjustment(idx, color, select_window)
            )
            green_button.pack(side=tk.LEFT, padx=5)

    # Add a close button at the bottom
    close_button = tk.Button(select_window, text="Close", command=select_window.destroy)
    close_button.pack(pady=10)

def prepare_line_adjustment(self, measurement_idx, line_color, select_window):
    """Prepare for line adjustment by temporarily highlighting the selected line"""
    # Close the selection window
    select_window.destroy()

    # Get the measurement
    measurement = self.save_measurement_list[measurement_idx]

    # Ensure we have the right coordinates
    if line_color == 'blue' and 'blue_coordinates' in measurement:
        coords = measurement['blue_coordinates']
    elif line_color == 'green' and 'green_coordinates' in measurement:
        coords = measurement['green_coordinates']
    else:
        messagebox.showerror("Error", "Selected line coordinates not found.")
        return

    # Convert from original image coordinates to current screen coordinates
    # Include the offset from panning
    start_x = coords[0][0] / self.image_scale_x + self.image_x_offset
    start_y = coords[0][1] / self.image_scale_y + self.image_y_offset
    end_x = coords[1][0] / self.image_scale_x + self.image_x_offset
    end_y = coords[1][1] / self.image_scale_y + self.image_y_offset

    # Create a new popup window for adjustment
    adjust_window = tk.Toplevel(self.master)
    adjust_window.title(f"Adjust {line_color.capitalize()} Line")
    adjust_window.geometry("300x200")

    instruction_label = tk.Label(
        adjust_window,
        text="Enter new coordinates for the line endpoints:",
        wraplength=280,
        justify=tk.LEFT
    )
    instruction_label.pack(padx=10, pady=10, anchor=tk.W)

    # Create frames for start and end coordinates
    start_frame = tk.Frame(adjust_window)
    start_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(start_frame, text="Start X:").grid(row=0, column=0, sticky=tk.W)
    start_x_entry = tk.Entry(start_frame, width=8)
    start_x_entry.insert(0, str(int(start_x)))
    start_x_entry.grid(row=0, column=1, padx=5)

    tk.Label(start_frame, text="Start Y:").grid(row=0, column=2, sticky=tk.W)
    start_y_entry = tk.Entry(start_frame, width=8)
    start_y_entry.insert(0, str(int(start_y)))
    start_y_entry.grid(row=0, column=3, padx=5)

    end_frame = tk.Frame(adjust_window)
    end_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(end_frame, text="End X:").grid(row=0, column=0, sticky=tk.W)
    end_x_entry = tk.Entry(end_frame, width=8)
    end_x_entry.insert(0, str(int(end_x)))
    end_x_entry.grid(row=0, column=1, padx=5)

    tk.Label(end_frame, text="End Y:").grid(row=0, column=2, sticky=tk.W)
    end_y_entry = tk.Entry(end_frame, width=8)
    end_y_entry.insert(0, str(int(end_y)))
    end_y_entry.grid(row=0, column=3, padx=5)

    # Preview the adjusted line on the canvas
    preview_line = self.canvas.create_line(
        start_x, start_y, end_x, end_y,
        fill=line_color, width=2, dash=(4, 4), tags="preview_line"
    )

    # Add start and end point markers
    point_size = 5
    start_point = self.canvas.create_oval(
        start_x - point_size, start_y - point_size,
        start_x + point_size, start_y + point_size,
        fill=line_color, tags="preview_points")

    end_point = self.canvas.create_oval(
        end_x - point_size, end_y - point_size,
        end_x + point_size, end_y + point_size,
        fill=line_color, tags="preview_points")

    # Function to update preview when entries change
    def update_preview(*args):
        try:
            new_start_x = int(start_x_entry.get())
            new_start_y = int(start_y_entry.get())
            new_end_x = int(end_x_entry.get())
            new_end_y = int(end_y_entry.get())

            # Update line
            self.canvas.coords(preview_line, new_start_x, new_start_y, new_end_x, new_end_y)

            # Update points
            self.canvas.coords(
                start_point,
                new_start_x - point_size, new_start_y - point_size,
                new_start_x + point_size, new_start_y + point_size
            )
            self.canvas.coords(
                end_point,
                new_end_x - point_size, new_end_y - point_size,
                new_end_x + point_size, new_end_y + point_size
            )
        except ValueError:
            pass  # Invalid input, just don't update

    # Bind entry changes to preview update
    start_x_entry.bind("<KeyRelease>", update_preview)
    start_y_entry.bind("<KeyRelease>", update_preview)
    end_x_entry.bind("<KeyRelease>", update_preview)
    end_y_entry.bind("<KeyRelease>", update_preview)

    # Buttons frame
    button_frame = tk.Frame(adjust_window)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    # Apply button
    apply_button = tk.Button(
        button_frame,
        text="Apply",
        command=lambda: self.apply_line_adjustment(
            measurement_idx,
            line_color,
            int(start_x_entry.get()),
            int(start_y_entry.get()),
            int(end_x_entry.get()),
            int(end_y_entry.get()),
            adjust_window,
            [preview_line, start_point, end_point]
        )
    )
    apply_button.pack(side=tk.LEFT, padx=5)

    # Cancel button
    cancel_button = tk.Button(
        button_frame,
        text="Cancel",
        command=lambda: self.cancel_line_adjustment(
            adjust_window,
            [preview_line, start_point, end_point]
        )
    )
    cancel_button.pack(side=tk.LEFT, padx=5)

    # Handle window close event
    adjust_window.protocol(
        "WM_DELETE_WINDOW",
        lambda: self.cancel_line_adjustment(
            adjust_window,
            [preview_line, start_point, end_point]
        )
    )


def apply_line_adjustment(self, measurement_idx, line_color, start_x, start_y, end_x, end_y, window, canvas_items):
    """Apply the adjusted line coordinates and update measurements"""
    # First clean up the preview
    for item in canvas_items:
        self.canvas.delete(item)

    # Get the measurement
    measurement = self.save_measurement_list[measurement_idx]

    # Convert from screen coordinates to original image coordinates
    # First subtract the offset and then apply the scale
    new_start = (
        (start_x - self.image_x_offset) * self.image_scale_x,
        (start_y - self.image_y_offset) * self.image_scale_y
    )
    new_end = (
        (end_x - self.image_x_offset) * self.image_scale_x,
        (end_y - self.image_y_offset) * self.image_scale_y
    )

    # Update the measurement in the list
    if line_color == 'blue':
        # Update blue line coordinates
        measurement['blue_coordinates'] = (new_start, new_end)

        # Recalculate length
        blue_length_pixels = math.sqrt(
            (new_end[0] - new_start[0]) ** 2 + (new_end[1] - new_start[1]) ** 2)
        measurement['blue_length_pixels'] = blue_length_pixels

        if self.calibration_done and 'blue_length_mm' in measurement:
            measurement['blue_length_mm'] = blue_length_pixels / self.pixels_per_mm

    elif line_color == 'green':
        # Update green line coordinates
        measurement['green_coordinates'] = (new_start, new_end)

        # Recalculate length
        green_length_pixels = math.sqrt(
            (new_end[0] - new_start[0]) ** 2 + (new_end[1] - new_start[1]) ** 2)
        measurement['green_length_pixels'] = green_length_pixels

        if self.calibration_done and 'green_length_mm' in measurement:
            measurement['green_length_mm'] = green_length_pixels / self.pixels_per_mm

    # If both lines exist, recalculate ratio
    if 'blue_length_pixels' in measurement and 'green_length_pixels' in measurement:
        measurement['ratio'] = measurement['green_length_pixels'] / measurement['blue_length_pixels']

    # Redraw the line with the updated coordinates
    # We need to find and update the corresponding line in the saved_lines list
    found = False
    for i, line in enumerate(self.saved_lines):
        if self.canvas.itemcget(line, "fill") == line_color:
            self.canvas.delete(line)
            new_line = self.canvas.create_line(
                start_x, start_y, end_x, end_y,
                fill=line_color, width=2)
            self.saved_lines[i] = new_line
            found = True
            break

    # If no existing line was found, add a new one
    if not found:
        new_line = self.canvas.create_line(
            start_x, start_y, end_x, end_y,
            fill=line_color, width=2)
        self.saved_lines.append(new_line)

    # Close window
    window.destroy()

    # Show confirmation message
    messagebox.showinfo(
        "Adjustment Complete",
        f"The {line_color} line has been adjusted and measurements updated."
    )

def cancel_line_adjustment(self, window, canvas_items):
    """Cancel the line adjustment process"""
    # Clean up preview items
    for item in canvas_items:
        self.canvas.delete(item)

    # Close window
    window.destroy()


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

                    selected_rectangle = simpledialog.askstring("No match - Enter tooth",
                                                                "Available tooth names:\n" + names_string + "\n\nEnter the name of the tooth:")
                    if selected_rectangle:
                        if selected_rectangle in rectangle_names:
                            tooth_id = selected_rectangle
                        else:
                            confirm_selection = messagebox.askyesno("Confirmation",
                                                                    selected_rectangle + " was not in the list. Do you want to save?")
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
                if self.function1_enabled.get():
                    tooth_id = simpledialog.askstring("No match - Enter tooth", "Enter the name of the tooth:")
                    if not tooth_id:
                        tooth_id = "NA"
                else:
                    tooth_id = "NA"
        else:
            # No rectangles present
            if self.function1_enabled.get():
                tooth_id = simpledialog.askstring("No match - Enter tooth", "Enter the name of the tooth:")
                if not tooth_id:
                    tooth_id = "NA"
            else:
                tooth_id = "NA"

        if blue_measurements and green_measurements:
            # Get the latest measurement for blue and green - already in original image coordinates
            latest_blue_measurement = blue_measurements[-1]
            latest_green_measurement = green_measurements[-1]

            # Calculate length in pixels
            blue_length_pixels = math.sqrt(
                (latest_blue_measurement[1][0] - latest_blue_measurement[0][0]) ** 2 +
                (latest_blue_measurement[1][1] - latest_blue_measurement[0][1]) ** 2)

            green_length_pixels = math.sqrt(
                (latest_green_measurement[1][0] - latest_green_measurement[0][0]) ** 2 +
                (latest_green_measurement[1][1] - latest_green_measurement[0][1]) ** 2)

            # Calculate in mm if calibration is done
            if self.calibration_done:
                blue_length_mm = blue_length_pixels / self.pixels_per_mm
                green_length_mm = green_length_pixels / self.pixels_per_mm

            # Compute the ratio between the lengths
            ratio = green_length_pixels / blue_length_pixels

            # Append the measurement information to a list
            if tooth_id == "NA":
                if self.calibration_done:
                    measurement_info = {
                        "filename": self.image_filename,
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
                        "filename": self.image_filename,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "ratio": ratio
                    }
            else:
                if self.calibration_done:
                    measurement_info = {
                        "filename": self.image_filename,
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
                        "filename": self.image_filename,
                        "tooth_id": tooth_id,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "ratio": ratio
                    }
            self.save_measurement_list.append(measurement_info)
            # Do something with measurement_info
            # Show popup "Saved" that disappears after 1 second
            popup = tk.Toplevel(self.master)
            popup.title("Saved")

            # Get the pointer position
            x, y = self.master.winfo_pointerxy()
            popup.geometry(f"+{x}+{y}")  # Place popup relative to pointer position
            label = tk.Label(popup, text="Saving")
            label.pack(pady=5)
            popup.after(200, popup.destroy)  # Close popup after 1 second


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
                        "filename": self.image_filename,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "blue_length_mm": blue_length_mm
                    }
                else:
                    measurement_info = {
                        "filename": self.image_filename,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels
                    }
            else:
                if self.calibration_done:
                    measurement_info = {
                        "filename": self.image_filename,
                        "tooth_id": tooth_id,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels,
                        "blue_length_mm": blue_length_mm
                    }
                else:
                    measurement_info = {
                        "filename": self.image_filename,
                        "tooth_id": tooth_id,
                        "blue_coordinates": latest_blue_measurement,
                        "blue_length_pixels": blue_length_pixels
                    }
            self.save_measurement_list.append(measurement_info)
            # Do something with measurement_info
            # Show popup "Saved" that disappears after 1 second
            popup = tk.Toplevel(self.master)
            popup.title("Saved")

            # Get the pointer position
            x, y = self.master.winfo_pointerxy()
            popup.geometry(f"+{x}+{y}")  # Place popup relative to pointer position
            label = tk.Label(popup, text="Saving")
            label.pack(pady=5)
            popup.after(500, popup.destroy)  # Close popup after 1 second

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
                        "filename": self.image_filename,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "green_length_mm": green_length_mm
                    }
                else:
                    measurement_info = {
                        "filename": self.image_filename,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels
                    }
            else:
                if self.calibration_done:
                    measurement_info = {
                        "filename": self.image_filename,
                        "tooth_id": tooth_id,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels,
                        "green_length_mm": green_length_mm
                    }
                else:
                    measurement_info = {
                        "filename": self.image_filename,
                        "tooth_id": tooth_id,
                        "green_coordinates": latest_green_measurement,
                        "green_length_pixels": green_length_pixels
                    }
            self.save_measurement_list.append(measurement_info)
            # Do something with measurement_info
            # Show popup "Saved" that disappears after 1 second
            popup = tk.Toplevel(self.master)
            popup.title("Saved")

            # Get the pointer position
            x, y = self.master.winfo_pointerxy()
            popup.geometry(f"+{x}+{y}")  # Place popup relative to pointer position
            label = tk.Label(popup, text="Saving")
            label.pack(pady=5)
            popup.after(500, popup.destroy)  # Close popup after 1 second

        else:
            messagebox.showinfo("Not enough measurements",
                                "At least one measurement is required to save.")
    else:
        messagebox.showerror("No image open", "Open an image first.")

    # Keep lines if function2 is active
    if self.function2_enabled.get():
        if self.blue_lines:
            self.saved_lines.extend(self.blue_lines)
        if self.green_lines:
            self.saved_lines.extend(self.green_lines)
        self.blue_lines.clear()
        self.green_lines.clear()

    self.auto_save_measurements_as_json()

def show_saved_measurements(self):
    if self.save_measurement_list:
        saved_measurements_window = tk.Toplevel(self.master)
        saved_measurements_window.title("Saved measurements")

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
        messagebox.showinfo("No saved measurements", "No measurement data currently saved.")


def toggle_lines_visibility(self):
    if not self.saved_lines:
        messagebox.showinfo("No saved measurements", "No saved measurements to hide")
    else:
        # Toggle the state of all lines based on the state
        new_state = "hidden" if self.lines_state == "normal" else "normal"
        self.lines_state = new_state
        for line in self.saved_lines:
            self.canvas.itemconfigure(line, state=new_state)
from tkinter import filedialog, simpledialog, messagebox
import math
def set_pixels_per_mm(self):
    pixels_per_mm = simpledialog.askfloat("Ange pixlar per mm", "Ange antal pixlar per millimeter:")
    if pixels_per_mm:
        self.pixels_per_mm = pixels_per_mm
        messagebox.showinfo("Pixlar per mm inställda",
                            f"Pixlar per mm inställda till: {pixels_per_mm:.2f} vilket motsvarar pixelstorleken {1 / pixels_per_mm:.2f}")
        self.calibration_done = True


def set_pixels_size(self):
    pixels_size = simpledialog.askfloat("Ange pixelstorlek", "Ange storleken på pixlarna i millimeter:")
    if pixels_size:
        self.pixels_per_mm = 1 / pixels_size
        messagebox.showinfo("Pixelstorleken inställd",
                            f"Pixelstorleken är inställd till  {pixels_size} vilket motsvarar {self.pixels_per_mm:.2f} pixlar per mm ")
        self.calibration_done = True


def calibrate_pixels_to_mm(self):
    if self.image:
        self.calibration_done = False
        self.canvas.bind("<Button-1>", lambda event: self.calibrate_click(event))
        messagebox.showinfo("Kalibrering",
                            "Tryck ned vänster musknapp dra en linje över ett objekt med en känd längd.")
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
    distance_mm = simpledialog.askfloat("Kalibrering",
                                        "Skriv in sträckan som den den röda linjen motsvarar i millimeter:")
    if distance_mm:
        self.pixels_per_mm = distance_pixels / distance_mm
        messagebox.showinfo("Kalibrering", f"Pixlar per mm enligt kalibrering: {self.pixels_per_mm:.2f}")
        self.calibration_done = True
        self.calibration_active = False
        self.canvas.bind("<Button-1>", lambda event: self.click(event, "left"))  # Rebind left-click event
        self.canvas.bind("<Button-3>", lambda event: self.click(event, "right"))  # Rebind right-click event
    self.reset_canvas()

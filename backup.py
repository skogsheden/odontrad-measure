def click(self, event, button):
    if self.image:
        color = "blue" if button == "left" else "green"
        lines = self.blue_lines if button == "left" else self.green_lines

        if not self.measure1:
            self.measure1 = (event.x, event.y)
        else:
            if lines:
                self.canvas.delete(lines[-1])  # Delete the previous line
            self.measure2 = (event.x, event.y)
            line = self.canvas.create_line(self.measure1[0], self.measure1[1], self.measure2[0], self.measure2[1],
                                           fill=color, width=2)
            lines.append(line)
            self.measurements[color].append((self.measure1, self.measure2))
            distance_pixels = math.sqrt(
                (self.measure2[0] - self.measure1[0]) ** 2 + (self.measure2[1] - self.measure1[1]) ** 2)
            self.measure1 = None
            self.measure2 = None
            if self.calibration_done:
                print(f"Distance: {distance_pixels} pixels and {distance_pixels / self.pixels_per_mm} mm")
            else:
                print(f"Distance: {distance_pixels} pixels")
    elif not self.image:
        messagebox.showerror("Ingen bild laddad", "Ladda en bild först.")

from tkinter import simpledialog
import tkinter as tk


def start_rectangle(self, event):
    self.annotation_start_point = (event.x, event.y)
    self.annotation_previous_color = self.annotation_current_color
    self.annotation_current_color = self.generate_random_color()


def draw_rectangle(self, event):
    if self.annotation_start_point:
        if self.annotation_end_point:
            self.canvas.delete(self.rect)
        self.annotation_end_point = (event.x, event.y)

        self.rect = self.canvas.create_rectangle(self.annotation_start_point[0], self.annotation_start_point[1],
                                                 self.annotation_end_point[0], self.annotation_end_point[1],
                                                 outline=self.annotation_current_color)


def end_rectangle(self, event):
    if self.annotation_start_point and self.annotation_end_point:
        name = simpledialog.askstring("Ange tand", "Skriv in namnet på tanden:")
        if not name:
            name = "NA"  # No id provided
        if name:
            # Determine position of text
            x1, y1 = self.annotation_start_point
            x2, y2 = self.annotation_end_point
            text_x = min(x1, x2)
            text_y = min(y1, y2)

            # Store data
            rectangle = {
                "image": self.image_filename,
                "tooth_id": name,
                "coordinates": (self.annotation_start_point, self.annotation_end_point),
                "rect": self.rect,
                "text": self.canvas.create_text(text_x, text_y, text=name, anchor=tk.NW,
                                                fill=self.annotation_current_color),
                "color": self.annotation_current_color,
            }
            self.canvas.itemconfigure(rectangle["rect"], state="normal")
            self.rectangles.append(rectangle)
            # Rita namnet i det övre vänstra hörnet

        self.annotation_start_point = None
        self.annotation_end_point = None
        print(self.rectangles)


def delete_last_rectangle(self, event):
    if self.rectangles:
        print("delete")
        print(self.rectangles)
        last_rectangle = self.rectangles[-1]["rect"]
        last_text = self.rectangles[-1]["text"]
        self.canvas.delete(last_rectangle)  # Delete the rectangle from the canvas
        self.canvas.delete(last_text)
        self.rectangles.pop()
    else:
        print("Inget att radera")


def toggle_rectangles_visibility(self):
    for rectangle_data in self.rectangles:
        rectangle = rectangle_data["rect"]
        text = rectangle_data["text"]
        color = rectangle_data["color"]
        current_state = self.canvas.itemcget(rectangle, "state")
        new_state = "hidden" if current_state == "normal" else "normal"
        self.canvas.itemconfigure(rectangle, state=new_state)
        self.canvas.itemconfigure(text, state=new_state)

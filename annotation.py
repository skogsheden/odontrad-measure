from tkinter import simpledialog
import tkinter as tk
import os
import json
from PIL import Image


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
            x1 = min(self.annotation_start_point[0], self.annotation_end_point[0])
            x2 = max(self.annotation_start_point[0], self.annotation_end_point[0])
            y1 = max(self.annotation_start_point[1], self.annotation_end_point[1])
            y2 = min(self.annotation_start_point[1], self.annotation_end_point[1])

            text_x = min(x1, x2)
            text_y = min(y1, y2)

            x1 = int(x1 * self.image_scale_x)
            x2 = int(x2 * self.image_scale_x)
            y1 = int(y1 * self.image_scale_y)
            y2 = int(y2 * self.image_scale_y)

            # Store data
            rectangle = {
                "image": self.image_filename,
                "tooth_id": name,
                "coordinates": ((x1, y1), (x2, y2)),  # Store the new coordinates
                "rect": self.rect,
                "text": self.canvas.create_text(text_x, text_y, text=name, anchor=tk.NW,
                                                fill=self.annotation_current_color),
                "color": self.annotation_current_color
            }
            self.canvas.itemconfigure(rectangle["rect"], state="normal")
            self.rectangles.append(rectangle)
            print(rectangle)
            # Rita namnet i det övre vänstra hörnet

        self.annotation_start_point = None
        self.annotation_end_point = None
        self.save_annotations()


def delete_last_rectangle(self, event):
    if self.rectangles:
        last_rectangle = self.rectangles[-1]["rect"]
        last_text = self.rectangles[-1]["text"]
        self.canvas.delete(last_rectangle)  # Delete the rectangle from the canvas
        self.canvas.delete(last_text)
        self.rectangles.pop()
        self.save_annotations()
    else:
        print("Inget att radera")


def toggle_rectangles_visibility(self, event=None):
    if self.rectangles:
        for rectangle_data in self.rectangles:
            rectangle = rectangle_data["rect"]
            text = rectangle_data["text"]
            color = rectangle_data["color"]
            current_state = self.canvas.itemcget(rectangle, "state")
            new_state = "hidden" if current_state == "normal" else "normal"
            self.canvas.itemconfigure(rectangle, state=new_state)
            self.canvas.itemconfigure(text, state=new_state)
    else:
        print("Nothing to hide")


def save_annotations(self):
    # Get the filename of the image without extension
    image_filename = os.path.splitext(os.path.basename(self.image_filepath))[0]

    with Image.open(self.image_filepath) as img:
        # Get image properties
        mode_to_bpp = {'1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32, 'CMYK': 32, 'YCbCr': 24, 'I': 32, 'F': 32}
        width, height = img.size
        depth = mode_to_bpp[img.mode]

    # Save annotations only if there are any
    if self.rectangles:
        # Create a dictionary to store all annotations
        annotations = {"filename": image_filename, "annotations": [],
                       "size": [{"width": width, "height": height, "depth": depth}]}
        for rectangle_data in self.rectangles:
            xmin = min(rectangle_data["coordinates"][0][0], rectangle_data["coordinates"][1][0])
            ymin = min(rectangle_data["coordinates"][0][1], rectangle_data["coordinates"][1][1])
            xmax = max(rectangle_data["coordinates"][0][0], rectangle_data["coordinates"][1][0])
            ymax = max(rectangle_data["coordinates"][0][1], rectangle_data["coordinates"][1][1])
            annotation = {
                "name": rectangle_data["tooth_id"],
                "bndbox": {
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax
                },
            }
            annotations["annotations"].append(annotation)
        # Save the annotations to a .annot file
        annot_filename = f"{image_filename}.json"
        annot_filepath = os.path.join(os.path.dirname(self.image_filepath), annot_filename)
        with open(annot_filepath, "w") as annot_file:
            json.dump(annotations, annot_file)
        print(f"Annoteringar sparade till: {annot_filepath}")
    else:
        annot_filename = f"{image_filename}.json"
        annot_filepath = os.path.join(os.path.dirname(self.image_filepath), annot_filename)
        if os.path.exists(annot_filepath):
            os.remove(annot_filepath)
            print(f"Inga annoteringar kvar, raderar filen: {annot_filepath}")
        else:
            print("Inget att spara")


def load_annotations(self):
    # Get the filename of the image without extension
    image_filename = os.path.splitext(os.path.basename(self.image_filepath))[0]
    # Check if annotation file exists
    annot_filename = f"{image_filename}.json"
    annot_filepath = os.path.join(os.path.dirname(self.image_filepath), annot_filename)
    if os.path.exists(annot_filepath):
        with open(annot_filepath, "r") as annot_file:
            annotations = json.load(annot_file)
        # Draw rectangles based on annotations
        for annotation in annotations["annotations"]:
            tooth_id = annotation["name"]
            xmin = annotation["bndbox"]["xmin"]
            ymin = annotation["bndbox"]["ymin"]
            xmax = annotation["bndbox"]["xmax"]
            ymax = annotation["bndbox"]["ymax"]
            coordinates = ((xmin, ymax), (xmax, ymin))
            color = self.generate_random_color()

            # Recalculate to fit screen
            img_x1, img_y1 = coordinates[0]
            img_x2, img_y2 = coordinates[1]

            x1 = img_x1 / self.image_scale_x
            x2 = img_x2 / self.image_scale_x
            y1 = img_y1 / self.image_scale_y
            y2 = img_y2 / self.image_scale_y

            text_x = min(x1, x2)
            text_y = min(y1, y2)
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color)
            text = self.canvas.create_text(text_x, text_y, text=tooth_id, anchor=tk.NW, fill=color)

            # Add the loaded rectangle to self.rectangles
            self.rectangles.append({
                "tooth_id": tooth_id,
                "coordinates": coordinates,
                "rect": rect,
                "text": text,
                "color": color
            })
        print(f"Annoteringar laddade från: {annot_filepath}")
    else:
        print("Inga annoteringar funna!")

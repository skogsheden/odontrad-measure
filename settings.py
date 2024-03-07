import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import json


def show_program_info(self):
    info_text = """
    Mät avståndet mellan två punkter i röntgenbilder
    som pixlar, mm eller relativa mått mellan två 
    mätningar. 
    
    Annotera bilderna med tandnummer för
    att automatisk registera tandnummer för mätningar. 

    Version: 0.1.4 (2024.03)
    Skapat av: Nils Gustafsson 
    """
    messagebox.showinfo("Om", info_text)


def show_shortcuts(self):
    shortcut_text = """
    Mätning:
    - Vänsterklicka: Rita blå linje. 
    - Högerklicka: Rita en grön linje.
    - Tryck på 's': Spara mätningen

    Annotering:
    - Tryck på 'h': För att växla mellan visa/dölja.
    - Tryck på 'Esc/Escape': Avsluta annotering.
    
    Övergripande:
    - Tryck på 'q': Avsluta programmet
    """
    messagebox.showinfo("Kortkommandon", shortcut_text)


def open_settings_window(self):
    self.settings_window = tk.Toplevel(self.master)
    self.settings_window.title("Inställningar")
    string_var = tk.StringVar()
    string_var.set(self.username)

    # Ställ in storlek och padding
    self.settings_window.geometry("400x200")
    self.settings_window['padx'] = 10
    self.settings_window['pady'] = 10

    # Skapa etiketter och kryssrutor för att visa och ändra variablernas värden
    tk.Label(self.settings_window, text="Granskare:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    self.username_entry = tk.Entry(self.settings_window, textvariable=string_var)
    self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

    tk.Label(self.settings_window, text="Ange tand och yta vid inmatning:").grid(row=1, column=0, sticky=tk.W,
                                                                                 padx=10, pady=5)
    self.function1_checkbox = tk.Checkbutton(self.settings_window, variable=self.function1_enabled)
    self.function1_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

    tk.Label(self.settings_window, text="Behåll sparade mätningar:").grid(row=2, column=0, sticky=tk.W, padx=10,
                                                                          pady=5)
    self.function2_checkbox = tk.Checkbutton(self.settings_window, variable=self.function2_enabled)
    self.function2_checkbox.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    # Lägg till en knapp för att spara ändringar och stänga fönstret
    save_button = tk.Button(self.settings_window, text="Spara", command=self.save_user)
    save_button.grid(row=4, column=0, columnspan=2, pady=10)


def save_user(self):
    self.username = self.username_entry.get()
    self.save_settings()
    self.settings_window.destroy()


def save_settings(self):
    settings = {
        "username": self.username,
        "function1_enabled": self.function1_enabled.get(),
        "function2_enabled": self.function2_enabled.get(),

    }
    with open("settings.cfg", "w") as file:
        json.dump(settings, file)


def load_settings(self):
    try:
        with open("settings.cfg", "r") as file:
            settings = json.load(file)
            self.username = settings.get("username", "")
            self.function1_enabled.set(settings.get("function1_enabled", False))
            self.function2_enabled.set(settings.get("function2_enabled", False))
    except FileNotFoundError:
        # Default settings if the file doesn't exist
        self.username = ""
        self.function1_enabled.set(False)
        self.function2_enabled.set(False)


def clear_all_saved(self):
    for line in self.blue_lines:
        self.canvas.delete(line)
    for line in self.green_lines:
        self.canvas.delete(line)
    for line in self.saved_lines:
        self.canvas.delete(line)
    self.blue_lines.clear()
    self.green_lines.clear()
    self.saved_lines.clear()
    self.measurements.clear()
    self.save_measurement_list.clear()
    self.measurements = {"blue": [], "green": []}  # Separate measurements for blue and green lines
    self.measure1 = None
    self.measure2 = None


def reset_canvas(self):
    for line in self.blue_lines:
        self.canvas.delete(line)
    for line in self.green_lines:
        self.canvas.delete(line)
    self.blue_lines.clear()
    self.green_lines.clear()
    self.measure1 = None
    self.measure2 = None

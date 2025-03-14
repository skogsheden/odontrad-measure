import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import json


def show_program_info(self):
    """Shows a nicely formatted program information dialog"""
    info_window = tk.Toplevel(self.master)
    info_window.title("About OdontRad-Measure")
    info_window.geometry("600x600")
    info_window.resizable(False, False)

    # Set icon if available
    try:
        info_window.iconbitmap("icon.ico")
    except:
        pass

    # Main frame with padding
    main_frame = tk.Frame(info_window, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Program title with larger font
    title_label = tk.Label(main_frame, text="OdontRad-Measure", font=("Arial", 18, "bold"))
    title_label.pack(pady=(0, 10))

    # Program description with wrapped text
    desc_text = "A specialized tool for dental X-ray analysis allowing precise measurements between points in dental radiographs as pixels, millimeters, or as ratios between paired measurements."
    desc_label = tk.Label(main_frame, text=desc_text, wraplength=450, justify=tk.CENTER)
    desc_label.pack(pady=(0, 15))

    # Separator line
    separator = tk.Frame(main_frame, height=1, bg="gray")
    separator.pack(fill=tk.X, pady=5)

    # Features section with better formatting
    features_frame = tk.Frame(main_frame)
    features_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    features_title = tk.Label(features_frame, text="Features:", font=("Arial", 10, "bold"))
    features_title.pack(anchor=tk.W)

    features = [
        "Measure distances using blue (left click) or green (right click) lines",
        "Calibrate measurements using known reference points",
        "Annotate images with bounding boxes and tooth IDs for automatic association",
        "Zoom, pan and adjust image brightness/contrast for optimal viewing",
        "Save and load measurements for later analysis",
        "Export measurement data for research or clinical documentation",
        "Organize and navigate through multiple images"
    ]

    for feature in features:
        feature_frame = tk.Frame(features_frame)
        feature_frame.pack(fill=tk.X, pady=2)

        bullet = tk.Label(feature_frame, text="•", width=2)
        bullet.pack(side=tk.LEFT)

        feature_text = tk.Label(feature_frame, text=feature, wraplength=420, justify=tk.LEFT, anchor=tk.W)
        feature_text.pack(side=tk.LEFT, fill=tk.X)

    # Additional info
    add_info = tk.Label(main_frame,
                        text="Measurements can be adjusted after creation, and visibility can be toggled for clearer image analysis. Includes keyboard shortcuts for all major functions.",
                        wraplength=450, justify=tk.CENTER)
    add_info.pack(pady=10)

    # Separator line
    separator2 = tk.Frame(main_frame, height=1, bg="gray")
    separator2.pack(fill=tk.X, pady=5)

    # Version and author info
    version_label = tk.Label(main_frame, text="Version: 0.2.1 (2025.03)", font=("Arial", 9))
    version_label.pack()

    author_label = tk.Label(main_frame, text="Created by: Nils Gustafsson", font=("Arial", 9))
    author_label.pack()

    email_frame = tk.Frame(main_frame)
    email_frame.pack(pady=(0, 10))

    email_label = tk.Label(email_frame, text="Email: ", font=("Arial", 9))
    email_label.pack(side=tk.LEFT)

    email_value = tk.Label(email_frame, text="nils.gustafsson@umu.se",
                           fg="blue", cursor="hand2", font=("Arial", 9, "underline"))
    email_value.pack(side=tk.LEFT)

    # Make email clickable to open mail client
    email_value.bind("<Button-1>", lambda e: self.open_email("nils.gustafsson@umu.se"))

    # OK button at the bottom
    ok_button = tk.Button(main_frame, text="OK", width=10, command=info_window.destroy)
    ok_button.pack(pady=(10, 0))

    # Center the window on the screen
    info_window.update_idletasks()
    width = info_window.winfo_width()
    height = info_window.winfo_height()
    x = (info_window.winfo_screenwidth() // 2) - (width // 2)
    y = (info_window.winfo_screenheight() // 2) - (height // 2)
    info_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Make sure this window is on top and has focus
    info_window.transient(self.master)
    info_window.grab_set()
    self.master.wait_window(info_window)


def open_email(self, email):
    """Opens the default email client with the specified email address"""
    import webbrowser
    webbrowser.open('mailto:' + email)


def show_shortcuts(self):
    """Shows a nicely formatted keyboard shortcuts dialog with improved fonts and layout"""
    shortcuts_window = tk.Toplevel(self.master)
    shortcuts_window.title("Keyboard Shortcuts")
    shortcuts_window.geometry("550x500")  # Wider window
    shortcuts_window.resizable(True, True)

    # Set icon if available
    try:
        shortcuts_window.iconbitmap("icon.ico")
    except:
        pass

    # Main frame with padding
    main_frame = tk.Frame(shortcuts_window, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Program title with larger font
    title_label = tk.Label(main_frame, text="Keyboard Shortcuts", font=("Arial", 18, "bold"))
    title_label.pack(pady=(0, 15))

    # Create a frame for the canvas and scrollbar
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    # Create canvas with scrollbar
    canvas = tk.Canvas(canvas_frame)
    scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the canvas scrolling
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Create a window within the canvas for the scrollable frame
    canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux scroll down

    # Helper function to create a section of shortcuts
    def create_shortcut_section(title, shortcuts):
        section_frame = tk.Frame(scrollable_frame)
        section_frame.pack(fill=tk.X, pady=(0, 15), padx=5)

        section_label = tk.Label(section_frame, text=title, font=("Arial", 12, "bold"))
        section_label.pack(anchor=tk.W)

        # Separator line
        separator = tk.Frame(section_frame, height=1, bg="gray")
        separator.pack(fill=tk.X, pady=5)

        # Create a table-like layout
        for key, desc in shortcuts:
            shortcut_frame = tk.Frame(section_frame)
            shortcut_frame.pack(fill=tk.X, pady=3)

            # Use a nicer font for keys and more width
            key_label = tk.Label(shortcut_frame, text=key, font=("Arial", 10), width=15, anchor=tk.W)
            key_label.pack(side=tk.LEFT, padx=(10, 0))

            desc_label = tk.Label(shortcut_frame, text=desc, font=("Arial", 10),
                                  wraplength=380, justify=tk.LEFT, anchor=tk.W)
            desc_label.pack(side=tk.LEFT, fill=tk.X, padx=(5, 0))

    # Create all sections
    create_shortcut_section("File Operations", [
        ("o", "Open image"),
        ("p", "Open folder with images"),
        ("q", "Exit the program")
    ])

    create_shortcut_section("Image Navigation", [
        ("n", "Next image"),
        ("b", "Previous image"),
        ("+", "Zoom in"),
        ("-", "Zoom out"),
        ("0", "Reset zoom"),
        ("Mouse wheel", "Zoom in/out"),
        ("Middle mouse", "Pan image (when zoomed)")
    ])

    create_shortcut_section("Measurement", [
        ("Left click", "Draw blue line"),
        ("Right click", "Draw green line"),
        ("s", "Save current measurement"),
        ("g", "Toggle visibility of saved lines"),
        ("v", "Show all saved measurements")
    ])

    create_shortcut_section("Annotation", [
        ("a", "Start/stop annotation mode"),
        ("h", "Toggle visibility of annotations"),
        ("Space", "Save empty annotation and move to next image"),
        ("Right click", "Delete the last annotation (when in annotation mode)")
    ])

    create_shortcut_section("Calibration", [
        ("c", "Start calibration mode")
    ])

    # Add a close button at the bottom
    ok_button = tk.Button(main_frame, text="OK", width=10, command=shortcuts_window.destroy)
    ok_button.pack(pady=(10, 0))

    # Center the window on the screen
    shortcuts_window.update_idletasks()
    width = shortcuts_window.winfo_width()
    height = shortcuts_window.winfo_height()
    x = (shortcuts_window.winfo_screenwidth() // 2) - (width // 2)
    y = (shortcuts_window.winfo_screenheight() // 2) - (height // 2)
    shortcuts_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Make sure this window is on top and has focus
    shortcuts_window.transient(self.master)
    shortcuts_window.grab_set()

    # Clean up the mousewheel binding when closing
    def on_close():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        shortcuts_window.destroy()

    shortcuts_window.protocol("WM_DELETE_WINDOW", on_close)
    ok_button.config(command=on_close)

    self.master.wait_window(shortcuts_window)

def open_settings_window(self):
    self.settings_window = tk.Toplevel(self.master)
    self.settings_window.title("Settings")
    string_var = tk.StringVar()
    string_var.set(self.username)

    # Set size and padding
    self.settings_window.geometry("400x200")
    self.settings_window['padx'] = 10
    self.settings_window['pady'] = 10

    # Create labels and checkboxes to display and change variable values
    tk.Label(self.settings_window, text="Examiner:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    self.username_entry = tk.Entry(self.settings_window, textvariable=string_var)
    self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

    tk.Label(self.settings_window, text="Specify tooth and surface when entering:").grid(row=1, column=0, sticky=tk.W,
                                                                                         padx=10, pady=5)
    self.function1_checkbox = tk.Checkbutton(self.settings_window, variable=self.function1_enabled)
    self.function1_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

    tk.Label(self.settings_window, text="Keep saved measurements:").grid(row=2, column=0, sticky=tk.W, padx=10,
                                                                         pady=5)
    self.function2_checkbox = tk.Checkbutton(self.settings_window, variable=self.function2_enabled)
    self.function2_checkbox.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    # Add a button to save changes and close the window
    save_button = tk.Button(self.settings_window, text="Save", command=self.save_user)
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
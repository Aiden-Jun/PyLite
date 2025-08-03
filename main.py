import tkinter as tk
from tkinter import PhotoImage, ttk, font
from tkinter import filedialog
from ttkbootstrap import Style
import subprocess
from PIL import Image, ImageTk
import re
import os
import ctypes
from pathlib import Path


class TextEditor(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Define font
        editor_font = ("Consolas", 15)  # Change the size as needed

        self.text = tk.Text(self, wrap="word", undo=True, font=editor_font)

        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<Key>", self.update_syntax_highlighting)
        self.text.bind("<Control-s>", lambda event: save_file())

    def update_syntax_highlighting(self, event=None):
        if dynamic_file_path:
            self.apply_syntax_highlighting()

    def apply_syntax_highlighting(self):
        self.text.tag_remove("keyword", "1.0", tk.END)
        self.text.tag_remove("string", "1.0", tk.END)
        self.text.tag_remove("variable", "1.0", tk.END)
        self.text.tag_remove("attribute", "1.0", tk.END)

        keywords = [
            "if",
            "else",
            "elif",
            "while",
            "for",
            "in",
            "def",
            "class",
            "import",
            "from",
            "quit",
            "print",
            "input",
            "return",
        ]
        keyword_regex = r"\b(" + "|".join(keywords) + r")\b"
        string_regex = r"(\'[^\']*\'|\"[^\"]*\")"
        attribute_regex = r"(?<=\.)[a-zA-Z]+\("
        variable_regex = r"(?:[^a-zA-Z]|^)([a-zA-Z_][a-zA-Z0-9_]*)\s*=?="

        self.text.tag_configure("keyword", foreground="#0497d1")
        self.text.tag_configure("string", foreground="#4fed4c")
        self.text.tag_configure("variable", foreground="#61afef")
        self.text.tag_configure("attribute", foreground="#f0e986")

        code = self.text.get("1.0", "end")

        for tag, pattern in [
            ("keyword", keyword_regex),
            ("string", string_regex),
            ("attribute", attribute_regex),
            ("variable", variable_regex),
        ]:
            for match in re.finditer(pattern, code):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text.tag_add(tag, start, end)


def switch_to_main_menu():
    main_editor.pack_forget()
    settings_page.pack_forget()
    main_menu.pack(fill="both", expand=True)


def switch_to_main_editor():
    main_menu.pack_forget()
    settings_page.pack_forget()
    main_editor.pack(fill="both", expand=True)


def switch_to_settings():
    main_menu.pack_forget()
    main_editor.pack_forget()
    settings_page.pack(fill="both", expand=True)


dynamic_file_path = None  # global variable to store the file path


def run():
    global dynamic_file_path  # Access the global variable

    code = editor.text.get("1.0", tk.END)

    # Check if the file has been saved
    if not code.strip():
        # If the editor is empty prompt user to input some code
        save_file_as()
        return

    # If the file path is not set prompt the user to save
    if dynamic_file_path is None:
        dynamic_file_path = filedialog.asksaveasfilename(
            defaultextension=".py", filetypes=[("Python Files", "*.py")]
        )
        if not dynamic_file_path:
            return  # User canceled

        # Save the code to the selected path
        with open(dynamic_file_path, "w") as f:
            f.write(code)

    # Execute file directly
    subprocess.Popen(["start", "cmd", "/K", "python", dynamic_file_path], shell=True)


def new_file():
    editor.text.delete("1.0", tk.END)
    dynamic_file_path = None
    update_file_name_label("")


def open_file_asker():
    global dynamic_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    open_file(file_path)


def open_file(file_path):
    global dynamic_file_path
    if file_path:
        with open(file_path, "r") as f:
            content = f.read()
            editor.text.delete("1.0", tk.END)
            editor.text.insert("1.0", content)
            if file_path.endswith(".py"):
                editor.after_idle(lambda: editor.update_syntax_highlighting())
        dynamic_file_path = file_path
        update_file_name_label(dynamic_file_path)


def update_file_name_label(file_path):
    if file_path:
        file_name = os.path.basename(file_path)
        file_name_label.config(text=file_name)
    else:
        file_name_label.config(text="")


def save_file_as():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".py", filetypes=[("Python Files", "*.py")]
    )
    if file_path:
        with open(file_path, "w") as f:
            text_content = editor.text.get("1.0", tk.END)
            f.write(text_content)

        dynamic_file_path = file_path  # Update global variable
        update_file_name_label(dynamic_file_path)

        # Reload tree view if it belongs to an opened folder
        folder_path = Path(file_path).parent
        for item in file_explorer.get_children():
            file_explorer.delete(item)
        fsobjects.clear()

        root_iid = insert_item(folder_path.name, folder_path, "")
        load_tree(folder_path, root_iid)
        file_explorer.item(root_iid, open=True)


def save_file():
    global dynamic_file_path  # Access the global variable

    # If the file has already been saved, overwrite it
    if dynamic_file_path:
        with open(dynamic_file_path, "w") as f:
            text_content = editor.text.get("1.0", tk.END)
            f.write(text_content)
    else:
        # If the file has not been saved yet, prompt the user to save it
        save_file_as()


grabbed = False


def on_mouse_press(event):
    if grabbed == False:
        global last_x, last_y
        last_x = eventx = event.x
        last_y = event.y


def on_mouse_drag(event):
    if grabbed == False:
        if not isinstance(event.widget, (tk.Text, ttk.Entry)):
            x = event.x - last_x + root.winfo_x()
            y = event.y - last_y + root.winfo_y()
            root.geometry(f"+{x}+{y}")


def on_window_resize(event):
    root.update_idletasks()


def on_grip_press(event):
    global grabbed
    grabbed = True


def on_grip_release(event):
    global grabbed
    grabbed = False


# Initialize the main application window
root = tk.Tk()
root.title("PyLite")
root.geometry("1200x800")
root.iconbitmap("pylite.ico")

icon = PhotoImage(file="pylite.png")
root.iconphoto(False, icon)


def close_window():
    root.destroy()


# Load the logo image from URL for the navigation bar
navbar_logo_path = "pylite.png"  # Update with your actual file path
navbar_logo_image = Image.open(navbar_logo_path)
navbar_resized_logo_image = ImageTk.PhotoImage(navbar_logo_image.resize((35, 35)))

# Set the theme using ttkbootstrap
style = Style(theme="darkly")
style.configure("Treeview", font=("Helvetica", 13))
style.configure("Treeview", font=("Helvetica", 13), rowheight=30)
style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
# Load PNG images
img_open = ImageTk.PhotoImage(
    Image.open("opened.png").resize((15, 15)), name="img_open", master=root
)
img_close = ImageTk.PhotoImage(
    Image.open("closed.png").resize((15, 15)), name="img_close", master=root
)

# Create a transparent placeholder image (1px wide, invisible) for spacing
img_placeholder = ImageTk.PhotoImage(
    Image.new("RGBA", (1, 1), (0, 0, 0, 0)), name="img_placeholder", master=root
)


def apply_custom_treeview():
    # Custom indicator element
    style.element_create(
        "Treeitem.myindicator",
        "image",
        "img_close",
        ("user1", "!user2", "img_open"),
        ("user2", "img_placeholder"),
        sticky="w",
        width=15,
    )

    # Replace default indicator with the custom one
    style.layout(
        "Treeview.Item",
        [
            (
                "Treeitem.padding",
                {
                    "sticky": "nswe",
                    "children": [
                        ("Treeitem.myindicator", {"side": "left", "sticky": ""}),
                        ("Treeitem.image", {"side": "left", "sticky": ""}),
                        (
                            "Treeitem.focus",
                            {
                                "side": "left",
                                "sticky": "",
                                "children": [
                                    ("Treeitem.text", {"side": "left", "sticky": ""})
                                ],
                            },
                        ),
                    ],
                },
            )
        ],
    )


apply_custom_treeview()

# Create two frames for two screens
main_menu = tk.Frame(root, bg="#282c34")
main_editor = tk.Frame(root, bg="#282c34")
settings_page = tk.Frame(root, bg="#282c34")

main_content = tk.Frame(main_menu)

main_logo = tk.Frame(main_content)

logo_path = "pylite.png"  # Use relative path or full path if needed
logo_image = Image.open(logo_path)
resized_logo_image = ImageTk.PhotoImage(logo_image.resize((100, 100)))

# Display the logo image
logo_label = ttk.Label(main_logo, image=resized_logo_image)
logo_label.pack(padx=10, pady=10, side="left")

big_logo_text_label = ttk.Label(main_logo, text="PyLite", font=("Helvetica", 70))
big_logo_text_label.pack(padx=10, pady=20, side="left")

main_logo.pack(side="top")

# Add widgets to the main menu
button_font = ("Helvetica", 16)

button_to_main_editor = tk.Button(
    main_content,
    text="Editor",
    width=35,
    height=2,
    command=switch_to_main_editor,
    font=button_font,
)
button_to_main_editor.pack(pady=5)

button_to_settings = tk.Button(
    main_content,
    text="Settings",
    width=35,
    height=2,
    command=switch_to_settings,
    font=button_font,
)
button_to_settings.pack(pady=5)

main_content.pack(fill="both", expand=True, pady=10, padx=10)

# Add navigation bar to the settings page
settings_navbar = tk.Frame(settings_page, bg="#282c34", height=40)
settings_navbar.pack(side="top", fill="x", pady=5)

settings_to_menu_button = ttk.Button(
    settings_navbar, text="Menu", bootstyle="warning", command=switch_to_main_menu
)
settings_to_menu_button.pack(side="left", padx=10, pady=5)

# Add widgets to the settings page
settings_label = ttk.Label(
    settings_page, text="Settings", font=("helvetica", 30, "bold")
)
settings_label.pack(side="top", pady=(10, 20))

# Create a frame to contain theme-related widgets
theme_frame = ttk.Frame(settings_page, padding=20)
theme_frame.pack()

theme_label = ttk.Label(theme_frame, text="Theme:", font=("helvetica", 12))
theme_label.grid(row=0, column=0, sticky="w", padx=(0, 10))


light_themes = ["Cosmo", "Minty", "Pulse", "Morph", "Lumen"]
dark_themes = ["Darkly", "Cyborg", "Vapor", "Solar"]

# Function to change the theme
def change_theme():
    selected_theme = theme_var.get()
    style.theme_use(selected_theme.lower())
    # Reapply custom Treeview font and rowheight after theme change
    style.configure("Treeview", font=("Helvetica", 13))
    style.configure("Treeview", font=("Helvetica", 13), rowheight=30)
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
    apply_custom_treeview()


# Create a variable to store the selected theme
theme_var = tk.StringVar(settings_page)
theme_var.set("Darkly")  # Set default theme

# Theme selector dropdown
available_themes = light_themes + dark_themes
theme_selector = ttk.Combobox(
    theme_frame,
    textvariable=theme_var,
    values=available_themes,
    width=30,
    state="readonly",
)
theme_selector.grid(row=0, column=1, sticky="w")

# Button to apply theme
apply_theme_button = ttk.Button(theme_frame, text="Apply Theme", command=change_theme)
apply_theme_button.grid(row=0, column=2, padx=(10, 0), sticky="w")

# Add widgets to the main editor
nav_bar = tk.Frame(main_editor, bg="#282c34", height=40)
nav_bar.pack(side="top", fill="x")


button_to_main_menu = ttk.Button(
    nav_bar, text="Menu", bootstyle="warning", command=switch_to_main_menu
)
button_to_main_menu.pack(side="left", padx=0, pady=0, ipadx=0, ipady=0)

button_run = ttk.Button(nav_bar, text="Run", bootstyle="success", command=run)
button_run.pack(side="left", padx=0, pady=0, ipadx=0, ipady=0)

file_name_label = ttk.Label(nav_bar, text="")
file_name_label.pack(side="left", padx=10, pady=5)

button_open = ttk.Button(nav_bar, text="Open", command=open_file_asker)
button_open.pack(side="right", padx=0, pady=0, ipadx=0, ipady=0)


def open_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        # Clear existing tree items
        for item in file_explorer.get_children():
            file_explorer.delete(item)
        fsobjects.clear()

        path = Path(folder_path)
        # Insert root folder as the top-level item
        root_iid = insert_item(path.name, path, "")
        load_tree(path, root_iid)
        file_explorer.item(root_iid, open=True)  # Expand root folder by default


button_open_folder = ttk.Button(nav_bar, text="Open Folder", command=open_folder)
button_open_folder.pack(side="right", padx=0, pady=0, ipadx=0, ipady=0)


button_save_as = ttk.Button(nav_bar, text="Save As", command=save_file_as)
button_save_as.pack(side="right", padx=0, pady=0, ipadx=0, ipady=0)

button_save = ttk.Button(nav_bar, text="Save", command=save_file)
button_save.pack(side="right", padx=0, pady=0, ipadx=0, ipady=0)

button_new = ttk.Button(nav_bar, text="New", command=new_file)
button_new.pack(side="right", padx=0, pady=0, ipadx=0, ipady=0)


midsection = ttk.PanedWindow(main_editor, orient="horizontal")
midsection.pack(fill="both", expand=True, padx=0, pady=0)

file_frame = ttk.Frame(midsection, width=300)
editor_frame = ttk.Frame(midsection)

fsobjects = {}


def safe_iterdir(path: Path):
    try:
        return tuple(path.iterdir())
    except PermissionError:
        print("You don't have permission to read", path)
        return ()


def insert_item(name: str, path: Path, parent: str = ""):
    iid = file_explorer.insert(parent, tk.END, text=name, tags=("fstag",))
    fsobjects[iid] = path
    return iid


def load_tree(path: Path, parent: str = ""):
    for fsobj in safe_iterdir(path):
        fullpath = path / fsobj
        child = insert_item(fsobj.name, fullpath, parent)
        if fullpath.is_dir():
            for sub_fsobj in safe_iterdir(fullpath):
                insert_item(sub_fsobj.name, fullpath / sub_fsobj, child)


def load_subitems(iid: str):
    for child_iid in file_explorer.get_children(iid):
        if fsobjects[child_iid].is_dir():
            load_tree(fsobjects[child_iid], parent=child_iid)


def on_item_opened(event):
    iid = file_explorer.selection()[0]
    load_subitems(iid)


def on_item_selected(event):
    selected = file_explorer.selection()
    if selected:
        iid = selected[0]
        path = fsobjects.get(iid)
        if path:
            if path.is_dir() == False:
                open_file(str(path))


style.layout(
    "Custom.Treeview",
    [
        ("Treeview.treearea", {"sticky": "nswe"}),
        ("Custom.Treeitem.indicator", {"side": "left", "sticky": ""}),
    ],
)

file_explorer = ttk.Treeview(file_frame, show="tree", style="Custom.Treeview")
file_explorer.pack(fill="both", expand=True, padx=(0, 5))
file_explorer.tag_bind("fstag", "<<TreeviewOpen>>", on_item_opened)
file_explorer.bind("<<TreeviewSelect>>", on_item_selected)

editor = TextEditor(editor_frame)
editor.pack(fill="both", expand=True, padx=(5, 0))

midsection.add(file_frame, weight=1)
midsection.add(editor_frame, weight=4)  # Weight 4 means editor gets 4 times space


def maintain_split(event=None):
    total_width = midsection.winfo_width()
    midsection.sashpos(0, int(total_width * 0.2))  # 20% for left pane


midsection.bind("<Configure>", maintain_split)
root.after(50, maintain_split)

main_menu.pack(fill="both", expand=True)

grip = ttk.Sizegrip(main_menu)
grip.place(relx=1.0, rely=1.0, anchor="se")
grip.lift(main_content)

editor_grip = ttk.Sizegrip(main_editor)
editor_grip.place(relx=1.0, rely=1.0, anchor="se")

settings_grip = ttk.Sizegrip(settings_page)
settings_grip.place(relx=1.0, rely=1.0, anchor="se")


def start_move(event):
    root.x = event.x
    root.y = event.y


def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")


root.mainloop()

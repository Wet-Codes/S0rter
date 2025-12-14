import shutil
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime

# ------------------------------
# CONFIGURATION
# ------------------------------

USE_DATE_FOLDERS = False  # toggled by GUI
BASE_DIR  = None


IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".avif"}
DOC_EXT = {".pdf", ".txt", ".docx", ".doc", ".odt", ".odp"}
ART_EXT  = {".sai", ".webp", ".clip"}
ICON_EXT = {".ico", ".svg"}
SHORTCUT_EXT = {".lnk"}
VIDEO_EXT = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".mpeg", ".mpg", ".3gp", ".m4v", ".ts", ".vob", ".ogv",
    ".rm", ".rmvb", ".asf", ".divx", ".f4v", ".mts", ".m2ts"
}
CODE_EXT = {
    ".py", ".java", ".c", ".cpp", ".h", ".hpp",
    ".js", ".ts", ".jsx", ".tsx",
    ".html", ".css", ".scss",
    ".php", ".rb", ".go", ".rs",
    ".swift", ".kt",
    ".cs", ".vb",
    ".sh", ".bat", ".ps1",
    ".sql", ".json", ".xml", ".yaml", ".yml"
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger()

# Config target folders 

def get_category(extension: str) -> str:
    """Return file category based on extension."""
    ext = extension.lower()

    if ext in IMAGE_EXT:
        return "Images"
    if ext in DOC_EXT:
        return "Documents"
    if ext in SHORTCUT_EXT:
        return "Shortcuts"
    if ext in ICON_EXT:
        return "Icons"
    if ext in ART_EXT:
        return "Arts"
    if ext in VIDEO_EXT:
        return "Videos"
    if ext in CODE_EXT:
        return "Codes"
    
    return "Others"

#  folders paths
def get_month_folder(file: Path) -> str:
    """Return YYYY-MM month folder from file modified date."""
    timestamp = file.stat().st_mtime
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%B %Y")


def sort_file(file: Path):
    """Sort a single file into proper folder category."""
    if file.is_dir():
        return

    
   
    category = get_category(file.suffix)

    if USE_DATE_FOLDERS:
        month_folder = get_month_folder(file)
        target_folder = BASE_DIR / category / month_folder
    else:
        target_folder = BASE_DIR / category


    target_folder.mkdir(parents=True, exist_ok=True)


#  Logging (console stuff)

    try:
        shutil.move(str(file), str(target_folder / file.name))
        if USE_DATE_FOLDERS:
            logging.info(f"Moved: {file.name} → {month_folder}/{category}")
        else:
            logging.info(f"Moved: {file.name} → {category}")
    except Exception as e:
        logging.error(f"Failed to move {file.name}: {e}")


# ------------------------------
# FINAL EXECUTION
# ------------------------------



def sort_all_files():
    global BASE_DIR
    if not BASE_DIR.exists():
        logging.error("Source folder does not exist!")
        return

    for file in BASE_DIR.iterdir():
        sort_file(file)

    logging.info("Sorting complete.")


# ------------------------------
# GUI
# ------------------------------


class TkTextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(
            0,
            self._append,
            msg
        )

    def _append(self, msg):
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")


def launch_gui():
    global BASE_DIR, USE_DATE_FOLDERS

    root = tk.Tk()
    root.title("File Sorter")
    root.geometry("400x220")
    log_text = tk.Text(root, height=8, state="disabled")
    log_text.pack(fill="both", padx=10, pady=5)

    for handler in logging.getLogger().handlers[:]:
        if isinstance(handler, TkTextHandler):
            logging.getLogger().removeHandler(handler)

    gui_handler = TkTextHandler(log_text)
    gui_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s")
    )
    logging.getLogger().addHandler(gui_handler)




    date_var = tk.BooleanVar(value=False)

    def choose_base():
        global BASE_DIR, USE_DATE_FOLDERS

        path = filedialog.askdirectory(title="Select Folder to Sort")
        if path:
            BASE_DIR = Path(path)

    def start_sort():
        global BASE_DIR, USE_DATE_FOLDERS

        if not BASE_DIR:
            messagebox.showerror("Error", "Please select a folder")
            return

        USE_DATE_FOLDERS = date_var.get()
        root.destroy()
        sort_all_files()

    tk.Button(root, text="Select Folder", command=choose_base).pack(pady=10)

    tk.Checkbutton(
        root,
        text="Sort with Month & Year folders",
        variable=date_var
    ).pack(pady=5)

    tk.Button(root, text="Start Sorting", command=start_sort).pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
        launch_gui()
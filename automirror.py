from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from mirror_auto import mirror_auto
from mirror_path import mirror_path_file, default_output_path


# --- Functions to select auto and pathfiles and mirror them ---
def select_and_mirror_auto():
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("Auto files", "*.auto"), ("All files", "*.*")]
    )
    if not file_path:
        return

    try:
        mirror_auto(file_path)
        path_var.set(file_path)

        print("---------------- Auto mirrored successfully! ---------------------")

    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")

def select_and_mirror_path():
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("Path files", "*.path"), ("All files", "*.*")]
    )
    if not file_path:
        return

    try:
        file_path = Path(file_path)
        dest_path: Path = default_output_path(file_path)
        mirror_path_file(file_path, dest_path)

        print(f"Mirrored '{file_path.name}' → '{dest_path.name}'")
        path_var.set(file_path)
        print("---------------- Path mirrored successfully! ---------------------")

    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")

# --- Redirect print statements to the result box ---
class ConsoleRedirector:
    """Redirects stdout/stderr to a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        # Append message to the Text widget
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Auto-scroll
        self.text_widget.configure(state='disabled')

    def flush(self):
        # Required for file-like object compatibility
        pass


# --- Main window ---
root = tk.Tk()
root.title("PathPlanner Auto-Mirror Tool")
root.geometry("800x600")
root.resizable(False, False)
root.configure(bg="#f4f6f9")

# Title
tk.Label(root, text="PathPlanner Auto-Mirror", font=("Helvetica", 16, "bold"),
         bg="#f4f6f9", fg="#1a1a2e").pack(pady=(24, 4))

# Buttons
tk.Button(root, text="📂  Select Auto File", command=select_and_mirror_auto,
          font=("Helvetica", 11, "bold"), bg="#4f8ef7", fg="white",
          activebackground="#3a6fd8", activeforeground="white",
          relief="flat", padx=16, pady=8, cursor="hand2").pack(pady=18)

tk.Button(root, text="📂  Select Path File", command=select_and_mirror_path,
          font=("Helvetica", 11, "bold"), bg="#4f8ef7", fg="white",
          activebackground="#3a6fd8", activeforeground="white",
          relief="flat", padx=16, pady=8, cursor="hand2").pack(pady=18)

# File path display
path_var = tk.StringVar(value="No file selected")
tk.Label(root, textvariable=path_var, font=("Helvetica", 9), bg="#f4f6f9",
         fg="#888", wraplength=560).pack()

# Text widget for console output
console_text = tk.Text(root, wrap='word', height=20, width=80, state='disabled', bg='black', fg='white')
console_text.pack(padx=10, pady=10, fill='both', expand=True)

# Redirect stdout and stderr
sys.stdout = ConsoleRedirector(console_text)
sys.stderr = ConsoleRedirector(console_text)

root.mainloop()

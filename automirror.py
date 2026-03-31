from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from mirror_auto import mirror_auto
from mirror_path import mirror_path_file, default_output_path



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

        result_var.set("Auto mirrored successfully!")
        result_label.config(fg="#1a1a2e")

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

        result_var.set("Path mirrored successfully!")
        result_label.config(fg="#1a1a2e")

    except Exception as e:
        messagebox.showerror("Error", f"Could not read file:\n{e}")

# --- Main window ---
root = tk.Tk()
root.title("PathPlanner Auto-Mirror Tool")
root.geometry("600x320")
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

# Result box
result_frame = tk.Frame(root, bg="#e8edf5", bd=0, relief="flat")
result_frame.pack(fill="x", padx=40, pady=(12, 0))

tk.Label(result_frame, text="Result:", font=("Helvetica", 9, "bold"),
         bg="#e8edf5", fg="#555").pack(anchor="w", padx=10, pady=(8, 0))

result_var = tk.StringVar(value="—")
result_label = tk.Label(result_frame, textvariable=result_var,
                        font=("Courier", 11), bg="#e8edf5", fg="#aaa",
                        wraplength=520, justify="left")
result_label.pack(anchor="w", padx=10, pady=(2, 10))

root.mainloop()

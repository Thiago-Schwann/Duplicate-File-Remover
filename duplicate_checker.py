import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
from collections import defaultdict

LOG_FILE = "scan_log.txt"


def write_log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def get_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def delete_duplicates():
    folder_path = folder_entry.get()
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Please select a valid folder.")
        return

    result_text.delete(1.0, tk.END)
    with open(LOG_FILE, "w", encoding="utf-8") as log_file:
        log_file.write("Scan started...\n")

    Thread(target=process_duplicates, args=(folder_path,), daemon=True).start()

def process_duplicates(folder_path):
    size_dict = defaultdict(list)

    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)        

            try:
                file_size = os.path.getsize(file_path)
                size_dict[file_size].append(file_path)
            except Exception as e:
                msg = f"Error processing {file_path}: {e}"
                result_text.insert(tk.END, msg + "\n", "error")
                write_log(msg)

    duplicates = []
    for file_size, file_list in size_dict.items():
        if len(file_list) > 1:
            hash_dict = {}
            for file_path in file_list:
                try:
                    file_hash = get_file_hash(file_path)
                    if file_hash in hash_dict:
                        duplicates.append(file_path)
                        msg = f"Duplicate found: {file_path}"
                        result_text.insert(tk.END, msg + "\n\n", "duplicate")
                        write_log(msg)
                    else:
                        hash_dict[file_hash] = file_path
                except Exception as e:
                    msg = f"Error hashing {file_path}: {e}"
                    result_text.insert(tk.END, msg + "\n", "error")
                    write_log(msg)

    if duplicates:
        delete_files(duplicates)
    else:
        msg = "\nNo duplicates found."
        result_text.insert(tk.END, msg + "\n", "info")
        write_log(msg)

def delete_files(duplicates):
    for file_path in duplicates:
        try:
            os.remove(file_path)
            msg = f"Deleted: {file_path}"
            result_text.insert(tk.END, msg + "\n\n", "deleted")
            write_log(msg)
        except Exception as e:
            msg = f"Error deleting {file_path}: {e}"
            result_text.insert(tk.END, msg + "\n\n", "error")
            write_log(msg)
    result_text.insert(tk.END, "\nDeletion completed.\n", "deleted")
    write_log("Deletion completed.")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

root = tk.Tk()
root.title("Duplicate File Checker & PDF Renamer")
root.geometry("700x400")

folder_label = tk.Label(root, text="Select Folder to Scan for Duplicates and Rename PDFs:")
folder_label.pack(pady=10)

folder_entry = tk.Entry(root, width=60)
folder_entry.pack(pady=5)

folder_button = tk.Button(root, text="Browse", command=select_folder)
folder_button.pack(pady=5)

delete_button = tk.Button(root, text="Check and Delete Duplicates", command=delete_duplicates)
delete_button.pack(pady=10)

result_text = tk.Text(root, wrap=tk.WORD, height=15)
result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

result_text.tag_config("error", foreground="red")
result_text.tag_config("duplicate", foreground="orange")
result_text.tag_config("deleted", foreground="green")
result_text.tag_config("info", foreground="blue")

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

root.mainloop()

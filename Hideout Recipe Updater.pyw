import os
import sys
import hashlib
import requests
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

API_URL = "https://api.github.com/repos/Hazeofdream/hideout-recipes/contents"


def sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hideout Recipe Updater")
        self.root.geometry("700x500")

        # Resolve base directory (works for .py and .exe)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Target subfolder
        target_subdir = os.path.join(
            base_dir,
            "SPT",
            "user",
            "mods",
            "HideoutRecipeFramework",
            "recipes"
        )

        # Ensure directory exists
        os.makedirs(target_subdir, exist_ok=True)

        self.target_path = tk.StringVar(value=target_subdir)

        # Top frame
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Target Folder:").pack(anchor="w")

        path_frame = tk.Frame(top_frame)
        path_frame.pack(fill="x")

        tk.Entry(path_frame, textvariable=self.target_path).pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side="right")

        # Run button
        tk.Button(root, text="Run Update", command=self.run_update).pack(pady=5)

        # Output box
        self.output = scrolledtext.ScrolledText(root)
        self.output.pack(fill="both", expand=True, padx=10, pady=5)

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.root.update()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_path.set(folder)

    def run_update(self):
        target_path = self.target_path.get().strip()

        if not os.path.exists(target_path):
            messagebox.showerror("Error", "Target directory not found.")
            return

        self.output.delete(1.0, tk.END)
        self.log(f"Target Path:\n{target_path}\n")

        self.log("Querying GitHub repository...")

        try:
            response = requests.get(API_URL, headers={"User-Agent": "Python"})
            response.raise_for_status()
            files = response.json()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch repository:\n{e}")
            return

        json_files = [f for f in files if f["name"].endswith(".json")]

        temp_dir = tempfile.mkdtemp(prefix="hideout_update_")

        added = []
        updated = []

        for file in json_files:
            name = file["name"]
            download_url = file["download_url"]

            dest = os.path.join(target_path, name)
            temp_file = os.path.join(temp_dir, name)

            self.log(f"Processing: {name}")

            try:
                r = requests.get(download_url)
                with open(temp_file, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                self.log(f"  Failed to download: {e}")
                continue

            if not os.path.exists(dest):
                shutil.move(temp_file, dest)
                added.append(name)
                continue

            local_hash = sha256(dest)
            remote_hash = sha256(temp_file)

            if local_hash != remote_hash:
                shutil.move(temp_file, dest)
                updated.append(name)
            else:
                os.remove(temp_file)

        shutil.rmtree(temp_dir, ignore_errors=True)

        if added:
            self.log("\nAdded:")
            for f in added:
                self.log(f" + {f}")

        if updated:
            self.log("\nUpdated:")
            for f in updated:
                self.log(f" * {f}")

        if not added and not updated:
            self.log("\nNo changes were made.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
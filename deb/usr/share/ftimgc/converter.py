#!/usr/bin/env python3
import os, subprocess, threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File to IMG Converter")
        self.resizable(False, False)
        self.geometry("520x200")
        self.configure(padx=20, pady=20)

        self.src = tk.StringVar(value="No file selected")
        self.dst = tk.StringVar(value="Output: (auto)")
        self._src_path = None
        self._dst_path = None

        # Source row
        src_frame = tk.Frame(self)
        src_frame.pack(fill="x", pady=4)
        tk.Label(src_frame, textvariable=self.src, anchor="w", width=52).pack(side="left")
        tk.Button(src_frame, text="Browse…", command=self.on_browse).pack(side="right")

        # Output row
        dst_frame = tk.Frame(self)
        dst_frame.pack(fill="x", pady=4)
        tk.Label(dst_frame, textvariable=self.dst, anchor="w", width=52).pack(side="left")
        tk.Button(dst_frame, text="Save As…", command=self.on_save_as).pack(side="right")

        # Progress bar
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=480)
        self.progress.pack(pady=10)

        # Status label
        self.status = tk.StringVar(value="Idle")
        tk.Label(self, textvariable=self.status).pack()

        # Convert button
        self.convert_btn = tk.Button(self, text="Convert to .img", command=self.on_convert)
        self.convert_btn.pack(pady=6)

    def on_browse(self):
        path = filedialog.askopenfilename(title="Select a file")
        if path:
            self._src_path = path
            self.src.set(path)
            if self._dst_path is None:
                self._dst_path = os.path.splitext(path)[0] + ".img"
                self.dst.set(f"Output: {self._dst_path}")

    def on_save_as(self):
        init = os.path.basename(os.path.splitext(self._src_path)[0]) + ".img" if self._src_path else "output.img"
        path = filedialog.asksaveasfilename(
            title="Save .img as",
            initialfile=init,
            defaultextension=".img",
            filetypes=[("IMG files", "*.img"), ("All files", "*.*")]
        )
        if path:
            self._dst_path = path if path.endswith(".img") else path + ".img"
            self.dst.set(f"Output: {self._dst_path}")

    def on_convert(self):
        if not self._src_path:
            messagebox.showerror("Error", "Please select a source file first.")
            return
        self.convert_btn.config(state="disabled")
        self.status.set("Converting…")
        self.progress.start(10)
        threading.Thread(target=self._do_convert, daemon=True).start()

    def _do_convert(self):
        try:
            subprocess.run(
                ["dd", f"if={self._src_path}", f"of={self._dst_path}", "bs=4M", "conv=fsync"],
                check=True, stderr=subprocess.PIPE
            )
            self.after(0, self._on_done, True, None)
        except subprocess.CalledProcessError as e:
            self.after(0, self._on_done, False, e.stderr.decode())

    def _on_done(self, success, error):
        self.progress.stop()
        self.convert_btn.config(state="normal")
        if success:
            self.status.set("Done!")
            messagebox.showinfo("Success", f"Saved to:\n{self._dst_path}")
        else:
            self.status.set("Failed")
            messagebox.showerror("Conversion Failed", error)

if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()

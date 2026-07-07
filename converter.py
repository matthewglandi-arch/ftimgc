#!/usr/bin/env python3
import os, shutil, threading
import tkinter as tk
from tkinter import ttk, messagebox

HOME = os.path.expanduser("~")

class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File to IMG Converter")
        self.attributes("-fullscreen", True)
        self.configure(bg="#1e1e2e")

        self._current_dir = tk.StringVar(value=HOME)
        self._selected: set[str] = set()

        self._build_ui()
        self._load_dir(HOME)

        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.bind("<F11>", lambda e: self.attributes("-fullscreen", True))

    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────────────────
        top = tk.Frame(self, bg="#181825", pady=8, padx=12)
        top.pack(fill="x")

        tk.Button(top, text="✕  Exit", command=self.destroy,
                  bg="#f38ba8", fg="white", relief="flat",
                  font=("Sans", 11, "bold"), padx=10).pack(side="right")

        tk.Label(top, text="File → IMG Converter", bg="#181825", fg="white",
                 font=("Sans", 16, "bold")).pack(side="left")

        # ── Path bar ─────────────────────────────────────────────────────────
        path_bar = tk.Frame(self, bg="#313244", pady=6, padx=12)
        path_bar.pack(fill="x")

        tk.Button(path_bar, text="⬆  Up", command=self._go_up,
                  bg="#45475a", fg="white", relief="flat",
                  font=("Sans", 10), padx=8).pack(side="left", padx=(0, 8))

        tk.Label(path_bar, textvariable=self._current_dir,
                 bg="#313244", fg="#cdd6f4",
                 font=("Monospace", 10)).pack(side="left")

        # ── Main area (file list + sidebar) ──────────────────────────────────
        main = tk.Frame(self, bg="#1e1e2e")
        main.pack(fill="both", expand=True)

        # File list
        list_frame = tk.Frame(main, bg="#1e1e2e")
        list_frame.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)

        cols = ("type", "name", "size")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings",
                                  selectmode="extended")
        self.tree.heading("type", text="")
        self.tree.heading("name", text="Name")
        self.tree.heading("size", text="Size")
        self.tree.column("type", width=36, stretch=False, anchor="center")
        self.tree.column("name", width=600)
        self.tree.column("size", width=100, anchor="e")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#181825", foreground="#cdd6f4",
                         fieldbackground="#181825", rowheight=30,
                         font=("Sans", 11))
        style.configure("Treeview.Heading", background="#313244",
                         foreground="#cdd6f4", font=("Sans", 11, "bold"))
        style.map("Treeview", background=[("selected", "#45475a")])

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Sidebar
        side = tk.Frame(main, bg="#181825", width=260)
        side.pack(side="right", fill="y", padx=12, pady=12)
        side.pack_propagate(False)

        tk.Label(side, text="Selected Files", bg="#181825", fg="#cdd6f4",
                 font=("Sans", 12, "bold")).pack(anchor="w", pady=(8, 4), padx=8)

        self.sel_box = tk.Listbox(side, bg="#1e1e2e", fg="#a6e3a1",
                                   selectbackground="#313244",
                                   font=("Monospace", 9), relief="flat",
                                   highlightthickness=0, borderwidth=0)
        self.sel_box.pack(fill="both", expand=True, padx=8)

        tk.Button(side, text="Clear Selection",
                  command=self._clear_selection,
                  bg="#45475a", fg="white", relief="flat",
                  font=("Sans", 10), pady=4).pack(fill="x", padx=8, pady=6)

        # ── Bottom bar ───────────────────────────────────────────────────────
        bottom = tk.Frame(self, bg="#181825", pady=10, padx=12)
        bottom.pack(fill="x", side="bottom")

        self.status = tk.StringVar(value="Select files above, then click Convert.")
        tk.Label(bottom, textvariable=self.status, bg="#181825", fg="#a6adc8",
                 font=("Sans", 10)).pack(side="left")

        self.progress = ttk.Progressbar(bottom, mode="determinate", length=300)
        self.progress.pack(side="left", padx=16)

        self.conv_btn = tk.Button(bottom, text="⚙  Convert to .img",
                                   command=self._on_convert,
                                   bg="#89b4fa", fg="#1e1e2e",
                                   font=("Sans", 12, "bold"),
                                   relief="flat", padx=16, pady=6)
        self.conv_btn.pack(side="right")

    # ── Directory navigation ─────────────────────────────────────────────────

    def _load_dir(self, path):
        self.tree.delete(*self.tree.get_children())
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            messagebox.showerror("Permission Denied", f"Cannot open:\n{path}")
            return
        self._current_dir.set(path)
        for e in entries:
            if e.name.startswith("."):
                continue
            icon = "📁" if e.is_dir() else "📄"
            try:
                size = "" if e.is_dir() else self._fmt_size(e.stat().st_size)
            except OSError:
                size = ""
            self.tree.insert("", "end", iid=e.path,
                             values=(icon, e.name, size))

    def _go_up(self):
        parent = os.path.dirname(self._current_dir.get())
        if parent != self._current_dir.get():
            self._load_dir(parent)

    def _on_double_click(self, _):
        sel = self.tree.focus()
        if sel and os.path.isdir(sel):
            self._load_dir(sel)

    # ── Selection ────────────────────────────────────────────────────────────

    def _on_select(self, _):
        for iid in self.tree.selection():
            if os.path.isfile(iid):
                self._selected.add(iid)
        self._refresh_sidebar()

    def _clear_selection(self):
        self._selected.clear()
        self.tree.selection_remove(*self.tree.selection())
        self._refresh_sidebar()

    def _refresh_sidebar(self):
        self.sel_box.delete(0, "end")
        for p in self._selected:
            self.sel_box.insert("end", os.path.basename(p))
        self.status.set(f"{len(self._selected)} file(s) selected.")

    # ── Conversion ───────────────────────────────────────────────────────────

    def _on_convert(self):
        if not self._selected:
            messagebox.showwarning("No files", "Select at least one file first.")
            return
        self.conv_btn.config(state="disabled")
        self.progress["value"] = 0
        self.progress["maximum"] = len(self._selected)
        threading.Thread(target=self._do_convert, daemon=True).start()

    def _do_convert(self):
        files = list(self._selected)
        errors = []
        for i, src in enumerate(files, 1):
            dst = os.path.splitext(src)[0] + ".img"
            self.after(0, self.status.set, f"Converting {os.path.basename(src)}…")
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                errors.append(f"{os.path.basename(src)}: {e}")
            self.after(0, self._set_progress, i)

        self.after(0, self._on_done, errors)

    def _set_progress(self, val):
        self.progress["value"] = val

    def _on_done(self, errors):
        self.conv_btn.config(state="normal")
        if errors:
            messagebox.showerror("Some conversions failed", "\n".join(errors))
            self.status.set("Done with errors.")
        else:
            self.status.set(f"✓ {len(self._selected)} file(s) converted successfully.")
            messagebox.showinfo("Done", f"{len(self._selected)} file(s) converted to .img")
        self._clear_selection()
        self._load_dir(self._current_dir.get())

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_size(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"

if __name__ == "__main__":
    app = ConverterApp()
    app.mainloop()

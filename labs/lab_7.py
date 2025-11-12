import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

COLUMNS = ("id", "name", "category", "quantity", "price", "location", "created_at")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Облік товарів")
        self.data = []
        self.current_file = None
        self.sort_state = {c: False for c in COLUMNS}

        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Відкрити…", command=self.open_csv)
        filemenu.add_command(label="Зберегти", command=self.save_csv)
        filemenu.add_command(label="Зберегти як…", command=self.save_csv_as)
        menubar.add_cascade(label="Файл", menu=filemenu)
        self.root.config(menu=menubar)

        top = ttk.Frame(self.root)
        top.pack(fill="both", expand=True, padx=6, pady=6)

        left = ttk.Frame(top)
        left.pack(side="left", fill="both", expand=True)

        search_bar = ttk.Frame(left)
        search_bar.pack(fill="x", pady=(0,6))
        ttk.Label(search_bar, text="Пошук:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_bar, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_tree())

        self.tree = ttk.Treeview(left, columns=COLUMNS, show="headings", height=14)
        for col in COLUMNS:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=110 if col!="name" else 160, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right = ttk.Frame(top)
        right.pack(side="left", fill="y", padx=(6,0))

        self.entries = {}
        for i, field in enumerate(["id", "name", "category", "quantity", "price", "location"]):
            ttk.Label(right, text=field).grid(row=i, column=0, sticky="w", pady=2)
            e = tk.Entry(right)
            e.grid(row=i, column=1, pady=2, padx=6)
            self.entries[field] = e

        btns = ttk.Frame(right)
        btns.grid(row=6, column=0, columnspan=2, pady=8, sticky="ew")
        ttk.Button(btns, text="Додати", command=self.add_item).pack(side="left", expand=True, fill="x")
        ttk.Button(btns, text="Оновити", command=self.update_item).pack(side="left", expand=True, fill="x", padx=6)
        ttk.Button(btns, text="Видалити", command=self.delete_item).pack(side="left", expand=True, fill="x")
        ttk.Button(btns, text="Очистити форму", command=self.clear_form).pack(side="left", expand=True, fill="x", padx=6)

        self.status = tk.StringVar(value="Готово")
        ttk.Label(self.root, textvariable=self.status, anchor="w", relief="sunken").pack(fill="x")

    def set_status(self, msg):
        self.status.set(msg)

    def clear_highlights(self):
        for e in self.entries.values():
            e.configure(bg="white")

    def generate_id(self):
        ids = [int(str(x["id"])) for x in self.data if str(x["id"]).isdigit()]
        return str(max(ids) + 1 if ids else 1)

    def validate(self, for_update=False, selected_id=None):
        self.clear_highlights()
        ok = True
        v = {k: self.entries[k].get().strip() for k in self.entries}

        if not v["id"]:
            v["id"] = self.generate_id()
        if not v["name"]:
            self.entries["name"].configure(bg="#ffdddd"); ok = False
        if not v["category"]:
            self.entries["category"].configure(bg="#ffdddd"); ok = False

        try:
            v["quantity"] = int(v["quantity"])
            if v["quantity"] < 0: raise ValueError
        except:
            self.entries["quantity"].configure(bg="#ffdddd"); ok = False

        try:
            v["price"] = float(v["price"].replace(",", "."))
            if v["price"] < 0: raise ValueError
        except:
            self.entries["price"].configure(bg="#ffdddd"); ok = False

        if not v["location"]:
            self.entries["location"].configure(bg="#ffdddd"); ok = False

        for x in self.data:
            if str(x["id"]) == v["id"]:
                if for_update and selected_id == v["id"]:
                    continue
                self.entries["id"].configure(bg="#ffdddd"); ok = False

        if not ok:
            self.set_status("Перевірте виділені поля")
            return None
        return v

    def add_item(self):
        v = self.validate()
        if not v:
            return
        v["created_at"] = datetime.now().isoformat(timespec="seconds")
        self.data.append(v)
        self.refresh_tree()
        self.set_status("Додано")

    def on_select(self, _):
        sel = self.get_selected()
        if not sel:
            return
        for k in self.entries:
            self.entries[k].delete(0, tk.END)
            self.entries[k].insert(0, sel[k])

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        rid = self.tree.item(sel[0], "values")[0]
        for x in self.data:
            if str(x["id"]) == str(rid):
                return x
        return None

    def update_item(self):
        sel = self.get_selected()
        if not sel:
            self.set_status("Виберіть запис")
            return
        v = self.validate(for_update=True, selected_id=str(sel["id"]))
        if not v:
            return
        sel.update(v)
        self.refresh_tree()
        self.set_status("Оновлено")

    def delete_item(self):
        sel = self.get_selected()
        if not sel:
            self.set_status("Виберіть запис")
            return
        if not messagebox.askyesno("Підтвердження", "Видалити вибраний запис?"):
            return
        self.data = [x for x in self.data if str(x["id"]) != str(sel["id"])]
        self.refresh_tree()
        self.clear_form()
        self.set_status("Видалено")

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.clear_highlights()
        self.set_status("Форма очищена")

    def refresh_tree(self):
        q = self.search_var.get().strip().lower()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for x in self.data:
            if q and q not in x["name"].lower() and q not in x["category"].lower():
                continue
            self.tree.insert("", "end", values=[x[c] for c in COLUMNS])

    def sort_by_column(self, col):
        self.sort_state[col] = not self.sort_state[col]
        reverse = self.sort_state[col]
        try:
            self.data.sort(key=lambda x: float(x[col]), reverse=reverse)
        except:
            self.data.sort(key=lambda x: str(x[col]).lower(), reverse=reverse)
        self.refresh_tree()

    def open_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                if tuple(r.fieldnames or []) != COLUMNS:
                    raise ValueError("Невірні заголовки CSV")
                rows = []
                for row in r:
                    row["quantity"] = int(row["quantity"])
                    row["price"] = float(row["price"])
                    rows.append(row)
            self.data = rows
            self.current_file = path
            self.refresh_tree()
            self.set_status(f"Завантажено {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Помилка відкриття", str(e))
            self.set_status("Помилка відкриття")

    def save_csv(self):
        if not self.current_file:
            return self.save_csv_as()
        self.write_csv(self.current_file)

    def save_csv_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        self.current_file = path
        self.write_csv(path)

    def write_csv(self, path):
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=COLUMNS)
                w.writeheader()
                w.writerows(self.data)
            self.set_status(f"Збережено {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Помилка збереження", str(e))
            self.set_status("Помилка збереження")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
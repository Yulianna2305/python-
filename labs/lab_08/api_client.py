import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import requests

SERVER_URL = "http://127.0.0.1:8000"
CACHE_FILE = "cache.csv"
FIELDS = ["id", "name", "category", "quantity", "price", "location", "created_at"]


class ApiClient:
    def __init__(self):
        self.mode = "online"

    def ensure_cache(self):
        if not os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS)
                writer.writeheader()

    def load_cache(self):
        self.ensure_cache()
        with open(CACHE_FILE, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def save_cache(self, items):
        self.ensure_cache()
        with open(CACHE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(items)

    def get_items(self):
        try:
            r = requests.get(f"{SERVER_URL}/items", timeout=2)
            r.raise_for_status()
            data = r.json()
            self.save_cache(data)
            self.mode = "online"
            return data, None
        except Exception as e:
            self.mode = "offline"
            return self.load_cache(), f"Offline режим: {e}"

    def create_item(self, item):
        if self.mode == "online":
            try:
                r = requests.post(f"{SERVER_URL}/items", json=item, timeout=2)
                r.raise_for_status()
                return r.json(), None
            except Exception:
                self.mode = "offline"
        return self.create_offline(item)

    def create_offline(self, item):
        items = self.load_cache()
        new_id = str(max([int(i["id"]) for i in items], default=0) + 1)
        item["id"] = new_id
        item["created_at"] = datetime.now().isoformat(timespec="seconds")
        items.append(item)
        self.save_cache(items)
        return item, None

    def delete_item(self, item_id):
        if self.mode == "online":
            try:
                r = requests.delete(f"{SERVER_URL}/items/{item_id}", timeout=2)
                r.raise_for_status()
                return None
            except:
                self.mode = "offline"
        items = self.load_cache()
        items = [i for i in items if i["id"] != item_id]
        self.save_cache(items)
        return None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Client (Tkinter + Flask)")
        self.geometry("850x500")

        self.api = ApiClient()

        self.build_ui()
        self.reload_items()

    def build_ui(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)

        cols = FIELDS
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        sb.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        form = ttk.Frame(self)
        form.pack(side="right", fill="y", padx=10)

        self.inputs = {}
        for i, field in enumerate(["name", "category", "quantity", "price", "location"]):
            ttk.Label(form, text=field).grid(row=i, column=0, pady=3)
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var).grid(row=i, column=1)
            self.inputs[field] = var

        ttk.Button(form, text="Додати", command=self.add_item).grid(row=6, column=0, pady=10)
        ttk.Button(form, text="Видалити", command=self.del_item).grid(row=6, column=1)

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).pack(side="bottom", fill="x")

    def set_status(self, txt):
        self.status.set(txt)

    def reload_items(self):
        items, err = self.api.get_items()
        self.tree.delete(*self.tree.get_children())
        for i in items:
            self.tree.insert("", tk.END, values=[i[k] for k in FIELDS])
        if err:
            self.set_status(err)
        else:
            self.set_status("Сервер онлайн")

    def add_item(self):
        try:
            item = {
                "name": self.inputs["name"].get(),
                "category": self.inputs["category"].get(),
                "quantity": int(self.inputs["quantity"].get()),
                "price": float(self.inputs["price"].get()),
                "location": self.inputs["location"].get(),
            }
        except:
            messagebox.showerror("Помилка", "Невірні дані")
            return

        _, err = self.api.create_item(item)
        if err:
            messagebox.showerror("Помилка", err)
        self.reload_items()

    def del_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = self.tree.item(sel[0], "values")[0]
        self.api.delete_item(item_id)
        self.reload_items()


if __name__ == "__main__":
    App().mainloop()

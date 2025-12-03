import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import requests

SERVER_URL = "http://127.0.0.1:8000"
CACHE_FILE = "cache.csv"
CACHE_FIELDS = ["id", "name", "category", "quantity", "price", "location", "created_at"]


class ApiClient:
    def __init__(self):
        self.mode = "online"  

    def _ensure_cache(self):
        if not os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CACHE_FIELDS)
                writer.writeheader()

    def _load_cache(self):
        self._ensure_cache()
        items = []
        with open(CACHE_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append(row)
        return items

    def _save_cache(self, items):
        self._ensure_cache()
        with open(CACHE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CACHE_FIELDS)
            writer.writeheader()
            for item in items:
                writer.writerow(item)

    def get_items(self):
        """Спроба взяти дані з сервера, якщо не виходить - з кешу."""
        try:
            resp = requests.get(f"{SERVER_URL}/items", timeout=2)
            resp.raise_for_status()
            items = resp.json()
            self.mode = "online"
            self._save_cache(items)
            return items, None
        except Exception as e:
            self.mode = "offline"
            items = self._load_cache()
            return items, f"Offline режим: {e}"

    def create_item(self, data):
        if self.mode == "online":
            try:
                resp = requests.post(f"{SERVER_URL}/items", json=data, timeout=2)
                if resp.status_code == 400:
                    return None, resp.json().get("error", "Validation error")
                resp.raise_for_status()
                item = resp.json()
                items, _ = self.get_items()
                return item, None
            except Exception:
                self.mode = "offline"
        return self._create_item_offline(data)

    def _create_item_offline(self, data):
        items = self._load_cache()
        max_id = 0
        for it in items:
            try:
                i = int(it["id"])
                if i > max_id:
                    max_id = i
            except Exception:
                continue
        new_id = str(max_id + 1)

        item = {
            "id": new_id,
            "name": data["name"],
            "category": data["category"],
            "quantity": str(int(data["quantity"])),
            "price": str(float(data["price"])),
            "location": data["location"],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        items.append(item)
        self._save_cache(items)
        return item, None

    def update_item(self, item_id, data):
        if self.mode == "online":
            try:
                resp = requests.put(f"{SERVER_URL}/items/{item_id}", json=data, timeout=2)
                if resp.status_code in (400, 404):
                    return None, resp.json().get("error", "Error")
                resp.raise_for_status()
                item = resp.json()
                items, _ = self.get_items()
                return item, None
            except Exception:
                self.mode = "offline"
        return self._update_item_offline(item_id, data)

    def _update_item_offline(self, item_id, data):
        items = self._load_cache()
        updated = None
        for item in items:
            if item["id"] == item_id:
                if "name" in data:
                    item["name"] = data["name"]
                if "category" in data:
                    item["category"] = data["category"]
                if "quantity" in data:
                    item["quantity"] = str(int(data["quantity"]))
                if "price" in data:
                    item["price"] = str(float(data["price"]))
                if "location" in data:
                    item["location"] = data["location"]
                updated = item
                break
        if updated is None:
            return None, "Item not found in cache"
        self._save_cache(items)
        return updated, None

    def delete_item(self, item_id):
        if self.mode == "online":
            try:
                resp = requests.delete(f"{SERVER_URL}/items/{item_id}", timeout=2)
                if resp.status_code == 404:
                    return "Item not found on server"
                resp.raise_for_status()
                items, _ = self.get_items()
                return None
            except Exception:
                self.mode = "offline"
        return self._delete_item_offline(item_id)

    def _delete_item_offline(self, item_id):
        items = self._load_cache()
        new_items = [i for i in items if i["id"] != item_id]
        if len(new_items) == len(items):
            return "Item not found in cache"
        self._save_cache(new_items)
        return None

    def sync_with_server(self):
        try:
            resp = requests.get(f"{SERVER_URL}/items", timeout=3)
            resp.raise_for_status()
            server_items = resp.json()
        except Exception as e:
            self.mode = "offline"
            return f"Сервер недоступний: {e}"

        self.mode = "online"

        cache_items = self._load_cache()

        for it in server_items:
            try:
                requests.delete(f"{SERVER_URL}/items/{it['id']}", timeout=2)
            except Exception:
                pass

        for it in cache_items:
            payload = {
                "name": it["name"],
                "category": it["category"],
                "quantity": it["quantity"],
                "price": it["price"],
                "location": it["location"],
            }
            try:
                r = requests.post(f"{SERVER_URL}/items", json=payload, timeout=2)
                r.raise_for_status()
            except Exception as e:
                return f"Помилка при синхронізації: {e}"

        items, err = self.get_items()
        if err:
            return f"Синхронізація частково вдала, але: {err}"

        return "Синхронізація завершена"

    def export_csv_from_server(self, path):
        try:
            resp = requests.get(f"{SERVER_URL}/export", timeout=5)
            resp.raise_for_status()
        except Exception as e:
            return f"Не вдалося отримати CSV з сервера: {e}"

        with open(path, "wb") as f:
            f.write(resp.content)
        return None


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory client (Tkinter + Flask)")
        self.geometry("900x500")

        self.api = ApiClient()

        self._create_menu()
        self._create_widgets()
        self._load_items_initial()

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        menu_file = tk.Menu(menubar, tearoff=0)
        menu_file.add_command(label="Синхронізувати зараз", command=self.on_sync)
        menu_file.add_command(label="Експорт CSV", command=self.on_export_csv)

        menubar.add_cascade(label="Файл", menu=menu_file)

    def _create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("id", "name", "category", "quantity", "price", "location", "created_at"),
            show="headings",
        )
        for col in ("id", "name", "category", "quantity", "price", "location", "created_at"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        self.entry_vars = {}
        fields = ["name", "category", "quantity", "price", "location"]
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field + ":").grid(row=i, column=0, sticky="e", pady=2)
            var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=var, width=25).grid(row=i, column=1, pady=2)
            self.entry_vars[field] = var

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Додати", command=self.on_add).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Оновити", command=self.on_update).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Видалити", command=self.on_delete).grid(row=0, column=2, padx=2)
        ttk.Button(btn_frame, text="Оновити список", command=self.on_reload).grid(row=0, column=3, padx=2)

        self.status_var = tk.StringVar()
        ttk.Label(self, textvariable=self.status_var, anchor="w", relief=tk.SUNKEN)\
            .pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, msg):
        self.status_var.set(msg)
        print(msg)

    def _load_items_initial(self):
        items, err = self.api.get_items()
        if err:
            self.set_status(err)
        else:
            self.set_status("Дані завантажено з сервера")
        self._fill_tree(items)

    def _fill_tree(self, items):
        self.tree.delete(*self.tree.get_children())
        for it in items:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    it.get("id", ""),
                    it.get("name", ""),
                    it.get("category", ""),
                    it.get("quantity", ""),
                    it.get("price", ""),
                    it.get("location", ""),
                    it.get("created_at", ""),
                ),
            )

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        _, name, category, quantity, price, location, _ = values
        self.entry_vars["name"].set(name)
        self.entry_vars["category"].set(category)
        self.entry_vars["quantity"].set(quantity)
        self.entry_vars["price"].set(price)
        self.entry_vars["location"].set(location)

    def _get_form_data(self):
        try:
            quantity = int(self.entry_vars["quantity"].get())
        except ValueError:
            raise ValueError("Quantity має бути цілим числом")

        try:
            price = float(self.entry_vars["price"].get())
        except ValueError:
            raise ValueError("Price має бути числом")

        if quantity < 0:
            raise ValueError("Quantity не може бути від'ємним")

        data = {
            "name": self.entry_vars["name"].get().strip(),
            "category": self.entry_vars["category"].get().strip(),
            "quantity": quantity,
            "price": price,
            "location": self.entry_vars["location"].get().strip(),
        }
        if not data["name"]:
            raise ValueError("Name не може бути порожнім")
        return data

    def get_selected_item_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")[0]

    def on_add(self):
        try:
            data = self._get_form_data()
        except ValueError as e:
            messagebox.showerror("Помилка валідації", str(e))
            self.set_status(str(e))
            return

        _, err = self.api.create_item(data)
        if err:
            messagebox.showerror("Помилка", err)
            self.set_status(err)
        items, err2 = self.api.get_items()
        self._fill_tree(items)
        self.set_status("Товар додано" + (f" / {err2}" if err2 else ""))

    def on_update(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            messagebox.showwarning("Увага", "Оберіть товар для оновлення")
            return
        try:
            data = self._get_form_data()
        except ValueError as e:
            messagebox.showerror("Помилка валідації", str(e))
            self.set_status(str(e))
            return

        _, err = self.api.update_item(item_id, data)
        if err:
            messagebox.showerror("Помилка", err)
            self.set_status(err)
        items, err2 = self.api.get_items()
        self._fill_tree(items)
        self.set_status("Товар оновлено" + (f" / {err2}" if err2 else ""))

    def on_delete(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            messagebox.showwarning("Увага", "Оберіть товар для видалення")
            return
        if not messagebox.askyesno("Підтвердження", "Видалити обраний товар?"):
            return

        err = self.api.delete_item(item_id)
        if err:
            messagebox.showerror("Помилка", err)
            self.set_status(err)
        items, err2 = self.api.get_items()
        self._fill_tree(items)
        self.set_status("Товар видалено" + (f" / {err2}" if err2 else ""))

    def on_reload(self):
        items, err = self.api.get_items()
        self._fill_tree(items)
        self.set_status(err or "Список оновлено")

    def on_sync(self):
        msg = self.api.sync_with_server()
        if msg:
            if "завершена" in msg:
                messagebox.showinfo("Синхронізація", msg)
            else:
                messagebox.showerror("Синхронізація", msg)

        items, err = self.api.get_items()
        self._fill_tree(items)
        self.set_status(err or (msg or "Синхронізація завершена"))

    def on_export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Зберегти CSV як...",
        )
        if not path:
            return
        err = self.api.export_csv_from_server(path)
        if err:
            messagebox.showerror("Експорт CSV", err)
            self.set_status(err)
        else:
            msg = f"CSV збережено в {path}"
            messagebox.showinfo("Експорт CSV", msg)
            self.set_status(msg)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()

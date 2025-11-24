import os
import csv
from datetime import datetime
import requests

COLUMNS = ("id", "name", "category", "quantity", "price", "location", "created_at")


class InventoryClient:
    def __init__(self, base_url="http://127.0.0.1:5000", cache_path="cache.csv"):
        self.url = base_url
        self.cache_path = cache_path


    def _load_cache(self):
        if not os.path.exists(self.cache_path):
            return []
        with open(self.cache_path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            items = []
            for row in r:
                row["quantity"] = int(row["quantity"])
                row["price"] = float(row["price"])
                items.append(row)
        return items

    def _save_cache(self, items):
        with open(self.cache_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(items)

    def fetch_items(self):
        try:
            r = requests.get(self.url + "/items", timeout=2)
            r.raise_for_status()
            items = r.json()
            self._save_cache(items)
            return items, True
        except:
            return self._load_cache(), False

    def add_item(self, data):
        payload = {
            "name": data["name"],
            "category": data["category"],
            "quantity": data["quantity"],
            "price": data["price"],
            "location": data["location"]
        }
        try:
            r = requests.post(self.url + "/items", json=payload, timeout=2)
            r.raise_for_status()
            items, _ = self.fetch_items()
            return items, True, "Додано на сервері"
        except:
            items = self._load_cache()

            new_id = max([int(x["id"]) for x in items] or [0]) + 1
            item = {
                "id": str(new_id),
                "name": payload["name"],
                "category": payload["category"],
                "quantity": int(payload["quantity"]),
                "price": float(payload["price"]),
                "location": payload["location"],
                "created_at": datetime.now().isoformat(timespec="seconds")
            }
            items.append(item)
            self._save_cache(items)
            return items, False, "Додано офлайн"

    def update_item(self, item_id, data):
        payload = {
            "name": data["name"],
            "category": data["category"],
            "quantity": data["quantity"],
            "price": data["price"],
            "location": data["location"]
        }
        try:
            r = requests.put(f"{self.url}/items/{item_id}", json=payload, timeout=2)
            r.raise_for_status()
            items, _ = self.fetch_items()
            return items, True, "Оновлено на сервері"
        except:
            items = self._load_cache()
            for it in items:
                if it["id"] == str(item_id):
                    it.update(payload)
            self._save_cache(items)
            return items, False, "Оновлено офлайн"

    def delete_item(self, item_id):
        try:
            r = requests.delete(f"{self.url}/items/{item_id}", timeout=2)
            if r.status_code not in (200, 204):
                raise Exception()
            items, _ = self.fetch_items()
            return items, True, "Видалено на сервері"
        except:
            items = [x for x in self._load_cache() if x["id"] != str(item_id)]
            self._save_cache(items)
            return items, False, "Видалено офлайн"

    def sync_now(self):
        items = self._load_cache()
        try:
            server_items = requests.get(self.url + "/items", timeout=2).json()
            for it in server_items:
                requests.delete(f"{self.url}/items/{it['id']}", timeout=2)
            for it in items:
                requests.post(self.url + "/items", json={
                    "name": it["name"],
                    "category": it["category"],
                    "quantity": it["quantity"],
                    "price": it["price"],
                    "location": it["location"]
                }, timeout=2)
            fresh_items, _ = self.fetch_items()
            return fresh_items, True, "Синхронізовано"
        except:
            return items, False, "Сервер недоступний"

    def export_csv(self, path):
        r = requests.get(self.url + "/export", timeout=2)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
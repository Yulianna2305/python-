from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import csv


@dataclass(order=True)
class Item:
    sort_index: tuple = field(init=False, repr=False)

    name: str
    category: str
    quantity: int
    value: float
    condition: str
    location: str
    added_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self):
        self.sort_index = (self.category, self.value)

    def total_value(self) -> float:
        return self.quantity * self.value

    def __str__(self):
        return f"[{self.category}] {self.name} ({self.quantity} шт.) — {self.value} грн/шт, стан: {self.condition}"


@dataclass
class Inventory:
    items: List[Item] = field(default_factory=list)

    def add_item(self, item: Item):
        self.items.append(item)

    def remove_item(self, name: str):
        self.items = [i for i in self.items if i.name.lower() != name.lower()]

    def find_by_category(self, category: str) -> List[Item]:
        return [i for i in self.items if i.category.lower() == category.lower()]

    def filter_items(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        condition: Optional[str] = None,
        location: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[Item]:

        result = self.items

        if name:
            result = [i for i in result if name.lower() in i.name.lower()]

        if category:
            result = [i for i in result if i.category.lower() == category.lower()]

        if condition:
            result = [i for i in result if i.condition.lower() == condition.lower()]

        if location:
            result = [i for i in result if i.location.lower() == location.lower()]

        if min_value is not None:
            result = [i for i in result if i.value >= min_value]

        if max_value is not None:
            result = [i for i in result if i.value <= max_value]

        return result

    def sort_items(self):
        self.items.sort()

    def total_inventory_value(self) -> float:
        return sum(item.total_value() for item in self.items)

    def save_to_csv(self, filename: str):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "category", "quantity", "value", "condition", "location", "added_at"])
            for item in self.items:
                writer.writerow([
                    item.name, item.category, item.quantity, item.value,
                    item.condition, item.location, item.added_at
                ])

    def load_from_csv(self, filename: str):
        self.items.clear()
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = Item(
                    name=row["name"],
                    category=row["category"],
                    quantity=int(row["quantity"]),
                    value=float(row["value"]),
                    condition=row["condition"],
                    location=row["location"],
                    added_at=row["added_at"]
                )
                self.items.append(item)

    def export_summary(self):
        summary = {}
        for item in self.items:
            summary[item.category] = summary.get(item.category, 0) + item.quantity

        return "\n".join(f"{cat}: {qty} шт." for cat, qty in summary.items())
    

if __name__ == "__main__":
    inv = Inventory()

    # додаємо кілька тестових предметів
    inv.add_item(Item("Гаечний ключ", "інструменти", 3, 15.0, "вживаний", "гараж"))
    inv.add_item(Item("Ноутбук", "електроніка", 1, 18000, "вживаний", "кімната"))
    inv.add_item(Item("Сокира", "інструменти", 2, 120.0, "новий", "комора"))

    print("ВСІ ПРЕДМЕТИ:")
    for item in inv.items:
        print(item)

    print("\nЗагальна вартість:", inv.total_inventory_value(), "грн")

    # сортування
    inv.sort_items()
    print("\nПісля сортування:")
    for item in inv.items:
        print(item)

    # запис у CSV
    inv.save_to_csv("inventory.csv")
    print("\nФайл inventory.csv створено!")

    # звіт по категоріях
    print("\nЗвіт:")
    print(inv.export_summary())


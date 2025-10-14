class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):                    
        return f"{self.name}: {self.quantity}, {self.value}"


class JunkStorage:
    @staticmethod     
    def serialize(items: list, filename: str):    
        with open(filename, 'w', encoding='utf-8') as f:
            for item in items:               
                value_str = str(item.value).replace(".", ",")
                line = f"{item.name}|{item.quantity}|{value_str}\n"
                f.write(line)

    @staticmethod
    def parse(filename: str) -> list:   
        items = []
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) != 3:
                    continue
                name, quantity_str, value_str = parts
                try:
                    quantity = int(quantity_str)
                    value = float(value_str.replace(",", "."))   
                    items.append(JunkItem(name, quantity, value))
                except ValueError:
                    continue
        return items


if __name__ == "__main__":
    items = [
        JunkItem("Бляшанка", 5, 2.5),
        JunkItem("Стара плата", 3, 7.8),
        JunkItem("Купка дротів", 10, 1.2)
    ]

    JunkStorage.serialize(items, "junk.csv")

    restored_items = JunkStorage.parse("junk.csv")

    for obj in restored_items:
        print(obj)






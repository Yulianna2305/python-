from abc import ABC, abstractmethod

class Medicine(ABC):
    def __init__(self, name: str, quantity: int, price: float):
        if not isinstance(name, str):
            raise TypeError("name має бути типу str")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("quantity має бути додатним int")
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("price має бути додатним числом")

        self.name = name
        self.quantity = quantity
        self.price = price

    @abstractmethod
    def requires_prescription(self) -> bool:
        pass

    @abstractmethod
    def storage_requirements(self) -> str:
        pass

    def total_price(self) -> float:
        return self.quantity * self.price

    @abstractmethod
    def info(self) -> str:
        pass

class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "8–15°C, темне місце"

    def info(self) -> str:
        return (f"aнтибіотик {self.name}, кількість {self.quantity}, "
                f"ціна за одиницю {self.price } грн, "
                f"загальна ціна {self.total_price()} грн.")

class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False

    def storage_requirements(self) -> str:
        return "15–25°C, сухо"

    def info(self) -> str:
        return (f"Вітамін {self.name}, кількість {self.quantity}, "
                f"ціна за одиницю {self.price} грн, "
                f"загальна ціна {self.total_price()} грн.")

class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "2–8°C, холодильник"

    def total_price(self) -> float:
        base_price = super().total_price()
        return base_price * 1.1

    def info(self) -> str:
        return (f"Вакцина {self.name}, кількість {self.quantity}, "
                f"ціна за одиницю {self.price} грн, "
                f"загальна ціна {self.total_price()} грн.")
    




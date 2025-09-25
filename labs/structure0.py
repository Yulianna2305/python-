from abc import ABC, abstractmethod

class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance: int) -> float:
        pass

    @abstractmethod
    def fuel_consumption(self, distance: int) -> float:
        pass

    @abstractmethod
    def info(self) -> str:
        pass

    def calculate_cost(self, distance: int, price_per_unit: float) -> float:
        return self.fuel_consumption(distance) * price_per_unit

class Car(Transport):
    def __init__(self, name: str, speed: int, capacity: int):
        super().__init__(name, speed, capacity)

    def move(self, distance: int) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: int) -> float:
        return distance * 0.07

    def info(self) -> str:
        return f"Автомобіль {self.name}, швидкість {self.speed} км/год, місткість {self.capacity}"

class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int):
        super().__init__(name, speed, capacity)
        self.passengers = passengers

    def move(self, distance: int) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: int) -> float:
        if self.passengers > self.capacity:
            print("Перевантажено!")
            return 0
        return distance * 0.15

    def info(self) -> str:
        return f"Автобус {self.name}, швидкість {self.speed} км/год, пасажирів {self.passengers}/{self.capacity}"

class Bicycle(Transport):
    def __init__(self, name: str, capacity: int = 1):
        super().__init__(name, speed=20, capacity=capacity)

    def move(self, distance: int) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance: int) -> float:
        return 0

    def info(self) -> str:
        return f"Велосипед {self.name}, швидкість {self.speed} км/год"

class ElectricCar(Car):
    def __init__(self, name: str, speed: int, capacity: int):
        super().__init__(name, speed, capacity)

    def battery_usage(self, distance: int) -> float:
        return distance * 0.2

    def fuel_consumption(self, distance: int) -> float:
        return 0

    def calculate_cost(self, distance: int, price_per_unit: float) -> float:
        return self.battery_usage(distance) * price_per_unit

    def info(self) -> str:
        return f"Електромобіль {self.name}, швидкість {self.speed} км/год, місткість {self.capacity}"

if __name__ == "__main__":
    transports = [
        Car("BMW", 100, 5),
        Bus("Mercedes", 80, 30, passengers=20),
        Bicycle("Trek"),
        ElectricCar("Tesla", 120, 5)
    ]

    distance = 100
    price = 2.0  

    for t in transports:
        print(t.info())
        print(f"Час у дорозі на {distance} км: {t.move(distance):.2f} год")
        print(f"Витрати пального/заряду: {t.fuel_consumption(distance):.2f}")
        print(f"Вартість: {t.calculate_cost(distance, price):.2f} грн\n")
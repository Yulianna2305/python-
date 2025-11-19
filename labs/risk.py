import threading
import time
import random

PRICE_PER_UNIT = 10

class Warehouse:
    def __init__(self, name, meds):
        self.name = name
        self.meds = meds
        self.lock = threading.Lock()

    def steal(self, amount):
        if self.meds <= 0:
            return 0
        
        outcome = random.random()
        if outcome < 0.2:
            return 0
        elif outcome < 0.6:
            to_steal = amount
        else:
            to_steal = random.randint(1, amount)
        
        stolen = min(to_steal, self.meds)
        self.meds -= stolen
        return stolen
    
class Runner(threading.Thread):
    def __init__(self, name, warehouse):
        super().__init__(name=name)
        self.warehouse = warehouse
        self.total_profit = 0

    def run(self):
        attempts = 10
        for i in range(1, attempts + 1):
            amount = random.randint(10, 30)
            with self.warehouse.lock:
                stolen = self.warehouse.steal(amount)

            self.total_profit += stolen * PRICE_PER_UNIT

            progress = i / attempts
            bar_len = 10
            filled = int(progress * bar_len)
            bar = "[" + "#" * filled + "-" * (bar_len - filled) + "]"
           
            print(
                f"{self.name} @ {self.warehouse.name} {bar}"
                f"{i} / {attempts}, stolen: {stolen} "
            )
            time.sleep(random.uniform(0.1, 0.5))

def run_simulation(number):
    print(f"\n === simulation #{number} === ")

    warehouses = []
    for i in range(1, 4):
        meds = random.randint(100, 300)
        warehouses.append(Warehouse(f"Warehouse-{i}", meds))

    runners = []
    for i in range(1, 6):  
        w = random.choice(warehouses)
        r = Runner(f"Runner-{i}", w)
        runners.append(r)

    for r in runners:
        r.start()

    for r in runners:
        r.join()

    total_profit = sum(r.total_profit for r in runners)

    print("\nRemaining meds:")
    for w in warehouses:
        print(f"{w.name}: {w.meds}")

    print(f"Total profit: {total_profit}")


if __name__ == "__main__":
    for i in range(1, 4):  
        run_simulation(i)
 
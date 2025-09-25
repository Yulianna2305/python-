from models import Antibiotic, Vitamin, Vaccine

def show_medicines(medicines):
    for med in medicines:
        print(med.info())
        print(f"Потребує рецепт: {'Так' if med.requires_prescription() else 'Ні'}")
        print(f"Умови зберігання: {med.storage_requirements()}")
        print("-" * 50)

if __name__ == "__main__":
    medicines = [
        Antibiotic("Амоксицилін", 10, 25.0),
        Vitamin("Вітамін C", 30, 5.0),
        Vaccine("COVID-19 Vaccine", 5, 110.0)
    ]

    show_medicines(medicines)
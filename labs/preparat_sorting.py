medicines = [
    {"name": "Amoxicillin", "quantity": 100, "category": "antibiotic", "temperature": 8.0},
    {"name": "Vitamin C", "quantity": 100, "category": "vitamin", "temperature": 22.5},
    {"name": "COVID-19 Vaccine", "quantity": 100, "category": "vaccine", "temperature": -2.0},
    {"name": "UnknownDrug", "quantity": "ten", "category": "other", "temperature": 15.0},
]

for med in medicines:  #значення зі словника зберігаємо в змінні
    name = med.get("name")
    quantity = med.get("quantity")
    category = med.get("category")
    temperature = med.get("temperature")

    if type(quantity) is not int or type(temperature) not in (int, float):
        print(f"{name}: помилка даних")
        continue

    if temperature < 5:
        temp_status = "надто холодно"
    elif temperature > 25:
        temp_status = "надто жарко"
    else:
        temp_status = "норма"

    if category == "antibiotic":
        catg_status = "рецептурний препарат"
    elif category == "vitamin":
        catg_status = "вільний продаж"
    elif category == "vaccine":
        catg_status = "потребує спецзберігання"
    else:
        catg_status = "невідома категорія"


    print(f"{name}: {catg_status}, {temp_status}")


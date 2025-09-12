clients = [
    {"name": "Tom", "amount": 50, "status": "clean"},
    {"name": "Igor", "amount": 50, "status": "suspicious"},
    {"name": "Anna", "amount": 50, "status": "fraud"},
    {"name": "Kate", "amount": 50, "status": "clean"},
    {"name": "Vlad", "amount": 50, "status": "suspicious"},
    {"name": "Lesyk", "amount": 50, "status": "fraud"}
]

results = []

for client in clients:
    name = client["name"]
    amount = client["amount"]
    status = client["status"]

    if type(amount) not in (int, float):
        print(f"{name}: фальшиві дані")
        continue

    if amount < 100:
        category = "дрібнота"
    elif amount < 1000:
        category = "середнячок"
    else:
        category = "великий клієнт"

    if status == "clean":
        decision = "працювати без питань"
    elif status == "suspicious":
        decision = "перевірити документи"
    elif status == "fraud":
        decision = "чорний список"
    else:
        decision = "невідомий статус"

    results.append((name, category, decision))

for r in results:
    print(r)


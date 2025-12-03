import csv
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "inventory.csv")
FIELDS = ["id", "name", "category", "quantity", "price", "location", "created_at"]


def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()


def read_items():
    ensure_data_file()
    items = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    return items


def write_items(items):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(items)


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(read_items())


@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    if not data:
        return {"error": "Invalid JSON"}, 400

    items = read_items()
    new_id = str(max([int(i["id"]) for i in items], default=0) + 1)

    item = {
        "id": new_id,
        "name": data["name"],
        "category": data["category"],
        "quantity": str(int(data["quantity"])),
        "price": str(float(data["price"])),
        "location": data["location"],
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    items.append(item)
    write_items(items)

    return item, 201


@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    items = read_items()

    for item in items:
        if item["id"] == item_id:
            for key in ["name", "category", "quantity", "price", "location"]:
                if key in data:
                    item[key] = str(data[key])
            write_items(items)
            return item

    return {"error": "Not found"}, 404


@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    items = read_items()
    new_items = [i for i in items if i["id"] != item_id]

    if len(new_items) == len(items):
        return {"error": "Not found"}, 404

    write_items(new_items)
    return "", 204


@app.route("/export")
def export_csv():
    ensure_data_file()
    return send_file(CSV_PATH, as_attachment=True)


if __name__ == "__main__":
    ensure_data_file()
    app.run(host="127.0.0.1", port=8000, debug=True)

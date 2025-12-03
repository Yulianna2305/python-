import csv
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "inventory.csv")
FIELDNAMES = ["id", "name", "category", "quantity", "price", "location", "created_at"]


def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
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
    ensure_data_file()
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def validate_item_payload(data, partial=False):
    required = ["name", "category", "quantity", "price", "location"]

    if not isinstance(data, dict):
        return False, "JSON body must be an object"

    if not partial:
        missing = [f for f in required if f not in data]
        if missing:
            return False, f"Missing fields: {', '.join(missing)}"

    if "name" in data and not isinstance(data["name"], str):
        return False, "Field 'name' must be string"
    if "category" in data and not isinstance(data["category"], str):
        return False, "Field 'category' must be string"
    if "location" in data and not isinstance(data["location"], str):
        return False, "Field 'location' must be string"

    if "quantity" in data:
        try:
            q = int(data["quantity"])
            if q < 0:
                return False, "Field 'quantity' must be non-negative integer"
        except (ValueError, TypeError):
            return False, "Field 'quantity' must be integer"

    if "price" in data:
        try:
            float(data["price"])
        except (ValueError, TypeError):
            return False, "Field 'price' must be number"

    return True, None


def generate_new_id(items):
    max_id = 0
    for item in items:
        try:
            i = int(item["id"])
            if i > max_id:
                max_id = i
        except (ValueError, TypeError):
            continue
    return str(max_id + 1)


@app.route("/items", methods=["GET"])
def get_items():
    items = read_items()
    return jsonify(items)


@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    is_valid, error = validate_item_payload(data, partial=False)
    if not is_valid:
        return jsonify({"error": error}), 400

    items = read_items()
    new_id = generate_new_id(items)

    item = {
        "id": new_id,
        "name": data["name"],
        "category": data["category"],
        "quantity": str(int(data["quantity"])),
        "price": str(float(data["price"])),
        "location": data["location"],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    items.append(item)
    write_items(items)
    return jsonify(item), 201


@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    is_valid, error = validate_item_payload(data, partial=True)
    if not is_valid:
        return jsonify({"error": error}), 400

    items = read_items()
    for item in items:
        if item["id"] == item_id:
            if "name" in data:
                item["name"] = data["name"]
            if "category" in data:
                item["category"] = data["category"]
            if "quantity" in data:
                item["quantity"] = str(int(data["quantity"]))
            if "price" in data:
                item["price"] = str(float(data["price"]))
            if "location" in data:
                item["location"] = data["location"]
            write_items(items)
            return jsonify(item)

    return jsonify({"error": "Item not found"}), 404


@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    items = read_items()
    new_items = [i for i in items if i["id"] != item_id]
    if len(new_items) == len(items):
        return jsonify({"error": "Item not found"}), 404
    write_items(new_items)
    return "", 204


@app.route("/export", methods=["GET"])
def export_csv():
    ensure_data_file()
    return send_file(
        CSV_PATH,
        mimetype="text/csv",
        as_attachment=True,
        download_name="inventory.csv",
    )


if __name__ == "__main__":
    ensure_data_file()
    app.run(host="127.0.0.1", port=8000, debug=True)
